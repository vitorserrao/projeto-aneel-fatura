"""Gera a planilha de apresentação: as 3 faturas reais simuladas.

Entradas copiadas de ``docs/validacao_faturas_reais/casos/*.json``; tarifas do
PostgreSQL (dataset ANEEL). Nada é digitado à mão aqui.

1. Copel — Grupo A (04/2023): Verde × Azul
2. CEMIG — BH CII_112 (12/2023): Verde × Azul
3. Equatorial — Tucuruí Núcleo (12/2024): Optante pelo Grupo B (art. 292)

Abas: Resumo, Entradas, Resultados, Fatura Copel, Fatura CEMIG,
Fatura Tucuruí, E-PI, Validação (10 casos reais item a item) e Premissas.

Uso: python scripts/gerar_planilha_apresentacao.py [--saida caminho.xlsx]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from fastapi.testclient import TestClient
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from api.main import app

client = TestClient(app)
CASOS_DIR = RAIZ / "docs/validacao_faturas_reais/casos"

CASOS = [
    {
        "id": "Copel — Grupo A",
        "curto": "Copel",
        "arquivo": "copel_2023_04.json",
        "modalidades": ["Verde", "Azul"],
        "nota": "unidade Verde; a Azul é simulada com a demanda única nos dois postos (premissa D6)",
    },
    {
        "id": "CEMIG — BH CII_112",
        "curto": "CEMIG",
        "arquivo": "cemig_bh_cii112_2023_12.json",
        "modalidades": ["Verde", "Azul"],
        "nota": "unidade Verde com 400 kW contratados e 200 kW medidos (parcela isenta de ICMS)",
    },
    {
        "id": "Equatorial — Tucuruí Núcleo",
        "curto": "Tucuruí",
        "arquivo": "equatorial_tucurui_nucleo_2024_12.json",
        "modalidades": ["Optante B"],
        "nota": "caso real de Optante pelo Grupo B (art. 292): tarifa única, sem demanda",
    },
]

TINTA, CINZA = "13232E", "F3F5F7"
LINHA = Side(style="thin", color="DCE3E8")
TITULO = Font(name="Calibri", size=14, bold=True, color=TINTA)
SECAO = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
CABECALHO = Font(name="Calibri", size=10, bold=True, color=TINTA)
CORPO = Font(name="Calibri", size=10)
NOTA = Font(name="Calibri", size=9, color="5B6B76")
NUM = "#,##0.00"
FUNDO_SECAO = PatternFill("solid", fgColor=TINTA)
FUNDO_CAB = PatternFill("solid", fgColor=CINZA)
FUNDO_DESTAQUE = PatternFill("solid", fgColor="EAF5EE")

TRIBUTA_REATIVO = {"CEMIG-D", "EQUATORIAL PA"}


# ---------------------------------------------------------------- API
def corpo_fatura(caso: dict) -> dict:
    p, meta = caso["perfil"], caso["meta"]
    corpo = {
        "distribuidora": meta["distribuidora"],
        "subgrupo": meta["subgrupo"],
        "classe": "Não se aplica",
        "subclasse": "Não se aplica",
        "detalhe": "Não se aplica",
        "data_referencia": p["data_referencia"],
        "consumo_ponta_kwh": p.get("consumo_ponta_kwh", 0.0),
        "consumo_fora_ponta_kwh": p.get("consumo_fora_ponta_kwh", 0.0),
        "demanda_medida_unica_kw": p.get("demanda_medida_unica_kw", 0.0),
        "demanda_contratada_unica_kw": p.get("demanda_contratada_unica_kw", 0.0),
        "reativo_energia_ponta_kvArh": p.get("reativo_energia_ponta_kvArh", 0.0),
        "reativo_energia_fora_ponta_kvArh": p.get("reativo_energia_fora_ponta_kvArh", 0.0),
        "bandeira_adicional_r_kwh": p.get("bandeira_adicional_r_kwh", 0.0),
        "cip_cosip_rs": p.get("cip_cosip_rs", 0.0),
        "outros_rs": p.get("outros_rs", 0.0),
        "atividade": "Comercial ou Industrial",
    }
    if p.get("potencia_transformadores_kva"):
        corpo["potencia_transformadores_kva"] = p["potencia_transformadores_kva"]
    return corpo


def params_fatura(caso: dict, modalidade: str, tributos: bool, isenta_kw: bool) -> dict:
    t = caso["tributos"]
    p = {
        "modalidade": modalidade,
        "base_tarifaria": "Tarifa de Aplicação",
        "aplicar_tributos": tributos,
        "pis": t["pis"],
        "cofins": t["cofins"],
        "icms": t["icms"],
        "tipo_icms": t.get("tipo_icms", "fora"),
        "reativos_direto": False,
        "arredondar_centavos": True,
        "tributar_reativos": caso["meta"]["distribuidora"] in TRIBUTA_REATIVO,
        "demanda_isenta_icms": True,
    }
    kw = caso["perfil"].get("demanda_isenta_icms_kw")
    if isenta_kw and kw:
        p["demanda_isenta_icms_kw"] = kw
    return p


def fatura(caso: dict, modalidade: str, tributos: bool = True, isenta_kw: bool = True) -> dict:
    r = client.post(
        "/api/calculo/fatura",
        json=corpo_fatura(caso),
        params=params_fatura(caso, modalidade, tributos, isenta_kw),
    )
    r.raise_for_status()
    return r.json()["fatura"]


def composicao(com: dict, sem: dict) -> dict:
    sem_por_desc = {l["descricao"]: l["custo"] for l in sem["linhas"]}
    acc = {"TE": 0.0, "TUSD energia": 0.0, "Demanda": 0.0, "Tributos": 0.0, "Outros": 0.0}
    for l in com["linhas"]:
        d = l["descricao"]
        valor, sem_v = l["custo"], sem_por_desc.get(d, l["custo"])
        acc["Tributos"] += max(0.0, valor - sem_v)
        if l["categoria"] == "TARIFA" and d.startswith("TE"):
            acc["TE"] += sem_v
        elif l["categoria"] == "TARIFA" and "DEMANDA" in d:
            acc["Demanda"] += sem_v
        elif l["categoria"] == "TARIFA":
            acc["TUSD energia"] += sem_v
        else:
            acc["Outros"] += sem_v
    return acc


# ---------------------------------------------------------------- planilha
def _secao(ws, linha: int, titulo: str, largura: int) -> int:
    ws.cell(row=linha, column=1, value=titulo).font = SECAO
    for c in range(1, largura + 1):
        ws.cell(row=linha, column=c).fill = FUNDO_SECAO
    ws.row_dimensions[linha].height = 20
    return linha + 2


def _tabela(ws, linha: int, cabecalhos: list[str], larguras: list[int]) -> int:
    for i, (h, w) in enumerate(zip(cabecalhos, larguras), start=1):
        c = ws.cell(row=linha, column=i, value=h)
        c.font, c.fill = CABECALHO, FUNDO_CAB
        c.alignment = Alignment(horizontal="left" if i == 1 else "right", wrap_text=True)
        c.border = Border(bottom=LINHA)
        ws.column_dimensions[get_column_letter(i)].width = w
    return linha + 1


def _linha(ws, linha: int, valores: list, negrito: bool = False, destaque: bool = False) -> int:
    for i, v in enumerate(valores, start=1):
        c = ws.cell(row=linha, column=i, value=v)
        c.font = CABECALHO if negrito else CORPO
        if isinstance(v, (int, float)):
            c.number_format = NUM
            c.alignment = Alignment(horizontal="right")
        if destaque:
            c.fill = FUNDO_DESTAQUE
    return linha + 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", default=str(RAIZ / "docs/apresentacao/simulacoes_3_faturas.xlsx"))
    args = ap.parse_args()

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)

    dados = []
    for cfg in CASOS:
        caso = json.loads((CASOS_DIR / cfg["arquivo"]).read_text(encoding="utf-8"))
        sims = {}
        for mod in cfg["modalidades"]:
            isenta = mod == caso["meta"]["modalidade"]
            com = fatura(caso, mod, True, isenta)
            sem = fatura(caso, mod, False, isenta)
            sims[mod] = {"com": com, "sem": sem, "comp": composicao(com, sem)}
        dados.append({**cfg, "caso": caso, "sims": sims})

    wb = Workbook()

    # ---------- Resumo
    ws = wb.active
    ws.title = "Resumo"
    ws["A1"] = "Simulação das 3 faturas reais — ACR por modalidade"
    ws["A1"].font = TITULO
    ws["A2"] = "Entradas copiadas das faturas; tarifas do dataset ANEEL pela vigência de cada caso."
    ws["A2"].font = NOTA

    linha = _secao(ws, 4, "Resultado por caso e modalidade", 8)
    linha = _tabela(
        ws, linha,
        ["Caso", "Modalidade", "Energia (MWh)", "Custo simulado (R$)", "R$/MWh",
         "Linhas da fatura (R$)", "Δ vs linhas (R$)", "Total impresso (R$)"],
        [30, 14, 14, 18, 12, 18, 16, 18],
    )
    for d in dados:
        meta = d["caso"]["meta"]
        pf = d["caso"]["perfil"]
        mwh = (pf.get("consumo_ponta_kwh", 0) + pf.get("consumo_fora_ponta_kwh", 0)) / 1000.0
        # Compara com a soma das linhas técnicas da fatura, não com o total
        # impresso: em CEMIG e Tucuruí o impresso tem créditos/retenções que
        # ficam fora do motor.
        tecnico = sum(l["valor"] for l in d["caso"]["linhas_esperadas"])
        for mod in d["modalidades"]:
            total = d["sims"][mod]["com"]["custo_total"]
            eh_real = mod == meta["modalidade"]
            linha = _linha(
                ws, linha,
                [d["id"], mod, mwh, total, total / mwh,
                 tecnico if eh_real else None,
                 (total - tecnico) if eh_real else None,
                 meta["total_fatura"] if eh_real else None],
                negrito=eh_real, destaque=eh_real,
            )
        linha += 1

    explicacoes = {
        "Copel — Grupo A": "reativo de 9 kVArh informado não gera excedente (fp ≥ 0,92, art. 304); "
                           "o resto fecha centavo a centavo",
        "CEMIG — BH CII_112": "fecha em R$ 0,06 nas linhas técnicas; o total impresso (R$ 52.234,40) é menor "
                              "porque a fatura traz créditos/retenções fora do motor (R$ 3.583,69)",
        "Equatorial — Tucuruí Núcleo": "diferença = reativo excedente de R$ 62,43 que a fatura cobra do optante e o "
                                       "motor não cobra (art. 303 — divergência D3 documentada); o total impresso "
                                       "(R$ 3.156,27) tem retenções federais de R$ 196,11",
    }
    linha = _secao(ws, linha, "Conferência — de onde vem cada diferença", 8)
    linha = _tabela(ws, linha, ["Caso", "Simulado (R$)", "Linhas da fatura (R$)", "Δ (R$)", "Explicação"],
                    [26, 16, 18, 12, 74])
    for d in dados:
        meta = d["caso"]["meta"]
        tecnico = sum(l["valor"] for l in d["caso"]["linhas_esperadas"])
        total = d["sims"][meta["modalidade"]]["com"]["custo_total"]
        linha = _linha(ws, linha, [d["id"], total, tecnico, total - tecnico,
                                   explicacoes.get(d["id"], "")])
    linha += 1

    linha = _secao(ws, linha, "Como ler cada linha", 8)
    linha = _tabela(ws, linha, ["Caso", "Modalidade da fatura", "Observação"], [30, 20, 84])
    for d in dados:
        linha = _linha(ws, linha, [d["id"], d["caso"]["meta"]["modalidade"], d["nota"]])
    ws.freeze_panes = "A6"

    # ---------- Entradas
    ws = wb.create_sheet("Entradas")
    ws["A1"] = "Entradas de cada fatura"
    ws["A1"].font = TITULO
    ws["A2"] = "Exatamente o que foi enviado à API."
    ws["A2"].font = NOTA
    cab = ["Campo", *[d["curto"] for d in dados]]

    linha = _secao(ws, 4, "Identificação", 4)
    linha = _tabela(ws, linha, cab, [34, 26, 26, 26])
    for nome, fn in [
        ("Distribuidora", lambda d: d["caso"]["meta"]["distribuidora"]),
        ("Subgrupo", lambda d: d["caso"]["meta"]["subgrupo"]),
        ("Competência", lambda d: d["caso"]["meta"]["competencia"]),
        ("Modalidade da fatura", lambda d: d["caso"]["meta"]["modalidade"]),
        ("Data de referência (tarifa)", lambda d: d["caso"]["perfil"]["data_referencia"]),
        ("Unidade", lambda d: d["caso"]["meta"].get("uc", "—")),
        ("PDF de origem", lambda d: Path(d["caso"]["meta"]["fonte"]).name),
    ]:
        linha = _linha(ws, linha, [nome, *[fn(d) for d in dados]])
    linha += 1

    linha = _secao(ws, linha, "Consumo, demanda e reativos", 4)
    linha = _tabela(ws, linha, cab, [34, 26, 26, 26])
    for nome, chave in [
        ("Consumo ponta (kWh)", "consumo_ponta_kwh"),
        ("Consumo fora de ponta (kWh)", "consumo_fora_ponta_kwh"),
        ("Demanda medida (kW)", "demanda_medida_unica_kw"),
        ("Demanda contratada (kW)", "demanda_contratada_unica_kw"),
        ("Reativo energia ponta (kVArh)", "reativo_energia_ponta_kvArh"),
        ("Reativo energia fora ponta (kVArh)", "reativo_energia_fora_ponta_kvArh"),
        ("Demanda isenta de ICMS (kW)", "demanda_isenta_icms_kw"),
        ("Bandeira adicional (R$/kWh)", "bandeira_adicional_r_kwh"),
        ("CIP/COSIP (R$)", "cip_cosip_rs"),
        ("Outros valores (R$)", "outros_rs"),
    ]:
        vals = [d["caso"]["perfil"].get(chave) for d in dados]
        if all(v in (None, 0, 0.0) for v in vals):
            continue
        linha = _linha(ws, linha, [nome, *[v if v is not None else "—" for v in vals]])
    linha += 1

    linha = _secao(ws, linha, "Tributos e flags", 4)
    linha = _tabela(ws, linha, cab, [34, 26, 26, 26])
    linha = _linha(ws, linha, ["PIS (%)", *[d["caso"]["tributos"]["pis"] * 100 for d in dados]])
    linha = _linha(ws, linha, ["COFINS (%)", *[d["caso"]["tributos"]["cofins"] * 100 for d in dados]])
    linha = _linha(ws, linha, ["ICMS (%)", *[d["caso"]["tributos"]["icms"] * 100 for d in dados]])
    linha = _linha(ws, linha, ["ICMS por fora", *[d["caso"]["tributos"].get("tipo_icms", "fora") for d in dados]])
    linha = _linha(ws, linha, ["Tributar reativos", *["sim" if d["caso"]["meta"]["distribuidora"] in TRIBUTA_REATIVO else "não" for d in dados]])
    linha = _linha(ws, linha, ["Demanda isenta de ICMS", *["sim" for _ in dados]])
    linha = _linha(ws, linha, ["Cenários simulados", *[" + ".join(d["modalidades"]) for d in dados]])

    # ---------- Resultados
    ws = wb.create_sheet("Resultados")
    ws["A1"] = "Composição do custo simulado"
    ws["A1"].font = TITULO
    ws["A2"] = "TE e TUSD sem tributos; a coluna Tributos é a diferença para o valor com tributos."
    ws["A2"].font = NOTA
    linha = _secao(ws, 4, "Por caso e modalidade", 9)
    linha = _tabela(
        ws, linha,
        ["Caso", "Modalidade", "TE (R$)", "TUSD energia (R$)", "Demanda (R$)",
         "Tributos (R$)", "Outros (R$)", "Total (R$)", "% da fatura real"],
        [28, 14, 14, 16, 14, 14, 12, 14, 16],
    )
    for d in dados:
        real = d["caso"]["meta"]["total_fatura"]
        for mod in d["modalidades"]:
            c = d["sims"][mod]["comp"]
            total = d["sims"][mod]["com"]["custo_total"]
            linha = _linha(
                ws, linha,
                [d["id"], mod, c["TE"], c["TUSD energia"], c["Demanda"], c["Tributos"],
                 c["Outros"], total, total / real],
                destaque=mod == d["caso"]["meta"]["modalidade"],
            )
            ws.cell(row=linha - 1, column=9).number_format = "0.0%"
        linha += 1

    # ---------- Faturas
    for d in dados:
        ws = wb.create_sheet(f"Fatura {d['curto'][:8]}")
        ws["A1"] = f"Fatura simulada — {d['id']}"
        ws["A1"].font = TITULO
        ws["A2"] = (
            f"{d['caso']['meta']['distribuidora']} · {d['caso']['meta']['subgrupo']} · "
            f"competência {d['caso']['meta']['competencia']} · {d['nota']}"
        )
        ws["A2"].font = NOTA
        linha = _secao(ws, 4, "Linhas de cobrança por modalidade", 6)
        linha = _tabela(
            ws, linha,
            ["Item", "Modalidade", "Quantidade", "Tarifa (R$)", "Valor (R$)", "% do total"],
            [46, 14, 14, 14, 16, 12],
        )
        for mod in d["modalidades"]:
            f = d["sims"][mod]["com"]
            for l in f["linhas"]:
                linha = _linha(ws, linha, [l["descricao"], mod, l["quantidade"], l["tarifa"],
                                           l["custo"], l["custo"] / f["custo_total"]])
                ws.cell(row=linha - 1, column=6).number_format = "0.0%"
            linha = _linha(ws, linha, [f"Total — {mod}", mod, None, None, f["custo_total"], 1.0], negrito=True)
            ws.cell(row=linha - 1, column=6).number_format = "0.0%"
        linha += 1
        ws.cell(row=linha, column=1,
                value="Energia em R$/MWh e demanda em R$/kW; a quantidade está na unidade da tarifa.").font = NOTA

    # ---------- E-PI
    ws = wb.create_sheet("E-PI")
    ws["A1"] = "Preço de indiferença (E-PI) — teto para negociar no ACL"
    ws["A1"].font = TITULO
    ws["A2"] = "Perdas k = 3% · encargos R$ 0/MWh · E-PI simplificado (sem OPEX/CAPEX)."
    ws["A2"].font = NOTA
    linha = _secao(ws, 4, "E-PI por caso e modalidade", 6)
    linha = _tabela(ws, linha, ["Caso", "Modalidade", "E-PI (R$/MWh)", "Energia (MWh)",
                                "Custo ACR (R$)", "Aviso"], [28, 16, 16, 14, 18, 44])
    for d in dados:
        meta, trib = d["caso"]["meta"], d["caso"]["tributos"]
        for mod in d["modalidades"]:
            r = client.post(
                "/api/epi/calcular",
                json={
                    "distribuidora": meta["distribuidora"],
                    "subgrupo": meta["subgrupo"],
                    "data_referencia": d["caso"]["perfil"]["data_referencia"],
                    "modalidade": mod,
                    "atividade": "Comercial ou Industrial",
                    "consumo_ponta_kwh": d["caso"]["perfil"].get("consumo_ponta_kwh", 0.0),
                    "consumo_fora_ponta_kwh": d["caso"]["perfil"].get("consumo_fora_ponta_kwh", 0.0),
                    "pis": trib["pis"],
                    "cofins": trib["cofins"],
                    "icms": trib["icms"],
                    "k": 0.03,
                    "encargos": 0.0,
                    "opex_mensal": 0.0,
                    "capex": 0.0,
                    "horizonte_meses": 60,
                },
            )
            if r.status_code != 200:
                linha = _linha(ws, linha, [d["id"], mod, "—", None, None,
                                           str(r.json().get("detail", "erro"))[:50]])
                continue
            e = r.json()
            linha = _linha(ws, linha, [d["id"], mod, e["pi"], e["e_mwh"], e["c_e_acr"],
                                       (e.get("aviso") or "")[:50]])
        linha += 1

    # ---------- Validação (todos os casos, camada 1)
    spec = importlib.util.spec_from_file_location("resultados_artigo", RAIZ / "scripts/resultados_artigo.py")
    ra = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ra)

    ws = wb.create_sheet("Validação")
    ws["A1"] = "Validação do motor contra as faturas reais (camada 1: tarifas impressas)"
    ws["A1"].font = TITULO
    ws["A2"] = "Critério: ≤ R$ 0,05 por item e ≤ R$ 1,00 no total técnico."
    ws["A2"].font = NOTA
    linha = _secao(ws, 4, "Todos os casos de docs/validacao_faturas_reais/casos", 6)
    linha = _tabela(ws, linha, ["Caso", "Item da fatura", "Fatura (R$)", "Motor (R$)", "Δ (R$)", "Status"],
                    [26, 42, 16, 16, 12, 12])
    for arq in sorted(ra.CASOS.glob("*.json")):
        r = ra.validar_arquivo(arq.name)
        for l in r["linhas"]:
            linha = _linha(
                ws, linha,
                [r["caso"], l["item"][:40], l["fatura"],
                 l["motor"] if l["motor"] is not None else "sem mapeamento",
                 l["delta"] if l["delta"] is not None else None,
                 "OK" if (l["delta"] is not None and abs(l["delta"]) <= 0.05) else "conferir"],
            )
        linha = _linha(ws, linha, [f"{r['caso']} — total", "", None, None, r["delta_total"],
                                   "OK" if r["aprovado"] else "DIVERGE"], negrito=True)
        linha += 1

    # ---------- Premissas
    ws = wb.create_sheet("Premissas")
    ws["A1"] = "Premissas da simulação"
    ws["A1"].font = TITULO
    itens = [
        ("Faturas de entrada", "Copel 04/2023 (Verde) · CEMIG BH CII_112 12/2023 (Verde) · Equatorial Tucuruí Núcleo 12/2024 (Optante B)"),
        ("Tarifas", "PostgreSQL com o dataset ANEEL, base 'Tarifa de Aplicação', vigência da data de referência de cada caso"),
        ("Bandeira", "Automática pela competência (tabela ANEEL 2015-01 a 2026-10); Tucuruí usa a bandeira pro rata impressa (0,0053016 R$/kWh)"),
        ("Tributos", "Alíquotas de cada fatura; ICMS por fora (multiplicativo)"),
        ("Demanda isenta de ICMS", "Sim (Súmula 391/STJ): na modalidade da fatura usa-se a quantidade impressa; nas simuladas, a API calcula contratada − medida"),
        ("Reativos", "Tributados em CEMIG e Equatorial (como na fatura); não tributados na Copel"),
        ("Azul simulada", "Copel e CEMIG são unidades Verde: a Azul usa a demanda medida única nos dois postos e a contratada única nas duas (premissa D6)"),
        ("Optante B", "Tucuruí é caso real de optante (art. 292): tarifa única do Grupo B, sem demanda"),
        ("CIP/COSIP", "Entra no total da fatura; fora do custo técnico nas comparações (premissa D4)"),
        ("Retenções", "Fora do motor (Tucuruí: −196,11 na fatura real)"),
        ("Gerado em", datetime.now().strftime("%d/%m/%Y %H:%M")),
        ("Script", "scripts/gerar_planilha_apresentacao.py"),
    ]
    linha = _secao(ws, 3, "Considerações", 2)
    linha = _tabela(ws, linha, ["Item", "Valor"], [32, 98])
    for k, v in itens:
        linha = _linha(ws, linha, [k, v])

    wb.save(saida)
    print(f"planilha: {saida}")
    print(f"abas: {', '.join(wb.sheetnames)}")
    for d in dados:
        for mod in d["modalidades"]:
            f = d["sims"][mod]["com"]
            print(f"  {d['curto']:10s} {mod:10s} R$ {f['custo_total']:>12,.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
