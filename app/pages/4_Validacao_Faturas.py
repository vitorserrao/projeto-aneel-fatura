"""Página de validação — faturas reais × motor (camadas 1 e 2)."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from app.components.simulacao import post_json
from app.components.ui import grafico_barras_agrupado, injetar_css, section_header

injetar_css()
st.set_page_config(page_title="Validação — Faturas Reais", layout="wide")

CASOS_DIR = Path("docs/validacao_faturas_reais/casos")


@st.cache_data(show_spinner=False)
def _carregar_casos() -> dict[str, dict]:
    casos = {}
    for arq in sorted(CASOS_DIR.glob("*.json")):
        casos[arq.stem] = json.loads(arq.read_text(encoding="utf-8"))
    return casos


def _rotina_validacao():
    """Mesma rotina dos resultados do artigo (scripts/resultados_artigo.py)."""
    import importlib.util

    raiz = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location(
        "resultados_artigo", raiz / "scripts" / "resultados_artigo.py"
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


st.title("Validação — Faturas Reais × Motor")
section_header(
    "Casos reais",
    "Compara as linhas da fatura real com o motor (camada 1: tarifas da própria fatura).",
)

casos = _carregar_casos()
nome = st.selectbox("Caso", sorted(casos.keys()))
caso = casos[nome]

meta = caso["meta"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Distribuidora", meta["distribuidora"])
c2.metric("Modalidade", meta["modalidade"])
c3.metric("Competência", meta["competencia"])
c4.metric("Total fatura", f"R$ {meta['total_fatura']:,.2f}")

with st.expander("Entradas do caso (JSON)", expanded=False):
    st.json(caso["perfil"])

resultado = _rotina_validacao().validar_arquivo(f"{nome}.json")
st.metric("Soma técnica (motor)", f"R$ {resultado['soma_tecnica_motor']:,.2f}",
          delta=f"R$ {resultado['delta_total']:+,.2f} vs fatura (soma técnica)")

linhas = [
    {
        "Linha": l["item"],
        "Fatura (R$)": l["fatura"],
        "Motor (R$)": l["motor"],
        "Δ (R$)": l["delta"],
        "Status": "✅" if l["delta"] is not None and abs(l["delta"]) <= 0.05
        else ("⚠️" if l["delta"] is not None else "—"),
    }
    for l in resultado["linhas"]
]
df = pd.DataFrame(linhas)
st.dataframe(df, use_container_width=True, hide_index=True)

diffs = [r for r in linhas if r["Δ (R$)"] is not None]
if diffs:
    df_diff = pd.DataFrame(diffs)
    df_diff["Linha"] = df_diff["Linha"].str.slice(0, 30)
    grafico_barras_agrupado(
        df_diff.set_index("Linha").reset_index(),
        "Linha",
        ["Δ (R$)"],
        "Diferenças por linha (fatura − motor)",
        altura=380,
    )

if st.button("Recalcular via API (camada 2 — tarifas do banco)"):
    trib = caso["tributos"]
    rt = _tarifa_reativo(caso)
    params = {
        "modalidade": meta["modalidade"],
        "base_tarifaria": "Tarifa de Aplicação",
        "aplicar_tributos": "true",
        "pis": trib["pis"],
        "cofins": trib["cofins"],
        "icms": trib["icms"],
        "tipo_icms": trib["tipo_icms"],
        "arredondar_centavos": "true",
        "demanda_isenta_icms": "true",
        "tributar_reativos": "true",
    }
    if rt is not None:
        params["reativos_direto"] = "true"
        params["tarifa_reativo_energia_r_kvarh"] = rt
    if caso["perfil"].get("demanda_isenta_icms_kw"):
        params["demanda_isenta_icms_kw"] = caso["perfil"]["demanda_isenta_icms_kw"]
    resp, erro = post_json("/calculo/fatura", caso["perfil"], params)
    if erro:
        st.error(erro)
    elif resp is not None and resp.status_code == 200:
        f = resp.json()["fatura"]
        st.metric("Total API (banco)", f"R$ {f['custo_total']:,.2f}")
    elif resp is not None:
        st.error(f"Erro {resp.status_code}: {resp.text}")

for nota in caso.get("notas", []):
    st.caption(f"📝 {nota}")
