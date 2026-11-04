"""Página de comparação de modalidades (Azul × Verde).

Consome ``POST /api/calculo/comparar`` e mostra o ranking + indisponíveis.
"""

from __future__ import annotations

import streamlit as st

from app.components.ui import injetar_css

from app.components.ui import grafico_barras_agrupado
from app.components.simulacao import (
    extrair_reativos_params,
    formulario_perfil,
    formulario_tributos,
    post_json,
    render_bandeira_usada,
    render_linhas_fatura,
    resolver_bandeira,
)

injetar_css()
st.set_page_config(page_title="Comparação de Modalidades", layout="wide")
st.title("Comparação de Modalidades — Grupo A")
st.caption("Calcula Azul × Verde para o mesmo perfil e ranqueia por menor custo.")

tributos = formulario_tributos()
perfil = formulario_perfil()

if perfil is not None:
    st.divider()
    st.subheader("Resultado")
    render_bandeira_usada(perfil["data_referencia"])
    perfil["bandeira_adicional_r_kwh"] = resolver_bandeira(perfil)
    reativos_params = extrair_reativos_params(perfil)

    if not tributos["aplicar_tributos"]:
        st.warning(
            "Comparação na **base líquida (sem tributos)**. Para incluir "
            "PIS/COFINS/ICMS, marque 'Aplicar PIS/COFINS/ICMS' em 'Tributos' "
            "e calcule novamente."
        )

    params = {
        "base_tarifaria": "Tarifa de Aplicação",
        **tributos,
        **reativos_params,
    }
    resp, erro = post_json("/calculo/comparar", perfil, params)
    if erro:
        st.error(erro)
    elif resp is not None and resp.status_code == 200:
        comp = resp.json()["comparacao"]

        melhor = comp.get("melhor")
        if melhor:
            st.success(f"Melhor modalidade: **{melhor}**")

        st.markdown("### Modalidades disponíveis (menor → maior custo)")
        disponiveis = comp.get("disponiveis", [])
        if not disponiveis:
            st.warning("Nenhuma modalidade disponível para este perfil/data.")

        if disponiveis:
            colunas = st.columns(len(disponiveis))
            for col, fatura in zip(colunas, disponiveis):
                col.metric(
                    f"{fatura['modalidade']} (R$)",
                    f"{fatura['custo_total']:,.2f}",
                    "menor custo" if fatura['modalidade'] == melhor else None,
                )

            import pandas as pd
            linhas_grafico = []
            for fatura in disponiveis:
                te = sum(
                    l["custo"] for l in fatura.get("linhas", [])
                    if (l.get("descricao") or "").upper().startswith("TE ")
                )
                tusd = sum(
                    l["custo"] for l in fatura.get("linhas", [])
                    if "TUSD" in (l.get("descricao") or "").upper()
                )
                linhas_grafico.append(
                    {"Modalidade": fatura["modalidade"], "TE (R$)": round(te, 2), "TUSD (R$)": round(tusd, 2)}
                )
            df_comp = pd.DataFrame(linhas_grafico)
            grafico_barras_agrupado(
                df_comp, "Modalidade", ["TE (R$)", "TUSD (R$)"],
                "TE × TUSD por modalidade",
            )

        for fatura in disponiveis:
            with st.expander(
                f"{fatura['modalidade']} — R$ {fatura['custo_total']:,.2f}",
                expanded=(fatura["modalidade"] == melhor),
            ):
                render_linhas_fatura(fatura)

        indisponiveis = comp.get("indisponiveis", [])
        if indisponiveis:
            st.markdown("### Indisponíveis")
            st.table(
                [
                    {"Modalidade": i["modalidade"], "Motivo": i["motivo"]}
                    for i in indisponiveis
                ]
            )

        st.info(
            "A comparação cobre Azul, Verde e **Optante B** (quando elegível). "
            "As modalidades do Grupo B (Convencional Monômia e Branca) podem ser "
            "simuladas na página **Simulação de Fatura**."
        )
    elif resp is not None:
        st.error(f"Erro {resp.status_code}: {resp.text}")
