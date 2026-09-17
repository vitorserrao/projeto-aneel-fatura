"""Consulta flexível às tabelas tarifárias do banco do projeto.

Uso (exemplos):

    # todas as tarifas TUSD de energia da Âmbar Amazonas A4 Azul em dez/2010
    .venv\\Scripts\\python.exe scripts\\consultar_banco.py ^
        --distribuidora "Âmbar Amazonas" --subgrupo A4 --modalidade Azul ^
        --componente TUSD --unidade MWh --data 2010-12-01

    # tudo que tem "ponta" no posto (seca/úmida/simples), para uma modalidade
    .venv\\Scripts\\python.exe scripts\\consultar_banco.py ^
        --distribuidora "Âmbar Amazonas" --subgrupo A4 --modalidade Azul ^
        --posto-contem ponta --data 2010-12-01

    # listar valores distintos de uma coluna (exploração)
    .venv\\Scripts\\python.exe scripts\\consultar_banco.py --distintos nom_posto_tarifario

    # bandeira tarifária de uma competência
    .venv\\Scripts\\python.exe scripts\\consultar_banco.py --bandeira 2025-06-01

Todos os filtros são opcionais e combináveis (AND). Sem ``--data``, não filtra
vigência (mostra todos os períodos).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from infra.database import create_session_factory

# Colunas normalizadas disponíveis para --distintos (evita SQL injection).
COLUNAS_DISTINTAS = {
    "sig_agente",
    "dsc_sub_grupo",
    "dsc_modalidade_tarifaria",
    "dsc_base_tarifaria",
    "dsc_classe",
    "dsc_sub_classe",
    "dsc_detalhe",
    "nom_posto_tarifario",
    "dsc_unidade_terciaria",
    "componente",
    "dsc_reh",
}


def _sql_filtros(args) -> tuple[str, dict]:
    where = []
    p = {}
    if args.distribuidora:
        where.append("d.sig_agente = :sig")
        p["sig"] = args.distribuidora
    if args.cnpj:
        where.append("d.num_cnpj = :cnpj")
        p["cnpj"] = args.cnpj
    if args.subgrupo:
        where.append("t.dsc_sub_grupo = :subgrupo")
        p["subgrupo"] = args.subgrupo
    if args.modalidade:
        where.append("t.dsc_modalidade_tarifaria = :modalidade")
        p["modalidade"] = args.modalidade
    if args.base:
        where.append("t.dsc_base_tarifaria = :base")
        p["base"] = args.base
    if args.classe:
        where.append("t.dsc_classe = :classe")
        p["classe"] = args.classe
    if args.subclasse:
        where.append("t.dsc_sub_classe = :subclasse")
        p["subclasse"] = args.subclasse
    if args.detalhe:
        where.append("t.dsc_detalhe = :detalhe")
        p["detalhe"] = args.detalhe
    if args.componente:
        where.append("t.componente = :componente")
        p["componente"] = args.componente.upper()
    if args.unidade:
        where.append("t.dsc_unidade_terciaria = :unidade")
        p["unidade"] = args.unidade
    if args.posto:
        where.append("t.nom_posto_tarifario = :posto")
        p["posto"] = args.posto
    if args.posto_contem:
        # case-insensitive; sem acento-sensibilidade exata (usa ILIKE)
        where.append("t.nom_posto_tarifario ILIKE :posto_like")
        p["posto_like"] = f"%{args.posto_contem}%"
    if args.reh:
        where.append("t.dsc_reh ILIKE :reh")
        p["reh"] = f"%{args.reh}%"
    if args.data:
        where.append("t.dat_inicio_vigencia <= :data AND t.dat_fim_vigencia >= :data")
        p["data"] = args.data
    clausula = (" WHERE " + " AND ".join(where)) if where else ""
    return clausula, p


def consultar(args) -> int:
    clausula, p = _sql_filtros(args)
    sql = f"""
        SELECT d.sig_agente, t.dsc_reh, t.dsc_sub_grupo,
               t.dsc_modalidade_tarifaria, t.dsc_base_tarifaria,
               t.componente, t.nom_posto_tarifario, t.dsc_unidade_terciaria,
               t.valor, t.dat_inicio_vigencia, t.dat_fim_vigencia,
               t.dsc_classe, t.dsc_sub_classe, t.dsc_detalhe
        FROM tarifa_aplicacao_componente t
        JOIN distribuidora d ON d.id = t.distribuidora_id
        {clausula}
        ORDER BY t.nom_posto_tarifario, t.componente, t.dat_inicio_vigencia
        LIMIT :lim
    """
    p["lim"] = args.limit
    with create_session_factory()() as sess:
        rows = sess.execute(text(sql), p).all()

    if not rows:
        print("(nenhum resultado)")
        return 0

    print(f"{'componente':5} {'posto':22} {'unid':5} {'valor':>10} "
          f"{'subgrp':5} {'modal':12} {'base':18} {'vigencia'}")
    print("-" * 96)
    for r in rows:
        (sig, reh, sub, mod, base, comp, posto, unid, valor,
         ini, fim, classe, subclasse, detalhe) = r
        print(f"{comp:5} {posto:22} {unid:5} {float(valor):>10.2f} "
              f"{sub:5} {mod:12} {base:18} {ini}..{fim}")

    # resumo se o filtro não pediu componente específico e há TE+TUSD
    print("-" * 96)
    print(f"{len(rows)} linha(s). Distribuidora(s): "
          f"{sorted({r[0] for r in rows})}")
    if args.data:
        print(f"(vigência filtrada na data {args.data})")
    return 0


def listar_distintos(coluna: str) -> int:
    if coluna not in COLUNAS_DISTINTAS:
        print(f"coluna inválida. Opções: {sorted(COLUNAS_DISTINTAS)}")
        return 2
    if coluna == "sig_agente":
        sql = "SELECT DISTINCT sig_agente FROM distribuidora ORDER BY 1"
    else:
        sql = (
            f"SELECT DISTINCT {coluna} FROM tarifa_aplicacao_componente "
            f"WHERE {coluna} IS NOT NULL ORDER BY 1"
        )
    with create_session_factory()() as sess:
        vals = [r[0] for r in sess.execute(text(sql)).all()]
    print(f"{coluna} ({len(vals)}):")
    for v in vals:
        print("  -", v)
    return 0


def consultar_bandeira(competencia: str) -> int:
    sql = (
        "SELECT competencia, bandeira, valor_mwh, valor_kwh, fonte "
        "FROM bandeira_tarifaria WHERE competencia = :c"
    )
    with create_session_factory()() as sess:
        rows = sess.execute(text(sql), {"c": competencia}).all()
    if not rows:
        print(f"(sem bandeira cadastrada para {competencia} — antes de jan/2015 "
              "não há bandeira)")
        return 0
    for r in rows:
        print(f"competencia={r[0]} bandeira={r[1]} R$/MWh={r[2]} "
              f"R$/kWh={r[3]}\n  fonte: {r[4]}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Consulta ao banco tarifário.")
    ap.add_argument("--distribuidora", help="sig_agente exato (ex.: 'Âmbar Amazonas')")
    ap.add_argument("--cnpj", help="num_cnpj exato")
    ap.add_argument("--subgrupo", help="ex.: A4, A3, B2")
    ap.add_argument("--modalidade", help="ex.: Azul, Verde, Convencional")
    ap.add_argument("--base", help="ex.: 'Tarifa de Aplicação'")
    ap.add_argument("--classe")
    ap.add_argument("--subclasse")
    ap.add_argument("--detalhe", help="ex.: 'Não se aplica', APE, SCEE")
    ap.add_argument("--componente", choices=["TE", "TUSD", "te", "tusd"])
    ap.add_argument("--unidade", help="ex.: MWh, kW, kWh")
    ap.add_argument("--posto", help="posto exato (ex.: 'Ponta úmida')")
    ap.add_argument("--posto-contem", dest="posto_contem",
                    help="filtra posto por substring (ex.: ponta)")
    ap.add_argument("--reh", help="trecho da REH (ex.: 1.077)")
    ap.add_argument("--data", help="vigência na data AAAA-MM-DD")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--distintos", metavar="COLUNA",
                    help=f"lista valores distintos de: {sorted(COLUNAS_DISTINTAS)}")
    ap.add_argument("--bandeira", metavar="AAAA-MM-DD",
                    help="consulta bandeira tarifária da competência")
    args = ap.parse_args(argv)

    if args.distintos:
        return listar_distintos(args.distintos)
    if args.bandeira:
        return consultar_bandeira(args.bandeira)
    return consultar(args)


if __name__ == "__main__":
    raise SystemExit(main())
