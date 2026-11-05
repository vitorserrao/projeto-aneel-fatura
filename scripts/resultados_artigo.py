"""Gera os resultados do artigo XXI ERIAC (tabelas + figuras) de forma reprodutível.

Casos do artigo (decisão de 04/11/2026):
  1. CEMIG-D, UC CEMIG-2 (A4 Verde, Poder Público), histórico jan–dez/2023
     — comparação Verde × Azul, demanda contratada ótima e E-PI.
  2. Copel, UC COPEL-1 (A4 Verde, comercial), histórico mai/2022–abr/2023
     — comparação Verde × Azul × Optante B (inelegível: art. 292) e E-PI.
  3. Equatorial Pará, UC EQT-TUCURUI-NUCLEO (B-Optante), 12/2024
     — validação do faturamento real de um Optante B.

Parte A (sem banco): validação "camada 1" das faturas reais dos três casos
(tarifas líquidas impressas na própria fatura).
Parte B (precisa do PostgreSQL com a base ANEEL): planejamento anual
(contrato atual × demanda otimizada) e E-PI com as tarifas vigentes em cada mês.

Uso:
    python scripts/resultados_artigo.py            # A + B
    python scripts/resultados_artigo.py --so-validacao
Saída: docs/artigo/resultados/ (CSV, Markdown, JSON e PNG).
Figuras exigem matplotlib (pip install matplotlib).
"""
from __future__ import annotations

import csv
import json
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from core.models import Consumidor  # noqa: E402
from core.motor_calculo import (  # noqa: E402
    calcular_fatura,
    elegivel_optante_b,
    motivo_indisponibilidade,
)
from core.tarifas import ParcelaTarifaria  # noqa: E402

CASOS = RAIZ / "docs/validacao_faturas_reais/casos"
SAIDA = RAIZ / "docs/artigo/resultados"

TOLERANCIA_LINHA = 0.05
TOLERANCIA_TOTAL = 1.00

# ---------------------------------------------------------------------------
# Históricos (grandezas FATURADAS, que já incluem perdas de transformação —
# premissa D2). Fonte: quadro "Histórico de Consumo" de cada fatura.
# data_referencia = dia 15 do mês de consumo (seleciona a vigência tarifária).
# ---------------------------------------------------------------------------
CEMIG_2023 = [
    # (mês de consumo, d_ponta kW, d_fora kW, e_ponta kWh, e_fora kWh)
    ("2023-01-15", 95, 98, 5250, 44100),
    ("2023-02-15", 151, 165, 6300, 46550),
    ("2023-03-15", 203, 207, 11200, 68950),
    ("2023-04-15", 189, 189, 8750, 59500),
    ("2023-05-15", 179, 168, 9800, 59850),
    ("2023-06-15", 168, 151, 9100, 57050),
    ("2023-07-15", 154, 140, 7000, 51100),
    ("2023-08-15", 189, 179, 9800, 63000),
    ("2023-09-15", 217, 238, 9800, 64400),
    ("2023-10-15", 203, 214, 10150, 64750),
    ("2023-11-15", 210, 231, 9800, 68250),
    ("2023-12-15", 193, 200, 7000, 54950),
]
# Fatura Copel: o mês de faturamento N corresponde ao consumo do mês N−1
# (ex.: fatura 04/2023 = leituras 28/02 a 31/03/2023 → referência 2023-03-15).
COPEL_2022_2023 = [
    ("2022-04-15", 1.37, 206.44, 12, 6914),    # fatura 05/2022
    ("2022-05-15", 7.97, 208.11, 25, 10600),   # 06/2022
    ("2022-06-15", 0.78, 207.13, 15, 2258),    # 07/2022
    ("2022-07-15", 0.39, 210.47, 14, 7463),    # 08/2022
    ("2022-08-15", 0.59, 206.44, 16, 10289),   # 09/2022
    ("2022-09-15", 0.88, 203.39, 16, 12832),   # 10/2022
    ("2022-10-15", 1.08, 193.25, 14, 9336),    # 11/2022
    ("2022-11-15", 0.78, 191.68, 16, 6903),    # 12/2022
    ("2022-12-15", 6.69, 168.16, 27, 6616),    # 01/2023
    ("2023-01-15", 4.82, 156.55, 49, 6846),    # 02/2023
    ("2023-02-15", 6.78, 139.82, 34, 7518),    # 03/2023
    ("2023-03-15", 6.88, 150.65, 55, 9094),    # 04/2023
]

