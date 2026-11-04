"""Página de simulação de fatura (Grupo A).

Consome ``POST /api/calculo/fatura`` e mostra as linhas + totais.
"""

from __future__ import annotations

import streamlit as st

from app.components.ui import injetar_css

from app.components.casos_prontos import CASOS_FATURAS_REAIS
from app.components.simulacao import (
    CASO_ARTIGO_ERIAC,
    extrair_reativos_params,
    formulario_perfil,
    formulario_tributos,
    post_json,
    render_bandeira_usada,
    render_linhas_fatura,
    resolver_bandeira,
)

injetar_css()
st.set_page_config(page_title="Simulação de Fatura", layout="wide")
st.title("Simulação de Fatura: Grupo A")
st.caption(
    "Preencha o perfil e calcule a fatura de uma modalidade (Verde ou Azul) com base na tarifa de aplicação."
)

opcoes_caso = ["Manual", "Artigo ERIAC 2025 — CPFL Piratininga A4 05/2018"] + list(CASOS_FATURAS_REAIS.keys())
caso_escolhido = st.selectbox("Caso pronto (pré-carregado)", opcoes_caso, index=0)
if caso_escolhido.startswith("Artigo"):
    st.session_state["caso_pronto"] = CASO_ARTIGO_ERIAC
    st.info("Caso do artigo pré-carregado no formulário.")
elif caso_escolhido in CASOS_FATURAS_REAIS:
    st.session_state["caso_pronto"] = CASOS_FATURAS_REAIS[caso_escolhido]
    st.info(f"Caso real '{caso_escolhido}' pré-carregado — compare com o valor da fatura.")
else:
    st.session_state.pop("caso_pronto", None)

modalidade = st.radio("Modalidade", ["Verde", "Azul", "Optante B", "Convencional Monômia", "Branca"], horizontal=True)
tributos = formulario_tributos()
perfil = formulario_perfil(modalidade=modalidade)

if perfil is not None:
    st.divider()
    st.subheader("Resultado")
    render_bandeira_usada(perfil["data_referencia"])
    perfil["bandeira_adicional_r_kwh"] = resolver_bandeira(perfil)
    reativos_params = extrair_reativos_params(perfil)

    if not tributos["aplicar_tributos"]:
        st.warning(
            "Fatura na **base líquida (sem tributos)**. Para incluir "
            "PIS/COFINS/ICMS, marque 'Aplicar PIS/COFINS/ICMS' em 'Tributos' "
            "e calcule novamente."
        )

    params = {
        "modalidade": modalidade,
        "base_tarifaria": "Tarifa de Aplicação",
        "arredondar_centavos": True,
        "tributar_reativos": tributos["aplicar_tributos"],
        **tributos,
        **reativos_params,
    }
    resp, erro = post_json("/calculo/fatura", perfil, params)
    if erro:
        st.error(erro)
    elif resp is not None and resp.status_code == 200:
        dados = resp.json()
        fatura = dados["fatura"]
        st.markdown(f"### Fatura — {fatura['modalidade']}")
        render_linhas_fatura(fatura)
    elif resp is not None:
        st.error(f"Erro {resp.status_code}: {resp.text}")
