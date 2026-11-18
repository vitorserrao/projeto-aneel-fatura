"""Carrega as bandeiras tarifárias direto dos conjuntos de dados abertos da ANEEL.

Dois arquivos, dois destinos — o tipo é detectado pelo cabeçalho:

1. **Bandeira acionada por competência** (``DatCompetencia`` /
   ``NomBandeiraAcionada`` / ``VlrAdicionalBandeira``) → ``bandeira_tarifaria``:
   uma linha por mês, com a bandeira que vigorou e o adicional em R$/MWh.
   ``valor_kwh`` = valor_mwh / 1000; vigência = mês civil da competência.

2. **Histórico normativo de valores** (``DscResolucao`` / ``DatVigencia`` /
   ``NomBandeiraAcionada`` / ``VlrAdicionalBandeiraRSMWh``) → ``bandeira_valor``:
   uma linha por (bandeira, vigência), com a resolução na coluna ``fonte``.

Formato: CSV separado por ``;``, campos entre aspas, decimal com vírgula
(pt-BR). Idempotente nas duas tabelas (ON CONFLICT atualiza).

Uso:
    python scripts/cargar_bandeiras_aneel.py --arquivo <csv> [--arquivo <csv>]
    python scripts/cargar_bandeiras_aneel.py --arquivo <csv> --dry-run

Fonte: ANEEL — Dados Abertos ("Bandeira Tarifária"). Guarde os CSV em
``data/`` ou aponte o caminho na linha de comando; nada é inventado aqui: o
script só transcreve o que está no arquivo.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from infra.database import create_session_factory

# Resolução/nome que identifica a origem no banco (rastreabilidade).
FONTE_ACIONADA = "ANEEL dados abertos - bandeira tarifaria acionada (CSV DatCompetencia)"
FONTE_VALORES = "ANEEL dados abertos - valores de bandeira (CSV DatVigencia)"


def _numero(txt: str) -> float:
    """'1.234,56' / '44,63' / ',00' (pt-BR) → float."""
    t = (txt or "").strip()
    if not t:
        return 0.0
    return float(t.replace(".", "").replace(",", "."))


def _fim_do_mes(dia: date) -> date:
    proximo = date(dia.year + (dia.month == 12), (dia.month % 12) + 1, 1)
    return proximo - timedelta(days=1)


def ler_csv(caminho: Path) -> tuple[str, list[dict]]:
    """Lê o CSV e devolve (tipo, linhas). tipo ∈ {'acionada', 'valores'}."""
    with caminho.open(encoding="utf-8-sig", newline="") as fh:
        leitor = csv.DictReader(fh, delimiter=";", quotechar='"')
        campos = set(leitor.fieldnames or [])
        linhas = list(leitor)

    if "DatCompetencia" in campos:
        tipo = "acionada"
    elif "DatVigencia" in campos:
        tipo = "valores"
    else:
        raise SystemExit(
            f"{caminho.name}: cabeçalho não reconhecido ({sorted(campos)}). "
            "Esperado DatCompetencia (bandeira acionada) ou DatVigencia (valores)."
        )
    return tipo, linhas


def preparar_acionadas(linhas: list[dict]) -> list[dict]:
    """CSV de bandeira acionada → linhas de ``bandeira_tarifaria``."""
    saida = []
    for l in linhas:
        competencia = date.fromisoformat(l["DatCompetencia"].strip())
        mwh = _numero(l["VlrAdicionalBandeira"])
        saida.append(
            {
                "competencia": competencia,
                "bandeira": l["NomBandeiraAcionada"].strip(),
                "valor_mwh": round(mwh, 6),
                "valor_kwh": round(mwh / 1000.0, 6),
                "vigencia_inicio": competencia.replace(day=1),
                "vigencia_fim": _fim_do_mes(competencia),
                "fonte": FONTE_ACIONADA,
            }
        )
    return sorted(saida, key=lambda r: r["competencia"])


def preparar_valores(linhas: list[dict]) -> list[dict]:
    """CSV de valores normativos → linhas de ``bandeira_valor``."""
    saida = []
    for l in linhas:
        vigencia = date.fromisoformat(l["DatVigencia"].strip())
        mwh = _numero(l["VlrAdicionalBandeiraRSMWh"])
        resolucao = (l.get("DscResolucao") or "").strip()
        saida.append(
            {
                "bandeira": l["NomBandeiraAcionada"].strip(),
                "vigencia_inicio": vigencia,
                "valor_mwh": round(mwh, 6),
                "valor_kwh": round(mwh / 1000.0, 6),
                "fonte": f"{FONTE_VALORES} - {resolucao}" if resolucao else FONTE_VALORES,
            }
        )
    return sorted(saida, key=lambda r: (r["bandeira"], r["vigencia_inicio"]))


SQL_ACIONADA = """
    INSERT INTO bandeira_tarifaria
        (competencia, bandeira, valor_mwh, valor_kwh, vigencia_inicio, vigencia_fim, fonte)
    VALUES
        (:competencia, :bandeira, :valor_mwh, :valor_kwh, :vigencia_inicio, :vigencia_fim, :fonte)
    ON CONFLICT (competencia) DO UPDATE SET
        bandeira = EXCLUDED.bandeira,
        valor_mwh = EXCLUDED.valor_mwh,
        valor_kwh = EXCLUDED.valor_kwh,
        vigencia_inicio = EXCLUDED.vigencia_inicio,
        vigencia_fim = EXCLUDED.vigencia_fim,
        fonte = EXCLUDED.fonte
