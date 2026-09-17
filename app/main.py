"""Página principal do Streamlit.

Define a página inicial do aplicativo com a navegação para as páginas de
consulta, simulação e comparação.
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Projeto ACR x ACL",
    layout="wide",
)

st.title("Projeto de Análise e Otimização ACR x ACL")
st.markdown(
    "Ferramenta para **enquadramento tarifário de consumidores potencialmente livres** "
    "cálculo no ACR, otimização de modalidades, EPI simplificado e projeção experimental."
)

st.divider()

st.subheader("O que está disponível")
st.markdown(
    "- **Consulta Tarifas**: leitura das tarifas ANEEL carregadas.\n"
    "- **Simulação de Fatura**: calcula a fatura do Grupo A (Azul/Verde) "
    "para um perfil.\n"
    "- **Comparação de Modalidades** Azul × Verde para o mesmo "
    "perfil.")

st.info(
    "Use a barra lateral para navegar. A API FastAPI precisa estar rodando "
    "em `http://127.0.0.1:8000` (`run_api.bat`)."
)
