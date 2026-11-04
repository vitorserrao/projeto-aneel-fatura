"""Página principal do Streamlit — visão geral do projeto."""
from __future__ import annotations

import streamlit as st

from app.components.ui import card, injetar_css, section_header

injetar_css()
st.set_page_config(page_title="Projeto ACR × ACL", layout="wide")

st.title("Projeto de Análise e Otimização ACR × ACL")
st.markdown(
    "Ferramenta acadêmica para **enquadramento tarifário de consumidores "
    "potencialmente livres**: cálculo no ACR, otimização de modalidades, "
    "validação contra faturas reais e projeção experimental."
)

section_header(
    "Módulos disponíveis",
    "Use a barra lateral para navegar. A API FastAPI precisa estar rodando "
    "em `http://127.0.0.1:8000` (`run_api.bat`).",
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    card("Consulta Tarifas", "Leitura", "tarifas ANEEL carregadas", delta_pos=True)
with c2:
    card("Simulação de Fatura", "Azul · Verde · B", "Grupo A, Optante B e Grupo B", delta_pos=True)
with c3:
    card("Comparação", "Ranking", "menor custo entre modalidades", delta_pos=True)
with c4:
    card("Validação", "Faturas reais", "fatura × motor, caso a caso", delta_pos=True)

st.divider()
st.info(
    "**Fluxo sugerido:** consulte as tarifas → simule uma fatura → compare "
    "modalidades → confira a validação com faturas reais."
)