"""

SQL_VALOR = """
    INSERT INTO bandeira_valor
        (bandeira, vigencia_inicio, valor_mwh, valor_kwh, fonte)
    VALUES
        (:bandeira, :vigencia_inicio, :valor_mwh, :valor_kwh, :fonte)
    ON CONFLICT (bandeira, vigencia_inicio) DO UPDATE SET
        valor_mwh = EXCLUDED.valor_mwh,
        valor_kwh = EXCLUDED.valor_kwh,
        fonte = EXCLUDED.fonte
"""


def _existentes(sess, tipo: str) -> dict:
    """Estado atual das linhas que os CSVs podem tocar (para o diff)."""
    if tipo == "acionada":
        sql = text("SELECT competencia, bandeira, valor_mwh FROM bandeira_tarifaria")
        return {(r[0],): (r[1], float(r[2])) for r in sess.execute(sql)}
    sql = text("SELECT bandeira, vigencia_inicio, valor_mwh FROM bandeira_valor")
    return {(r[0], r[1]): (r[0], float(r[2])) for r in sess.execute(sql)}


def comparar(tipo: str, linhas: list[dict], atuais: dict) -> tuple[list, list, list]:
    """(novas, alteradas, iguais) comparando com o banco."""
    novas, alteradas, iguais = [], [], []
    for r in linhas:
        chave = (r["competencia"],) if tipo == "acionada" else (r["bandeira"], r["vigencia_inicio"])
        if chave not in atuais:
            novas.append(r)
            continue
        _, mwh_atual = atuais[chave]
        bandeira_atual = atuais[chave][0]
        if tipo == "acionada":
            igual = bandeira_atual == r["bandeira"] and abs(mwh_atual - r["valor_mwh"]) < 1e-6
        else:
            igual = abs(mwh_atual - r["valor_mwh"]) < 1e-6
        (iguais if igual else alteradas).append(r)
    return novas, alteradas, iguais


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--arquivo", action="append", required=True, help="CSV da ANEEL (pode repetir)")
    ap.add_argument("--dry-run", action="store_true", help="só compara, não grava")
    args = ap.parse_args()

    total_gravado = 0
    with create_session_factory()() as sess:
        for caminho_txt in args.arquivo:
            caminho = Path(caminho_txt)
            if not caminho.exists():
                raise SystemExit(f"arquivo não encontrado: {caminho}")

            tipo, brutas = ler_csv(caminho)
            linhas = preparar_acionadas(brutas) if tipo == "acionada" else preparar_valores(brutas)
            atuais = _existentes(sess, tipo)
            novas, alteradas, iguais = comparar(tipo, linhas, atuais)

            destino = "bandeira_tarifaria" if tipo == "acionada" else "bandeira_valor"
            periodo = (
                f"{linhas[0]['competencia']} .. {linhas[-1]['competencia']}"
                if tipo == "acionada"
                else f"{linhas[0]['vigencia_inicio']} .. {linhas[-1]['vigencia_inicio']}"
            )
            bandeiras = sorted({r["bandeira"] for r in linhas})
            print(f"\n{caminho.name} -> {destino}")
            print(f"  linhas no arquivo: {len(linhas)} ({periodo})")
            print(f"  bandeiras: {', '.join(bandeiras)}")
            print(f"  novas: {len(novas)} | alteradas: {len(alteradas)} | iguais: {len(iguais)}")
            for r in alteradas[:10]:
                chave = r["competencia"] if tipo == "acionada" else r["vigencia_inicio"]
                antes = atuais[(chave,) if tipo == "acionada" else (r["bandeira"], chave)]
                print(f"    ! {chave} {r['bandeira']}: R$ {antes[1]:.2f} -> R$ {r['valor_mwh']:.2f}/MWh")

            if args.dry_run:
                continue

            sql = SQL_ACIONADA if tipo == "acionada" else SQL_VALOR
            for r in linhas:
                sess.execute(text(sql), r)
            sess.commit()
            total_gravado += len(linhas)
            print(f"  gravadas: {len(linhas)}")

    if args.dry_run:
        print("\n[dry-run] nada foi gravado.")
    else:
        print(f"\ntotal gravado: {total_gravado} linhas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