CASOS_ARTIGO = [
    {
        "id": "cemig",
        "titulo": "CEMIG-D · UC CEMIG-2 · A4 Verde · jan–dez/2023",
        "validacao": "cemig_bh_cii112_2023_12.json",
        "flags": {"demanda_isenta_icms": True, "tributar_reativos": True},
        "perfil": dict(distribuidora="CEMIG-D", subgrupo="A4", classe="Não se aplica",
                       detalhe="Não se aplica", atividade="Comercial ou Industrial",
                       tipo_ligacao="Trifásico", potencia_transformadores_kva=0.0),
        "historico": CEMIG_2023,
        "tributos": dict(pis=0.0078, cofins=0.0361, icms=0.18),
        "dc_atual": dict(verde=400.0, azul_ponta=400.0, azul_fora=400.0),
        "cip_mensal": 40.45,
    },
    {
        "id": "copel",
        "titulo": "Copel · UC COPEL-1 · A4 Verde · mai/2022–abr/2023",
        "validacao": "copel_2023_04.json",
        "flags": {"demanda_isenta_icms": True, "tributar_reativos": False},
        "perfil": dict(distribuidora="COPEL-DIS", subgrupo="A4", classe="Não se aplica",
                       detalhe="Não se aplica", atividade="Comercial ou Industrial",
                       tipo_ligacao="Trifásico",
                       # Potência não impressa na fatura; a demanda medida (até
                       # 210 kW) implica transformação > 112,5 kVA (art. 292).
                       potencia_transformadores_kva=225.0),
        "historico": COPEL_2022_2023,
        "tributos": dict(pis=0.0095, cofins=0.0438, icms=0.18),
        "dc_atual": dict(verde=260.0, azul_ponta=260.0, azul_fora=260.0),
        "cip_mensal": 115.01,
    },
]
CASO_OPTANTE = {
    "id": "tucurui_nucleo",
    "titulo": "Equatorial · UC EQT-TUCURUI-NUCLEO · B-Optante · 12/2024",
    "validacao": "equatorial_tucurui_nucleo_2024_12.json",
    "flags": {"demanda_isenta_icms": False, "tributar_reativos": True},
}


# ---------------------------------------------------------------------------
# Parte A — validação camada 1
# ---------------------------------------------------------------------------
def _parcelas_fatura(caso: dict) -> list[ParcelaTarifaria]:
    parcelas = []
    for t in caso["tarifas_liquidas"]:
        if t["componente"] == "REATIVO":
            continue
        unidade, valor = t["unidade"], t["valor"]
        if unidade == "R$/kWh":
            unidade, valor = "R$/MWh", valor * 1000
        parcelas.append(ParcelaTarifaria(t["componente"], t["grandeza"], t["posto"], unidade, valor))
    return parcelas


def _consumidor_fatura(caso: dict) -> Consumidor:
    p = caso["perfil"]
    campos = {k: v for k, v in p.items() if k not in ("data_referencia", "demanda_isenta_icms_kw")}
    return Consumidor(
        distribuidora=caso["meta"]["distribuidora"], subgrupo=caso["meta"]["subgrupo"],
        classe="Não se aplica", subclasse="Não se aplica", detalhe="Não se aplica",
        data_referencia=date.fromisoformat(p["data_referencia"]), **campos,
    )


