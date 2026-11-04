"""Componentes visuais reutilizáveis do front (tema, cards, gráficos)."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

COR_TE = "#1f4e79"
COR_TUSD = "#2e7d32"
COR_TOTAL = "#37474f"
COR_DELTA_POS = "#2e7d32"
COR_DELTA_NEG = "#c62828"

_CSS = """
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
h1, h2, h3 {color: #1a2b3c; letter-spacing: -0.01em;}
[data-testid="stMetricValue"] {font-weight: 700; color: #1a2b3c;}
.card {
  background: #ffffff;
  border: 1px solid #e3e8ee;
  border-radius: 10px;
  padding: 1rem 1.2rem;
  box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);
  margin-bottom: 0.6rem;
}
.card .card-titulo {font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; color: #5b6b7b;}
.card .card-valor {font-size: 1.7rem; font-weight: 700; color: #1a2b3c;}
.card .card-delta {font-size: 0.85rem; font-weight: 600;}
.delta-pos {color: #2e7d32;}
.delta-neg {color: #c62828;}
</style>
"""


def injetar_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def section_header(titulo: str, descricao: str | None = None) -> None:
    st.markdown(f"### {titulo}")
    if descricao:
        st.markdown(descricao)


def card(titulo: str, valor: str, delta: str | None = None, delta_pos: bool | None = None) -> None:
    delta_html = ""
    if delta is not None:
        classe = "delta-pos" if delta_pos else "delta-neg"
        delta_html = f'<div class="card-delta {classe}">{delta}</div>'
    st.markdown(
        f'<div class="card"><div class="card-titulo">{titulo}</div>'
        f'<div class="card-valor">{valor}</div>{delta_html}</div>',
        unsafe_allow_html=True,
    )


def metricas(totais: dict[str, float]) -> None:
    cols = st.columns(len(totais) or 1)
    for col, (nome, valor) in zip(cols, totais.items()):
        col.metric(nome, f"R$ {valor:,.2f}")


def tema_layout(fig: go.Figure, altura: int = 340) -> go.Figure:
    fig.update_layout(
        height=altura,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, sans-serif", color="#1a2b3c"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return fig


def grafico_barras_agrupado(
    df: pd.DataFrame,
    x: str,
    colunas: list[str],
    titulo: str,
    cores: list[str] | None = None,
    altura: int = 340,
) -> None:
    fig = go.Figure()
    cores = cores or [COR_TE, COR_TUSD, COR_TOTAL, "#e6b800", "#8e24aa"]
    for i, col in enumerate(colunas):
        fig.add_trace(
            go.Bar(
                x=df[x],
                y=df[col],
                name=col,
                marker_color=cores[i % len(cores)],
            )
        )
    fig.update_layout(barmode="group", title=titulo)
    st.plotly_chart(tema_layout(fig, altura), use_container_width=True)


def grafico_pizza(labels: list[str], valores: list[float], titulo: str, altura: int = 340) -> None:
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=valores,
            hole=0.45,
            marker=dict(colors=[COR_TE, COR_TUSD, "#e6b800", "#8e24aa", "#5b6b7b", "#c62828"]),
        )
    )
    fig.update_layout(title=titulo)
    st.plotly_chart(tema_layout(fig, altura), use_container_width=True)
