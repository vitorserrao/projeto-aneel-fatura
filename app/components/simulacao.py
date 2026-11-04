"""Componentes compartilhados das páginas de simulação (Streamlit).

Camada de APRESENTAÇÃO apenas: monta o formulário do perfil do consumidor e
chama a API FastAPI por HTTP. Nenhuma regra de negócio vive aqui.
"""

from __future__ import annotations

import os
from datetime import date

import requests
import streamlit as st

from app.components.ui import grafico_pizza

API_BASE = os.environ.get("ANEEL_API_BASE", "http://127.0.0.1:8000/api")

SUBGRUPOS = ["A1", "A2", "A3", "A3a", "A4", "AS", "B1", "B2", "B3", "B4"]

CASO_ARTIGO_ERIAC = {
    "distribuidora": "CPFL-PIRATININGA",
    "subgrupo": "A4",
    "classe": "Não se aplica",
    "subclasse": "Não se aplica",
    "detalhe": "Não se aplica",
    "data_referencia": date(2018, 5, 28),
    "consumo_ponta_kwh": 8849.85,
    "consumo_fora_ponta_kwh": 68276.07,
    "demanda_ponta_kw": 283.27,
    "demanda_fora_ponta_kw": 283.27,
    "demanda_contratada_ponta_kw": 200.0,
    "demanda_contratada_fora_ponta_kw": 200.0,
    "demanda_medida_unica_kw": 283.27,
    "demanda_contratada_unica_kw": 200.0,
    "percentual_mes_anterior": 0.0,
    "bandeira_selecionada": "Automática (bandeira do mês)",
    "cip_cosip_rs": 60.0,
    "outros_rs": 0.0,
    "reativo_energia_ponta_kvArh": 0.0,
    "reativo_energia_fora_ponta_kvArh": 39.36,
    "reativo_demanda_ponta_kvAr": 0.0,
    "reativo_demanda_fora_ponta_kvAr": 0.0,
    "reativo_energia_capacitiva_kvArh": 0.0,
    "reativo_demanda_capacitiva_kvAr": 0.0,
    "reativos_direto": True,
    "tarifa_reativo_automatica": False,
    "tarifa_reativo_energia_r_kvarh": 0.28209,  # TE B1 Residencial/1000 (calculada)
    "tarifa_reativo_demanda_r_kvar": 9.90,  # VRDRE = TUSD demanda Azul Fora Ponta A4 (calculada)
    "tributos": {
        "aplicar_tributos": True,
        "pis": 0.0135,
        "cofins": 0.062,
        "icms": 0.18,
        "tipo_icms": "dentro",
    },
}


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
    caso = st.session_state.get("caso_pronto") or {}
    mostrar_posto = modalidade in (None, "Azul")
    mostrar_unica = modalidade in (None, "Verde")
    with st.form(prefixo):
        tab_cons, tab_dem, tab_opt, tab_adic = st.tabs(
            ["Consumidor", "Consumo e Demanda", "Optante B (art. 292)", "Adicionais e Reativos"]
        )

        with tab_cons:
                    st.markdown("**Dados da unidade consumidora**")
                    c1, c2, c3 = st.columns(3)
                    distribuidora = c1.text_input(
                        "Distribuidora (sig_agente)", value=caso.get("distribuidora", "COPEL-DIS")
                    )
                    subgrupo = c2.selectbox(
                        "Subgrupo", SUBGRUPOS, index=SUBGRUPOS.index(caso.get("subgrupo", "A4"))
                    )
                    classe = c3.text_input(
                        "Classe",
                        value=caso.get("classe", "Não se aplica"),
                        help="No Grupo B (Optante B/Convencional/Branca), a classe "
                        "filtra a tarifa (ex.: Residencial, Comercial, Rural).",
                    )

                    c1, c2, c3 = st.columns(3)
                    subclasse = c1.text_input(
                        "Subclasse",
                        value=caso.get("subclasse", "Não se aplica"),
                        help="No Grupo B, a subclasse filtra a tarifa (ex.: "
                        "Residencial, Residencial Baixa Renda).",
                    )
                    detalhe = c2.text_input("Detalhe", value=caso.get("detalhe", "Não se aplica"))
                    data_referencia = c3.date_input(
                        "Data de referência", value=caso.get("data_referencia", date(2023, 3, 15))
                    )

        with tab_dem:
                    st.markdown("**Consumo (kWh)**")
                    c1, c2 = st.columns(2)
                    consumo_ponta = c1.number_input(
                        "Consumo Ponta (kWh)", min_value=0.0, value=caso.get("consumo_ponta_kwh", 55.0)
                    )
                    consumo_fora = c2.number_input(
                        "Consumo Fora Ponta (kWh)", min_value=0.0, value=caso.get("consumo_fora_ponta_kwh", 9094.0)
                    )
                    consumo_intermediario = c3.number_input(
                        "Consumo Intermediário (kWh)", min_value=0.0, value=caso.get("consumo_intermediario_kwh", 0.0)
                    )

                    # Defaults do caso pronto (ou neutros); preenchidos conforme a modalidade.
                    demanda_ponta = caso.get("demanda_ponta_kw", 0.0)
                    demanda_fora = caso.get("demanda_fora_ponta_kw", 0.0)
                    dem_contr_ponta = caso.get("demanda_contratada_ponta_kw", 0.0)
                    dem_contr_fora = caso.get("demanda_contratada_fora_ponta_kw", 0.0)
                    dem_med_unica = caso.get("demanda_medida_unica_kw", 150.65)
                    dem_contr_unica = caso.get("demanda_contratada_unica_kw", 260.0)
                    demanda_isenta_kw = caso.get("demanda_isenta_icms_kw", 0.0)

                    if mostrar_posto:
                        st.markdown("**Demanda da tarifa AZUL (por posto, kW)**")
                        c1, c2 = st.columns(2)
                        demanda_ponta = c1.number_input(
                            "Demanda Medida Ponta (kW)", min_value=0.0, value=caso.get("demanda_ponta_kw", 150.65)
                        )
                        demanda_fora = c2.number_input(
                            "Demanda Medida Fora Ponta (kW)", min_value=0.0, value=caso.get("demanda_fora_ponta_kw", 0.0)
                        )
                        c1, c2 = st.columns(2)
                        dem_contr_ponta = c1.number_input(
                            "Demanda Contratada Ponta (kW)", min_value=0.0, value=caso.get("demanda_contratada_ponta_kw", 0.0)
                        )
                        dem_contr_fora = c2.number_input(
                            "Demanda Contratada Fora Ponta (kW)", min_value=0.0, value=caso.get("demanda_contratada_fora_ponta_kw", 0.0)
                        )
                        demanda_isenta_kw = st.number_input(
                            "Demanda isenta de ICMS (kW) — opcional (0 = sem isenção)",
                            min_value=0.0,
                            value=caso.get("demanda_isenta_icms_kw", 0.0),
                        )

                    if mostrar_unica:
                        st.markdown("**Demanda da tarifa VERDE (única, kW)**")
                        c1, c2 = st.columns(2)
                        dem_med_unica = c1.number_input(
                            "Demanda Medida única (kW)", min_value=0.0, value=caso.get("demanda_medida_unica_kw", 150.65)
                        )
                        dem_contr_unica = c2.number_input(
                            "Demanda Contratada única (kW)", min_value=0.0, value=caso.get("demanda_contratada_unica_kw", 260.0)
                        )
                        demanda_isenta_kw = st.number_input(
                            "Demanda isenta de ICMS (kW) — opcional (0 = sem isenção)",
                            min_value=0.0,
                            value=caso.get("demanda_isenta_icms_kw", 0.0),
                        )

        with tab_opt:
                    st.markdown("**Optante B — Grupo A faturado como Grupo B (art. 292)**")
                    st.caption(
                        "Você não precisa informar a categoria: a classe do Grupo B é "
                        "derivada da atividade (Residencial → B1/Residencial; Rural → "
                        "B2/Rural). Para Comercial/Industrial (B3) informe a Classe na "
                        "aba Consumidor — sem ela e com tarifas ambíguas, o cálculo é "
                        "recusado com aviso (nunca soma tarifas diferentes)."
                    )
                    c1, c2, c3 = st.columns(3)
                    atividades = [
                        "Comercial ou Industrial",
                        "Rural",
                        "Residencial",
                        "Esportivo ou Parque Agropecuário",
                    ]
                    atividade = c1.selectbox(
                        "Atividade econômica",
                        atividades,
                        index=atividades.index(caso.get("atividade", "Comercial ou Industrial")),
                    )
                    potencia_transformadores = c2.number_input(
                        "Potência dos transformadores (kVA)",
                        min_value=0.0,
                        value=caso.get("potencia_transformadores_kva", 0.0),
                    )
                    tipos_ligacao = ["Trifásico", "Bifásico", "Monofásico"]
                    tipo_ligacao = c3.selectbox(
                        "Tipo de ligação",
                        tipos_ligacao,
                        index=tipos_ligacao.index(caso.get("tipo_ligacao", "Trifásico")),
                    )
                    cooperativa = st.checkbox(
                        "Cooperativa de eletrificação rural",
                        value=caso.get("cooperativa_eletrificacao_rural", False),
                    )
                    hotelaria = st.checkbox(
                        "Hotelaria/pousada em área de veraneio ou turismo",
                        value=caso.get("hotelaria_turismo", False),
                    )
                    pre_pagamento = st.checkbox(
                        "Pré-pagamento",
                        value=caso.get("pre_pagamento", False),
                    )
                    c1, c2 = st.columns(2)
                    carga_refletores = c1.number_input(
                        "Carga dos refletores (kW)",
                        min_value=0.0,
                        value=caso.get("carga_refletores_kw", 0.0),
                    )
                    carga_total = c2.number_input(
                        "Carga instalada total (kW)",
                        min_value=0.0,
                        value=caso.get("carga_instalada_total_kw", 0.0),
                    )

        with tab_adic:
                    st.markdown("**Adicionais**")
                    st.markdown(
                        '<span style="color:green">●</span> Verde &nbsp;&nbsp; '
                        '<span style="color:#e6b800">●</span> Amarela &nbsp;&nbsp; '
                        '<span style="color:red">●</span> Vermelha P1 &nbsp;&nbsp; '
                        '<span style="color:#8b0000">●</span> Vermelha P2',
                        unsafe_allow_html=True,
                    )
                    c1, c2, c3 = st.columns(3)
                    opcoes_bandeira = ["Automática (bandeira do mês)", "Verde", "Amarela",
                                       "Vermelha P1", "Vermelha P2"]
                    bandeira_selecionada = c1.selectbox(
                        "Bandeira tarifária",
                        opcoes_bandeira,
                        index=opcoes_bandeira.index(caso.get("bandeira_selecionada", "Automática (bandeira do mês)")),
                    )
                    cip = c2.number_input("CIP/COSIP (R$)", min_value=0.0, value=caso.get("cip_cosip_rs", 0.0))
                    outros = c3.number_input("Outros valores (R$)", min_value=0.0, value=caso.get("outros_rs", 115.01))

                    st.markdown("**Reativos excedentes**")
                    st.markdown(
                        "Informe o excedente já calculado (faturas antigas) e o preço das "
                        "tarifas diretas."
                    )
                    c1, c2 = st.columns(2)
                    reat_e_ponta = c1.number_input(
                        "Consumo de Energia Reativa Excedente — Ponta (kVArh)",
                        min_value=0.0, value=caso.get("reativo_energia_ponta_kvArh", 0.0),
                    )
                    reat_e_fora = c2.number_input(
                        "Consumo de Energia Reativa Excedente — Fora de Ponta (kVArh)",
                        min_value=0.0, value=caso.get("reativo_energia_fora_ponta_kvArh", 0.0),
                    )
                    c1, c2 = st.columns(2)
                    reat_d_ponta = c1.number_input(
                        "Demanda de Potência Reativa Excedente — Ponta (kVAr)",
                        min_value=0.0, value=caso.get("reativo_demanda_ponta_kvAr", 0.0),
                    )
                    reat_d_fora = c2.number_input(
                        "Demanda de Potência Reativa Excedente — Fora de Ponta (kVAr)",
                        min_value=0.0, value=caso.get("reativo_demanda_fora_ponta_kvAr", 0.0),
                    )
                    tarifa_reat_automatica = st.checkbox(
                        "Buscar tarifa de reativo automaticamente (VRERE/VRDRE do art. 304)",
                        value=caso.get("tarifa_reativo_automatica", True),
                    )
                    tarifa_reat_energia = None
                    tarifa_reat_demanda = None
                    if not tarifa_reat_automatica:
                        c1, c2 = st.columns(2)
                        tarifa_reat_energia = c1.number_input(
                            "Tarifa — Consumo de Energia Reativa Excedente (R$/kVArh)",
                            min_value=0.0,
                            value=caso.get("tarifa_reativo_energia_r_kvarh", 0.0),
                            format="%.6f",
                        )
                        tarifa_reat_demanda = c2.number_input(
                            "Tarifa — Demanda de Potência Reativa Excedente (R$/kVAr)",
                            min_value=0.0,
                            value=caso.get("tarifa_reativo_demanda_r_kvar", 0.0),
                            format="%.6f",
                        )
                    reativos_direto = True

                    percentual_mes_anterior = st.slider(
                        "% consumo mês anterior (rateio entre leituras)",
                        min_value=0.0,
                        max_value=1.0,
                        value=caso.get("percentual_mes_anterior", 0.0),
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
        "reativo_energia_capacitiva_kvArh": 0.0,
        "reativo_demanda_capacitiva_kvAr": 0.0,
        # Parâmetros de query (removidos pelas páginas antes do POST):
        "reativos_direto": reativos_direto,
        "tarifa_reativo_energia_r_kvarh": tarifa_reat_energia,
        "tarifa_reativo_demanda_r_kvar": tarifa_reat_demanda,
        "consumo_intermediario_kwh": consumo_intermediario,
        "tipo_ligacao": tipo_ligacao,
        "pre_pagamento": pre_pagamento,
        "demanda_isenta_icms": demanda_isenta_kw > 0,
        "demanda_isenta_icms_kw": demanda_isenta_kw if demanda_isenta_kw > 0 else None,
        "tarifa_reativo_automatica": tarifa_reat_automatica,
        "atividade": atividade,
        "potencia_transformadores_kva": potencia_transformadores,
        "cooperativa_eletrificacao_rural": cooperativa,
        "hotelaria_turismo": hotelaria,
        "carga_refletores_kw": carga_refletores,
        "carga_instalada_total_kw": carga_total,
    }