def _grupo(descricao: str) -> str:
    """Agrupa linhas (fatura ou motor) em itens comparáveis."""
    d = descricao.lower()
    if "isenta" in d or "s/ icms" in d:
        return "Demanda isenta de ICMS"
    if "reativ" in d or "reat" in d:
        return "Reativo excedente"
    if "bandeira" in d:
        return "Adicional de bandeira"
    if "ilum" in d or "cip" in d or "cosip" in d or "outros valores" in d:
        return "CIP/COSIP"
    if "demanda" in d:
        return "Demanda"
    ponta = ("ponta" in d or " hp" in d or d.endswith("hp")) and not any(
        x in d for x in ("fora", "f ponta", "f. ponta", "hfp"))
    if "consumo (kwh)" in d:
        return "Energia (tarifa única B)"
    if " te " in f" {d} " or "te energia" in d:
        return "TE ponta" if ponta else "TE fora ponta"
    if "usd" in d or "tusd" in d:
        return "TUSD ponta" if ponta else "TUSD fora ponta"
    if "energia ativa" in d:
        return "Energia ponta (TE+TUSD)" if ponta else "Energia fora ponta (TE+TUSD)"
    return descricao


def validar(caso_cfg: dict) -> dict:
    caso = json.loads((CASOS / caso_cfg["validacao"]).read_text(encoding="utf-8"))
    trib = caso["tributos"]
    rt = next((t["valor"] for t in caso["tarifas_liquidas"] if t["componente"] == "REATIVO"), None)
    fatura = calcular_fatura(
        _consumidor_fatura(caso), caso["meta"]["modalidade"], _parcelas_fatura(caso),
        demanda_unica=caso["meta"]["modalidade"] == "Verde",
        aplicar_tributos=True, pis=trib["pis"], cofins=trib["cofins"], icms=trib["icms"],
        tipo_icms=trib["tipo_icms"], reativos_direto=rt is not None,
        tarifa_reativo_energia_r_kvarh=rt, arredondar_centavos=True,
        demanda_isenta_icms=caso_cfg["flags"]["demanda_isenta_icms"],
        demanda_isenta_icms_kw=caso["perfil"].get("demanda_isenta_icms_kw"),
        tributar_reativos=caso_cfg["flags"]["tributar_reativos"],
    )
    # CEMIG imprime TE+TUSD numa linha só por posto → agrupar o motor igual.
    juntar_energia = any("energia ativa" in e["descricao"].lower() for e in caso["linhas_esperadas"])
    motor: dict[str, float] = {}
    for l in fatura.linhas:
        g = _grupo(l.descricao)
        if juntar_energia and g.startswith(("TE ", "TUSD ")):
            g = "Energia ponta (TE+TUSD)" if "fora" not in g else "Energia fora ponta (TE+TUSD)"
        if caso["meta"]["modalidade"] == "Optante B" and g.startswith("TUSD"):
            g = "Energia (tarifa única B)"
        motor[g] = round(motor.get(g, 0.0) + l.custo, 2)
    real: dict[str, float] = {}
    for e in caso["linhas_esperadas"]:
        g = _grupo(e["descricao"])
        real[g] = round(real.get(g, 0.0) + e["valor"], 2)
    linhas = []
    for g in real:
        m = motor.get(g)
        linhas.append({"item": g, "fatura": real[g], "motor": m,
                       "delta": None if m is None else round(m - real[g], 2)})
    soma_real = round(sum(real.values()), 2)
    soma_motor = round(sum(motor.get(g, 0.0) for g in real), 2)
    return {
        "caso": caso_cfg["titulo"], "linhas": linhas,
        "soma_tecnica_fatura": soma_real, "soma_tecnica_motor": soma_motor,
        "delta_total": round(soma_motor - soma_real, 2),
        "max_delta_linha": max(abs(l["delta"] or 0) for l in linhas),
        "aprovado": all(l["delta"] is not None and abs(l["delta"]) <= TOLERANCIA_LINHA for l in linhas)
        and abs(soma_motor - soma_real) <= TOLERANCIA_TOTAL,
        "total_fatura": caso["meta"]["total_fatura"], "notas": caso.get("notas", []),
    }


