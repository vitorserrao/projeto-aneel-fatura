"""Componentes compartilhados das páginas de simulação (Streamlit).

Camada de APRESENTAÇÃO apenas: monta o formulário do perfil do consumidor e
chama a API FastAPI por HTTP. Nenhuma regra de negócio vive aqui.
"""

from __future__ import annotations

import os
from datetime import date

import requests
import streamlit as st

API_BASE = os.environ.get("ANEEL_API_BASE", "http://127.0.0.1:8000/api")

SUBGRUPOS = ["A1", "A2", "A3", "A3a", "A4", "AS", "B1", "B2", "B3", "B4"]


def get_json(path: str, params: dict | None = None):
    """GET na API; retorna ``(dados, erro)``."""
    try:
        resp = requests.get(f"{API_BASE}{path}", params=params, timeout=30)
        return resp, None
    except requests.RequestException as exc:
        return None, (
            f"Falha ao contactar a API em `{API_BASE}`. O servidor FastAPI "
            f"está rodando? Detalhe: {exc}"
        )


def post_json(path: str, payload: dict, params: dict | None = None):
    """POST na API; retorna ``(response, erro)``."""
    try:
        resp = requests.post(
            f"{API_BASE}{path}", json=payload, params=params, timeout=60
        )
        return resp, None
    except requests.RequestException as exc:
        return None, (
            f"Falha ao contactar a API em `{API_BASE}`. O servidor FastAPI "
            f"está rodando? Detalhe: {exc}"
        )


def buscar_bandeira(competencia: str) -> dict | None:
    """Consulta a bandeira tarifária da competência na API."""
    resp, erro = get_json("/bandeira", {"competencia": competencia})
    if erro:
        return {"erro": erro}
    if resp is not None and resp.status_code == 200:
        return resp.json()
    return None


def buscar_bandeiras(competencia: str) -> dict | None:
    """Consulta as opções de bandeira e valores vigentes na competência."""
    resp, erro = get_json("/bandeiras", {"competencia": competencia})
    if erro:
        return {"erro": erro}
    if resp is not None and resp.status_code == 200:
        return resp.json()
    return None


def resolver_bandeira(perfil: dict) -> float:
    """Converte a bandeira selecionada no valor (R$/kWh) do banco.

    "Automática (bandeira do mês)" devolve 0 — a API busca a bandeira vigente.
    As demais opções buscam o valor vigente na competência em ``GET /bandeiras``.
    """
    selecionada = perfil.pop("bandeira_selecionada", None) or "Automática (bandeira do mês)"
    if selecionada == "Automática (bandeira do mês)":
        return 0.0
    dados = buscar_bandeiras(perfil["data_referencia"])
    if not dados or "opcoes" not in dados:
        return 0.0
    for opcao in dados["opcoes"]:
        if opcao["bandeira"] == selecionada:
            return float(opcao["valor_kwh"])
    return 0.0


