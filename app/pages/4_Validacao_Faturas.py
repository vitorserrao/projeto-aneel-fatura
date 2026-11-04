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


def _parcelas(caso: dict):
    from core.tarifas import ParcelaTarifaria

    parcelas = []
    for t in caso["tarifas_liquidas"]:
        if t["componente"] == "REATIVO":
            continue
        unidade = t["unidade"]
        valor = t["valor"]
        if unidade == "R$/kWh":
            unidade = "R$/MWh"
            valor = valor * 1000
        parcelas.append(
            ParcelaTarifaria(t["componente"], t["grandeza"], t["posto"], unidade, valor)
        )
    return parcelas


def _tarifa_reativo(caso: dict) -> float | None:
    for t in caso["tarifas_liquidas"]:
        if t["componente"] == "REATIVO":
            return float(t["valor"])
    return None


def _consumidor(caso: dict):
    from core.models import Consumidor

    p = caso["perfil"]
    return Consumidor(
        distribuidora=caso["meta"]["distribuidora"],
        subgrupo=caso["meta"]["subgrupo"],
        classe="Não se aplica",
        subclasse="Não se aplica",
        detalhe="Não se aplica",
        data_referencia=date.fromisoformat(p["data_referencia"]),
        consumo_ponta_kwh=p.get("consumo_ponta_kwh", 0.0),
        consumo_fora_ponta_kwh=p.get("consumo_fora_ponta_kwh", 0.0),
        consumo_intermediario_kwh=p.get("consumo_intermediario_kwh", 0.0),
        demanda_ponta_kw=p.get("demanda_ponta_kw", 0.0),
        demanda_fora_ponta_kw=p.get("demanda_fora_ponta_kw", 0.0),
        demanda_contratada_ponta_kw=p.get("demanda_contratada_ponta_kw", 0.0),
        demanda_contratada_fora_ponta_kw=p.get("demanda_contratada_fora_ponta_kw", 0.0),
        demanda_medida_unica_kw=p.get("demanda_medida_unica_kw", 0.0),
        demanda_contratada_unica_kw=p.get("demanda_contratada_unica_kw", 0.0),
        reativo_energia_ponta_kvArh=p.get("reativo_energia_ponta_kvArh", 0.0),
        reativo_energia_fora_ponta_kvArh=p.get("reativo_energia_fora_ponta_kvArh", 0.0),
        reativo_demanda_ponta_kvAr=p.get("reativo_demanda_ponta_kvAr", 0.0),
        reativo_demanda_fora_ponta_kvAr=p.get("reativo_demanda_fora_ponta_kvAr", 0.0),
        cip_cosip_rs=p.get("cip_cosip_rs", 0.0),
        outros_rs=p.get("outros_rs", 0.0),
        bandeira_adicional_r_kwh=p.get("bandeira_adicional_r_kwh", 0.0),
    )


def _camada1(caso: dict) -> dict[str, float]:
    from core.motor_calculo import calcular_fatura

    trib = caso["tributos"]
    rt = _tarifa_reativo(caso)
    fatura = calcular_fatura(
        _consumidor(caso),
        caso["meta"]["modalidade"],
        _parcelas(caso),
        demanda_unica=caso["meta"]["modalidade"] == "Verde",
        aplicar_tributos=True,
        pis=trib["pis"],
        cofins=trib["cofins"],
        icms=trib["icms"],
        tipo_icms=trib["tipo_icms"],
        reativos_direto=rt is not None,
        tarifa_reativo_energia_r_kvarh=rt,
        arredondar_centavos=True,
        demanda_isenta_icms=True,
        demanda_isenta_icms_kw=caso["perfil"].get("demanda_isenta_icms_kw"),
        tributar_reativos=True,
    )
    return {l.descricao: round(l.custo, 2) for l in fatura.linhas}


def _comparar_esperadas(linhas_motor: dict[str, float], caso: dict) -> list[dict]:
    linhas = []
    for e in caso["linhas_esperadas"]:
        d = e["descricao"].lower()
        alvo = None
        if "te ponta" in d:
            alvo = next((v for k, v in linhas_motor.items() if "TE ENERGIA PONTA" in k), None)
        elif "te f ponta" in d or "te f. ponta" in d:
            alvo = next((v for k, v in linhas_motor.items() if "TE ENERGIA FORA PONTA" in k), None)
        elif "usd ponta" in d:
            alvo = next((v for k, v in linhas_motor.items() if "TUSD ENERGIA PONTA" in k), None)
        elif "usd f ponta" in d:
            alvo = next((v for k, v in linhas_motor.items() if "TUSD ENERGIA FORA PONTA" in k), None)
        elif "demanda" in d and "reativ" not in d:
            alvo = sum(v for k, v in linhas_motor.items() if "TUSD DEMANDA" in k)
        elif "reativ" in d and "demanda" not in d:
            alvo = sum(v for k, v in linhas_motor.items() if "REATIVA" in k.upper() or "REATIVO" in k.upper())
        elif "ilum" in d or "cip" in d or "cosip" in d:
            alvo = sum(v for k, v in linhas_motor.items() if "CIP" in k.upper() or "ENCARGO" in k.upper())
        valor = e["valor"]
        delta = round(valor - alvo, 2) if alvo is not None else None
        linhas.append(
            {
                "Linha": e["descricao"],
                "Fatura (R$)": valor,
                "Motor (R$)": alvo,
                "Δ (R$)": delta,
                "Status": "✅" if delta is not None and abs(delta) <= 0.05 else ("⚠️" if delta is not None else "—"),
            }
        )
    return linhas


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

linhas_motor = _camada1(caso)
total_motor = sum(linhas_motor.values())
st.metric("Total motor (camada 1)", f"R$ {total_motor:,.2f}",
          delta=f"R$ {total_motor - meta['total_fatura']:,.2f} vs fatura")

linhas = _comparar_esperadas(linhas_motor, caso)
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
