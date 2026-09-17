"""Página de consulta tarifária (Sprint P3) — camada de LEITURA apenas.

Consome a API FastAPI (grupo de rotas de consulta) via HTTP; não acessa o
banco nem calcula nada. Mostra distribuidoras e tarifas reais carregadas.
"""

from __future__ import annotations

import os

import requests
import streamlit as st

API_BASE = os.environ.get("ANEEL_API_BASE", "http://127.0.0.1:8000/api")


def _get(path: str, params: dict | None = None):
    try:
        return requests.get(f"{API_BASE}{path}", params=params, timeout=10), None
    except requests.RequestException as exc:
        return None, f"Falha ao contactar a API em `{API_BASE}`. O servidor está rodando? Detalhe: {exc}"


st.set_page_config(page_title="Consulta Tarifas", layout="wide")
st.title("📄 Consulta de tarifas (leitura)")
st.caption(f"API de consulta: `{API_BASE}`")
st.markdown("Camada de leitura: mostra dado real da ANEEL já carregado, sem cálculo.")


st.markdown("""
<style>
/* Esconde o botão "Implementar" */
[data-testid="stDeployButton"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# Explica o endpoint e oferece botão para testar distribuidoras
if st.button("Carregar distribuidoras", type="primary"):
    resp, err = _get("/distribuidoras")
    if err:
        st.error(err)
    else:
        rows = resp.json()
        st.success(f"{len(rows)} distribuidoras carregadas.")
        st.dataframe([{"CNPJ": d["num_cnpj"], "Sigla": d["sig_agente"]} for d in rows])

st.divider()
st.subheader("Buscar tarifas vigentes")

col_sig, col_data, col_sub, col_mod, col_base, col_comp = st.columns(6)
sig = col_sig.text_input("Sigla distribuidora", "CPFL JAGUARI")
data = col_data.text_input("Data (AAAA-MM-DD)", "2010-06-01")
sub = col_sub.text_input("Subgrupo", "")
mod = col_mod.text_input("Modalidade", "")
base = col_base.text_input("Base tarifária", "")
comp = col_comp.selectbox("Componente", ["", "TE", "TUSD"], index=0)

if st.button("Consultar tarifas"):
    params = {}
    if sig:
        params["sig_agente"] = sig
    if data:
        params["data"] = data
    if sub:
        params["subgrupo"] = sub
    if mod:
        params["modalidade"] = mod
    if base:
        params["base_tarifaria"] = base
    if comp:
        params["componente"] = comp
    resp, err = _get("/tarifas", params)
    if err:
        st.error(err)
    elif resp.status_code == 400:
        st.error(resp.json().get("detail", "consulta inválida"))
    else:
        rows = resp.json()
        st.info(f"{len(rows)} registro(s) retornado(s).")
        if rows:
            st.dataframe(
                [
                    {
                        "Sigla": t["sig_agente"],
                        "Componente": t["componente"],
                        "Valor": t["valor"],
                        "Base": t["base_tarifaria"],
                        "Posto": t["posto"],
                        "Início": t["inicio_vigencia"],
                        "Fim": t["fim_vigencia"],
                        "Resolução": t["resolucao"],
                    }
                    for t in rows
                ]
            )