def formulario_perfil(
    prefixo: str = "perfil", modalidade: str | None = None
) -> dict | None:
    """Formulário com as entradas do ``Consumidor``; retorna o payload.

    ``modalidade`` (quando informada) controla quais campos de DEMANDA são
    exibidos: "Azul" -> demanda por posto (Ponta/Fora Ponta); "Verde" ->
    demanda única. ``None`` exibe ambos (uso na comparação).
    """
    mostrar_posto = modalidade in (None, "Azul")
    mostrar_unica = modalidade in (None, "Verde")
    with st.form(prefixo):
        st.markdown("**Dados da unidade consumidora**")
        c1, c2, c3 = st.columns(3)
        distribuidora = c1.text_input(
            "Distribuidora (sig_agente)", value="COPEL-DIS"
        )
        subgrupo = c2.selectbox("Subgrupo", SUBGRUPOS, index=4)  # A4
        classe = c3.text_input("Classe", value="Não se aplica")

        c1, c2, c3 = st.columns(3)
        subclasse = c1.text_input("Subclasse", value="Não se aplica")
        detalhe = c2.text_input("Detalhe", value="Não se aplica")
        data_referencia = c3.date_input(
            "Data de referência", value=date(2023, 3, 15)
        )

        st.markdown("**Consumo (kWh)**")
        c1, c2 = st.columns(2)
        consumo_ponta = c1.number_input(
            "Consumo Ponta (kWh)", min_value=0.0, value=55.0
        )
        consumo_fora = c2.number_input(
            "Consumo Fora Ponta (kWh)", min_value=0.0, value=9094.0
        )

        # Defaults neutros; preenchidos conforme a modalidade.
        demanda_ponta = demanda_fora = 0.0
        dem_contr_ponta = dem_contr_fora = 0.0
        dem_med_unica = 150.65
        dem_contr_unica = 260.0

        if mostrar_posto:
            st.markdown("**Demanda da tarifa AZUL (por posto, kW)**")
            c1, c2 = st.columns(2)
            demanda_ponta = c1.number_input(
                "Demanda Medida Ponta (kW)", min_value=0.0, value=150.65
            )
            demanda_fora = c2.number_input(
                "Demanda Medida Fora Ponta (kW)", min_value=0.0, value=0.0
            )
            c1, c2 = st.columns(2)
            dem_contr_ponta = c1.number_input(
                "Demanda Contratada Ponta (kW)", min_value=0.0, value=0.0
            )
            dem_contr_fora = c2.number_input(
                "Demanda Contratada Fora Ponta (kW)", min_value=0.0, value=0.0
            )

        if mostrar_unica:
            st.markdown("**Demanda da tarifa VERDE (única, kW)**")
            c1, c2 = st.columns(2)
            dem_med_unica = c1.number_input(
                "Demanda Medida única (kW)", min_value=0.0, value=150.65
            )
            dem_contr_unica = c2.number_input(
                "Demanda Contratada única (kW)", min_value=0.0, value=260.0
            )

        st.markdown("**Adicionais**")
        st.markdown(
            '<span style="color:green">●</span> Verde &nbsp;&nbsp; '
            '<span style="color:#e6b800">●</span> Amarela &nbsp;&nbsp; '
            '<span style="color:red">●</span> Vermelha P1 &nbsp;&nbsp; '
            '<span style="color:#8b0000">●</span> Vermelha P2',
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        bandeira_selecionada = c1.selectbox(
            "Bandeira tarifária",
            ["Automática (bandeira do mês)", "Verde", "Amarela",
             "Vermelha P1", "Vermelha P2"],
            index=0,
        )
        cip = c2.number_input("CIP/COSIP (R$)", min_value=0.0, value=0.0)
        outros = c3.number_input("Outros valores (R$)", min_value=0.0, value=115.01)

        st.markdown("**Reativos**")
        c1, c2, c3, c4 = st.columns(4)
        reat_e_ponta = c1.number_input(
            "Reativo energia Ponta (kVArh)", min_value=0.0, value=0.0
        )
        reat_e_fora = c2.number_input(
            "Reativo energia Fora Ponta (kVArh)", min_value=0.0, value=0.0
        )
        reat_d_ponta = c3.number_input(
            "Reativo demanda Ponta (kVAr)", min_value=0.0, value=0.0
        )
        reat_d_fora = c4.number_input(
            "Reativo demanda Fora Ponta (kVAr)", min_value=0.0, value=0.0
        )

        percentual_mes_anterior = st.slider(
            "% consumo mês anterior (rateio entre leituras)",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
        )

        submitted = st.form_submit_button("Calcular", type="primary")

    if not submitted:
        return None

    return {
        "distribuidora": distribuidora,
        "subgrupo": subgrupo,
        "classe": classe,
        "subclasse": subclasse,
        "detalhe": detalhe,
        "data_referencia": data_referencia.isoformat(),
        "consumo_ponta_kwh": consumo_ponta,
        "consumo_fora_ponta_kwh": consumo_fora,
        "demanda_ponta_kw": demanda_ponta,
        "demanda_fora_ponta_kw": demanda_fora,
        "demanda_contratada_ponta_kw": dem_contr_ponta,
        "demanda_contratada_fora_ponta_kw": dem_contr_fora,
        "demanda_medida_unica_kw": dem_med_unica,
        "demanda_contratada_unica_kw": dem_contr_unica,
        "percentual_mes_anterior": percentual_mes_anterior,
        "bandeira_selecionada": bandeira_selecionada,
        "cip_cosip_rs": cip,
        "outros_rs": outros,
        "reativo_energia_ponta_kvArh": reat_e_ponta,
        "reativo_energia_fora_ponta_kvArh": reat_e_fora,
        "reativo_demanda_ponta_kvAr": reat_d_ponta,
        "reativo_demanda_fora_ponta_kvAr": reat_d_fora,
    }


def formulario_tributos() -> dict:
    """Parâmetros de tributos (query params da API)."""
    with st.expander("Tributos (opcional)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        aplicar = c1.checkbox("Aplicar PIS/COFINS/ICMS", value=False)
        pis = c2.number_input("PIS (fração)", 0.0, 1.0, 0.0095, format="%.4f")
        cofins = c3.number_input("COFINS (fração)", 0.0, 1.0, 0.0438, format="%.4f")
        icms = c4.number_input("ICMS (fração)", 0.0, 1.0, 0.18, format="%.4f")
        tipo_icms = c1.selectbox("Tipo de ICMS", ["fora", "dentro"], index=0)

    return {
        "aplicar_tributos": aplicar,
        "pis": pis,
        "cofins": cofins,
        "icms": icms,
        "tipo_icms": tipo_icms,
    }


def render_linhas_fatura(fatura: dict) -> None:
    """Mostra as linhas da fatura em tabela + totais."""
    linhas = fatura.get("linhas", [])
    if linhas:
        st.dataframe(
            [
                {
                    "Descrição": l["descricao"],
                    "Categoria": l["categoria"],
                    "Quantidade": l["quantidade"],
                    "Tarifa (R$)": l["tarifa"],
                    "Custo (R$)": l["custo"],
                }
                for l in linhas
            ],
            use_container_width=True,
            hide_index=True,
        )
    c1, c2, c3 = st.columns(3)
    c1.metric("Custo tarifas (R$)", f"{fatura.get('custo_tarifas', 0.0):,.2f}")
    c2.metric("Custo total (R$)", f"{fatura.get('custo_total', 0.0):,.2f}")
    c3.metric("Tarifas não mapeadas", fatura.get("tarifas_nao_mapeadas", 0))


def render_bandeira_usada(competencia: str) -> None:
    """Mostra qual bandeira foi considerada para a competência."""
    dados = buscar_bandeira(competencia)
    if dados is None:
        return
    if "erro" in dados:
        st.warning(dados["erro"])
        return
    if dados.get("bandeira") is None:
        st.info(f"Bandeira para {competencia}: sem bandeira (anterior a jan/2015).")
        return
    st.info(
        f"Bandeira vigente em {competencia}: **{dados['bandeira']}** "
        f"({dados['valor_kwh']:.6f} R$/kWh)."
    )