def extrair_reativos_params(perfil: dict) -> dict:
    """Remove do payload os parâmetros de reativos e devolve como query params.

    Só inclui as chaves relevantes (evita enviar ``None`` para a API).
    """
    params: dict = {}
    if perfil.pop("reativos_direto", False):
        params["reativos_direto"] = True
    energia = perfil.pop("tarifa_reativo_energia_r_kvarh", None)
    demanda = perfil.pop("tarifa_reativo_demanda_r_kvar", None)
    if energia is not None:
        params["tarifa_reativo_energia_r_kvarh"] = energia
    if demanda is not None:
        params["tarifa_reativo_demanda_r_kvar"] = demanda
    perfil.pop("tarifa_reativo_automatica", None)
    isenta_kw = perfil.pop("demanda_isenta_icms_kw", None)
    if perfil.pop("demanda_isenta_icms", False):
        params["demanda_isenta_icms"] = True
    if isenta_kw:
        params["demanda_isenta_icms_kw"] = isenta_kw
    return params


def formulario_tributos() -> dict:
    """Parâmetros de tributos (query params da API)."""
    with st.expander("Tributos (opcional)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        trib = (st.session_state.get("caso_pronto") or {}).get("tributos", {})
        aplicar = c1.checkbox("Aplicar PIS/COFINS/ICMS", value=trib.get("aplicar_tributos", False))
        pis = c2.number_input("PIS (fração)", 0.0, 1.0, trib.get("pis", 0.0095), format="%.4f")
        cofins = c3.number_input("COFINS (fração)", 0.0, 1.0, trib.get("cofins", 0.0438), format="%.4f")
        icms = c4.number_input("ICMS (fração)", 0.0, 1.0, trib.get("icms", 0.18), format="%.4f")
        opcoes_icms = ["fora", "dentro"]
        tipo_icms = c1.selectbox("Tipo de ICMS", opcoes_icms, index=opcoes_icms.index(trib.get("tipo_icms", "fora")))

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
    c_graf1, c_graf2 = st.columns(2)
    with c_graf1:
        render_grafico_te_tusd(fatura)
    with c_graf2:
        categorias: dict[str, float] = {}
        for l in linhas:
            cat = l.get("categoria") or "OUTROS"
            categorias[cat] = categorias.get(cat, 0.0) + float(l.get("custo", 0.0))
        if categorias:
            grafico_pizza(
                list(categorias.keys()),
                [round(v, 2) for v in categorias.values()],
                "Custo por categoria",
            )

    c1, c2, c3 = st.columns(3)
    c1.metric("Custo tarifas (R$)", f"{fatura.get('custo_tarifas', 0.0):,.2f}")
    c2.metric("Custo total (R$)", f"{fatura.get('custo_total', 0.0):,.2f}")
    c3.metric("Tarifas não mapeadas", fatura.get("tarifas_nao_mapeadas", 0))


def render_grafico_te_tusd(fatura: dict) -> None:
    """Gráfico de barras TE × TUSD por posto (custo em R$)."""
    import pandas as pd

    linhas = fatura.get("linhas", [])
    dados: dict[tuple[str, str], float] = {}
    ordem_postos = {"Ponta": 0, "Intermediário": 1, "Fora Ponta": 2, "Outros": 3}
    for l in linhas:
        d = (l.get("descricao") or "").upper()
        if d.startswith("TE ") or " TE " in d:
            comp = "TE"
        elif "TUSD" in d:
            comp = "TUSD"
        else:
            continue
        if "INTERMEDI" in d:
            posto = "Intermediário"
        elif "FORA" in d:
            posto = "Fora Ponta"
        elif "PONTA" in d:
            posto = "Ponta"
        else:
            posto = "Outros"
        dados[(posto, comp)] = dados.get((posto, comp), 0.0) + float(l.get("custo", 0.0))
    if not dados:
        return
    postos = sorted({k[0] for k in dados}, key=lambda p: ordem_postos.get(p, 9))
    df = pd.DataFrame(
        [
            {
                "Posto": p,
                "TE (R$)": round(dados.get((p, "TE"), 0.0), 2),
                "TUSD (R$)": round(dados.get((p, "TUSD"), 0.0), 2),
            }
            for p in postos
        ]
    ).set_index("Posto")
    st.markdown("**TE × TUSD por posto**")
    st.bar_chart(df)


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
