"""Página de simulação de fatura (Grupo A).

Consome ``POST /api/calculo/fatura`` e mostra as linhas + totais.
"""

from __future__ import annotations

import streamlit as st

from app.components.simulacao import (
    formulario_perfil,
    formulario_tributos,
    post_json,
    render_bandeira_usada,
    render_linhas_fatura,
    resolver_bandeira,
)

st.set_page_config(page_title="Simulação de Fatura", layout="wide")
st.title("Simulação de Fatura: Grupo A")
st.caption(
    "Preencha o perfil e calcule a fatura de uma modalidade (Verde ou Azul) com base na tarifa de aplicação."
)

modalidade = st.radio("Modalidade", ["Verde", "Azul"], horizontal=True)
tributos = formulario_tributos()
perfil = formulario_perfil(modalidade=modalidade)

if perfil is not None:
    st.divider()
    st.subheader("Resultado")
    render_bandeira_usada(perfil["data_referencia"])
    perfil["bandeira_adicional_r_kwh"] = resolver_bandeira(perfil)

    if not tributos["aplicar_tributos"]:
        st.warning(
            "Fatura na **base líquida (sem tributos)**. Para incluir "
            "PIS/COFINS/ICMS, marque 'Aplicar PIS/COFINS/ICMS' em 'Tributos' "
            "e calcule novamente."
        )

    params = {
        "modalidade": modalidade,
        "base_tarifaria": "Tarifa de Aplicação",
        **tributos,
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