def parte_a() -> list[dict]:
    resultados = [validar(c) for c in CASOS_ARTIGO + [CASO_OPTANTE]]
    with open(SAIDA / "tabela_validacao.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["caso", "item", "fatura_rs", "motor_rs", "delta_rs"])
        for r in resultados:
            for l in r["linhas"]:
                w.writerow([r["caso"], l["item"], l["fatura"], l["motor"], l["delta"]])
    md = ["# Validação com faturas reais (camada 1)\n",
          f"Critério: |Δ| ≤ R$ {TOLERANCIA_LINHA:.2f} por item e ≤ R$ {TOLERANCIA_TOTAL:.2f} no total técnico.\n"]
    for r in resultados:
        md.append(f"\n## {r['caso']}\n\n| Item | Fatura (R$) | Motor (R$) | Δ (R$) |\n|---|---:|---:|---:|")
        for l in r["linhas"]:
            md.append(f"| {l['item']} | {l['fatura']:,.2f} | {l['motor'] if l['motor'] is not None else '—'} | {l['delta']} |")
        md.append(f"| **Soma técnica** | **{r['soma_tecnica_fatura']:,.2f}** | **{r['soma_tecnica_motor']:,.2f}** | **{r['delta_total']:+.2f}** |")
        md.append(f"\nStatus: {'aprovado' if r['aprovado'] else 'REPROVADO'} · total impresso na fatura R$ {r['total_fatura']:,.2f} (inclui itens financeiros fora do motor).")
    (SAIDA / "tabela_validacao.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    for r in resultados:
        print(f"[A] {r['caso']}: Δ total {r['delta_total']:+.2f}, máx/linha {r['max_delta_linha']:.2f} → {'OK' if r['aprovado'] else 'FALHOU'}")
    return resultados


# ---------------------------------------------------------------------------
# Parte B — planejamento anual + E-PI (banco ANEEL)
# ---------------------------------------------------------------------------
def _meses(historico) -> list[dict]:
    return [dict(data_referencia=d, d_med_ponta=float(dp), d_med_fora_ponta=float(df),
                 e_ponta_kwh=float(ep), e_fora_ponta_kwh=float(ef))
            for d, dp, df, ep, ef in historico]


def parte_b() -> dict:
    from infra.database import create_session_factory
    from infra.repositories.tarifa_repository import TarifaRepository
    from services.calculo_service import CalculoService
    from services.epi_service import EPIService
    from services.otimizacao_service import OtimizacaoService
    from services.planejamento_service import PlanejamentoService

    repo = TarifaRepository(create_session_factory())
    calculo = CalculoService(repo)
    servico = PlanejamentoService(calculo, EPIService(repo, OtimizacaoService(calculo)))

    saida: dict = {}
    for cfg in CASOS_ARTIGO:
        meses = _meses(cfg["historico"])
        perfil = Consumidor(data_referencia=date.fromisoformat(meses[-1]["data_referencia"]),
                            **cfg["perfil"])
        elegivel_b = elegivel_optante_b(perfil)
        comum = dict(**cfg["tributos"], tipo_icms="fora",
                     demanda_isenta_icms=cfg["flags"]["demanda_isenta_icms"],
                     tributar_reativos=cfg["flags"]["tributar_reativos"],
                     modalidade_atual="Verde", dc_atual_verde=cfg["dc_atual"]["verde"],
                     dc_atual_azul_ponta=cfg["dc_atual"]["azul_ponta"],
                     dc_atual_azul_fora=cfg["dc_atual"]["azul_fora"], k=0.03)
        plano, pi = servico.comparar(perfil, meses, **comum)
        _, pi_av = servico.comparar(perfil, meses, **comum, opex_mensal=1000.0,
                                    capex=20000.0, horizonte_meses=60)

        # Séries mensais por cenário (mesmo motor do planejamento).
        series = {}
        for mod in plano.modalidades:
            if mod.modalidade not in ("Verde", "Azul"):
                continue
            parc = [servico._parcelas(perfil, m, mod.modalidade) for m in meses]
            for cen, dc in (("atual", mod.dc_atual), ("otimizada", mod.dc_otima)):
                valores = []
                for i, m in enumerate(meses):
                    kw = (dict(dc_unica=dc, demanda_unica=True) if mod.modalidade == "Verde"
                          else dict(dc_unica=None, dc_ponta=dc[0], dc_fora=dc[1], demanda_unica=False))
                    f = servico._motor_mes(perfil, m, mod.modalidade, parc[i],
                                           pis=comum["pis"], cofins=comum["cofins"], icms=comum["icms"],
                                           tipo_icms="fora",
                                           demanda_isenta_icms=comum["demanda_isenta_icms"],
                                           tributar_reativos=comum["tributar_reativos"], **kw)
                    valores.append(round(f.custo_total, 2))
                series[f"{mod.modalidade} · {cen}"] = valores

        saida[cfg["id"]] = {
            "titulo": cfg["titulo"],
            "optante_b": {"elegivel": elegivel_b,
                          "motivo": motivo_indisponibilidade("Optante B", perfil)},
            "melhor_contrato_atual": plano.melhor_contrato_atual,
            "melhor_demanda_otimizada": plano.melhor_demanda_otimizada,
            "ganho": {"total": plano.ganho.ganho_total, "demanda": plano.ganho.ganho_demanda,
                      "modalidade": plano.ganho.ganho_modalidade},
            "modalidades": [
                {"modalidade": m.modalidade, "custo_contrato_atual": round(m.custo_contrato_atual, 2),
                 "custo_demanda_otimizada": round(m.custo_demanda_otimizada, 2),
                 "dc_atual": m.dc_atual, "dc_otima": m.dc_otima,
                 "epi_simplificado": (pi.get(m.modalidade) or {}).get("anual"),
                 "epi_com_custos": (pi_av.get(m.modalidade) or {}).get("anual")}
                for m in plano.modalidades],
            "series_mensais": series,
            "meses": [m["data_referencia"][:7] for m in meses],
            "demanda_medida": [max(m["d_med_ponta"], m["d_med_fora_ponta"]) for m in meses],
            "avisos": list(plano.avisos),
        }
        print(f"[B] {cfg['titulo']}: melhor otimizado = {plano.melhor_demanda_otimizada}, "
              f"ganho total R$ {plano.ganho.ganho_total:,.2f}")
    (SAIDA / "planejamento.json").write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    _tabela_planejamento(saida)
    _figuras(saida)
    return saida


def _tabela_planejamento(saida: dict) -> None:
    md = ["# Planejamento anual e E-PI\n"]
    for c in saida.values():
        md.append(f"\n## {c['titulo']}\n\n| Modalidade | DC atual (kW) | Custo atual (R$/ano) | DC ótima (kW) | Custo otimizado (R$/ano) | E-PI simplificado (R$/MWh) | E-PI c/ OPEX+CAPEX (R$/MWh) |\n|---|---:|---:|---:|---:|---:|---:|")
        for m in c["modalidades"]:
            md.append(f"| {m['modalidade']} | {m['dc_atual']} | {m['custo_contrato_atual']:,.2f} | {m['dc_otima']} | "
                      f"{m['custo_demanda_otimizada']:,.2f} | {m['epi_simplificado'] or '—'} | {m['epi_com_custos'] or '—'} |")
        g = c["ganho"]
        md.append(f"\nGanho total R$ {g['total']:,.2f} = ajuste de demanda R$ {g['demanda']:,.2f} + troca de modalidade R$ {g['modalidade']:,.2f}.")
        ob = c["optante_b"]
        md.append(f"Optante B: {'elegível' if ob['elegivel'] else 'inelegível — ' + str(ob['motivo'])}.")
    (SAIDA / "tabela_planejamento.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def _figuras(saida: dict) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib ausente: figuras não geradas (pip install matplotlib)")
        return
    cor = {"Verde": "#1F8A4C", "Azul": "#2B59C3"}
    for cid, c in saida.items():
        # Fig. A — custo anual por modalidade e cenário
        fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=200)
        mods = [m for m in c["modalidades"] if m["modalidade"] in cor]
        x = range(len(mods))
        ax.bar([i - 0.18 for i in x], [m["custo_contrato_atual"] / 1000 for m in mods], 0.34,
               color=[cor[m["modalidade"]] for m in mods], alpha=0.45, label="Contrato atual")
        ax.bar([i + 0.18 for i in x], [m["custo_demanda_otimizada"] / 1000 for m in mods], 0.34,
               color=[cor[m["modalidade"]] for m in mods], label="Demanda otimizada")
        for i, m in enumerate(mods):
            ax.text(i - 0.18, m["custo_contrato_atual"] / 1000, f"{m['custo_contrato_atual']/1000:,.1f}", ha="center", va="bottom", fontsize=7)
            ax.text(i + 0.18, m["custo_demanda_otimizada"] / 1000, f"{m['custo_demanda_otimizada']/1000:,.1f}", ha="center", va="bottom", fontsize=7)
        ax.set_xticks(list(x), [m["modalidade"] for m in mods])
        ax.set_ylabel("Custo anual (mil R$)")
        ax.legend(frameon=False, fontsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout(); fig.savefig(SAIDA / f"fig_custo_anual_{cid}.png"); plt.close(fig)

        # Fig. B — custo mensal por modalidade (demanda otimizada)
        fig, ax = plt.subplots(figsize=(6.5, 3.0), dpi=200)
        for nome, serie in c["series_mensais"].items():
            mod, cen = nome.split(" · ")
            ax.plot(c["meses"], [v / 1000 for v in serie], color=cor[mod],
                    linestyle="-" if cen == "otimizada" else "--", linewidth=1.6, marker="o", markersize=3,
                    label=f"{mod} ({cen})")
        ax.set_ylabel("Fatura mensal (mil R$)")
        ax.tick_params(axis="x", rotation=45, labelsize=7)
        ax.legend(frameon=False, fontsize=7, ncol=2)
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout(); fig.savefig(SAIDA / f"fig_custo_mensal_{cid}.png"); plt.close(fig)

        # Fig. C — demanda medida × contratada atual × ótima (Verde)
        verde = next(m for m in c["modalidades"] if m["modalidade"] == "Verde")
        fig, ax = plt.subplots(figsize=(6.5, 2.8), dpi=200)
        dm = c["demanda_medida"]; dc_ot = verde["dc_otima"]
        ax.bar(c["meses"], dm, color=["#C2410C" if d > 1.05 * dc_ot else "#5E7F93" for d in dm])
        ax.axhline(verde["dc_atual"], color="#13232E", linestyle="--", linewidth=1.2, label=f"Contratada atual ({verde['dc_atual']:.0f} kW)")
        ax.axhline(dc_ot, color="#D99A00", linewidth=1.6, label=f"Ótima ({dc_ot:.0f} kW)")
        ax.axhline(1.05 * dc_ot, color="#D99A00", linestyle=":", linewidth=1.0, label="Tolerância 105%")
        ax.set_ylabel("Demanda (kW)")
        ax.tick_params(axis="x", rotation=45, labelsize=7)
        ax.legend(frameon=False, fontsize=7)
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout(); fig.savefig(SAIDA / f"fig_demanda_{cid}.png"); plt.close(fig)
    print(f"figuras em {SAIDA.relative_to(RAIZ)}")


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    parte_a()
    if "--so-validacao" not in sys.argv:
        parte_b()


if __name__ == "__main__":
    main()
