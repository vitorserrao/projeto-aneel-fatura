"""Teste de integração do planejamento anual (endpoint /api/planejamento/comparar).

Usa o histórico jan–dez/2023 da fatura CEMIG-D CII_112 (A4 Verde) e confere:
- o endpoint anual responde com os dois cenários, DC ótimas e PI;
- a decomposição do ganho fecha;
- o cenário "contrato atual" de dez/2023 reproduz a fatura real dentro da
  tolerância de validação (R$ 0,05 por item / R$ 1,00 no total).
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from infra.database import create_db_engine, ping_db

client = TestClient(app)


@pytest.fixture(scope="module")
def banco():
    eng = create_db_engine()
    try:
        ping_db(eng)
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"PostgreSQL nao disponivel: {exc}")
    return True


HISTORICO_2023 = [
    {"data_referencia": "2023-01-15", "d_med_ponta": 95, "d_med_fora_ponta": 98, "e_ponta_kwh": 5250, "e_fora_ponta_kwh": 44100},
    {"data_referencia": "2023-02-15", "d_med_ponta": 151, "d_med_fora_ponta": 165, "e_ponta_kwh": 6300, "e_fora_ponta_kwh": 46550},
    {"data_referencia": "2023-03-15", "d_med_ponta": 203, "d_med_fora_ponta": 207, "e_ponta_kwh": 11200, "e_fora_ponta_kwh": 68950},
    {"data_referencia": "2023-04-15", "d_med_ponta": 189, "d_med_fora_ponta": 189, "e_ponta_kwh": 8750, "e_fora_ponta_kwh": 59500},
    {"data_referencia": "2023-05-15", "d_med_ponta": 179, "d_med_fora_ponta": 168, "e_ponta_kwh": 9800, "e_fora_ponta_kwh": 59850},
    {"data_referencia": "2023-06-15", "d_med_ponta": 168, "d_med_fora_ponta": 151, "e_ponta_kwh": 9100, "e_fora_ponta_kwh": 57050},
    {"data_referencia": "2023-07-15", "d_med_ponta": 154, "d_med_fora_ponta": 140, "e_ponta_kwh": 7000, "e_fora_ponta_kwh": 51100},
    {"data_referencia": "2023-08-15", "d_med_ponta": 189, "d_med_fora_ponta": 179, "e_ponta_kwh": 9800, "e_fora_ponta_kwh": 63000},
    {"data_referencia": "2023-09-15", "d_med_ponta": 217, "d_med_fora_ponta": 238, "e_ponta_kwh": 9800, "e_fora_ponta_kwh": 64400},
    {"data_referencia": "2023-10-15", "d_med_ponta": 203, "d_med_fora_ponta": 214, "e_ponta_kwh": 10150, "e_fora_ponta_kwh": 64750},
    {"data_referencia": "2023-11-15", "d_med_ponta": 210, "d_med_fora_ponta": 231, "e_ponta_kwh": 9800, "e_fora_ponta_kwh": 68250},
    {"data_referencia": "2023-12-15", "d_med_ponta": 193, "d_med_fora_ponta": 200, "e_ponta_kwh": 7000, "e_fora_ponta_kwh": 54950},
]


def _payload_anual(**overrides):
    payload = {
        "distribuidora": "CEMIG-D",
        "subgrupo": "A4",
        "classe": "Não se aplica",
        "detalhe": "Não se aplica",
        "atividade": "Comercial ou Industrial",
        "tipo_ligacao": "Trifásico",
        "meses": HISTORICO_2023,
        "pis": 0.0078,
        "cofins": 0.0361,
        "icms": 0.18,
        "tipo_icms": "fora",
        "modalidade_atual": "Verde",
        "dc_atual_verde": 400.0,
        "dc_atual_azul_ponta": 400.0,
        "dc_atual_azul_fora": 400.0,
        "k": 0.03,
        "encargos": 3.0,
    }
    payload.update(overrides)
    return payload


def test_planejamento_anual_cemig_2023(banco):
    resposta = client.post("/api/planejamento/comparar", json=_payload_anual())

    assert resposta.status_code == 200, resposta.text
    body = resposta.json()

    assert body["melhor_contrato_atual"] in ("Azul", "Verde")
    assert body["melhor_demanda_otimizada"] in ("Azul", "Verde")
    assert body["ganho"]["total"] == pytest.approx(
        body["ganho"]["demanda"] + body["ganho"]["modalidade"]
    )

    por_modalidade = {m["modalidade"]: m for m in body["modalidades"]}
    assert por_modalidade["Verde"]["custo_contrato_atual"] > 0
    assert por_modalidade["Verde"]["dc_atual"] == 400.0
    assert por_modalidade["Verde"]["dc_otima"] >= 30.0
    assert por_modalidade["Azul"]["dc_otima"] is not None
    assert por_modalidade["Verde"]["pi"]["anual"] is not None
    assert len(por_modalidade["Verde"]["pi"]["mensal"]) == 12


def test_dezembro_2023_contrato_atual_reproduz_fatura_real(banco):
    """A fatura de dez/2023 (contrato atual, Verde) bate com a fatura real."""
    perfil = {
        "distribuidora": "CEMIG-D",
        "subgrupo": "A4",
        "classe": "Não se aplica",
        "detalhe": "Não se aplica",
        "data_referencia": "2023-12-15",
        "consumo_ponta_kwh": 7000,
        "consumo_fora_ponta_kwh": 54950,
        "demanda_medida_unica_kw": 200,
        "demanda_contratada_unica_kw": 400,
        "cip_cosip_rs": 40.45,
    }
    params = {
        "modalidade": "Verde",
        "aplicar_tributos": "true",
        "tipo_icms": "fora",
        "pis": 0.0078,
        "cofins": 0.0361,
        "icms": 0.18,
        "demanda_isenta_icms": "true",
        "demanda_isenta_icms_kw": 200,
    }
    resposta = client.post("/api/calculo/fatura", json=perfil, params=params)

    assert resposta.status_code == 200, resposta.text
    linhas = resposta.json()["fatura"]["linhas"]

    te_ponta = sum(l["custo"] for l in linhas if "TE ENERGIA PONTA" in l["descricao"])
    tusd_ponta = sum(l["custo"] for l in linhas if "TUSD ENERGIA PONTA" in l["descricao"])
    te_fora = sum(l["custo"] for l in linhas if "TE ENERGIA FORA PONTA" in l["descricao"])
    tusd_fora = sum(l["custo"] for l in linhas if "TUSD ENERGIA FORA PONTA" in l["descricao"])
    demanda = sum(l["custo"] for l in linhas if "TUSD DEMANDA" in l["descricao"])
    cip = sum(l["custo"] for l in linhas if "CIP" in l["descricao"])

    # Fatura real: HP = 17.873,59 · HFP = 28.994,44 · Demanda = 8.909,61 ·
    # CIP = 40,45 · Total = 55.818,09.
    assert te_ponta + tusd_ponta == pytest.approx(17_873.59, abs=0.05)
    assert te_fora + tusd_fora == pytest.approx(28_994.44, abs=0.05)
    assert demanda == pytest.approx(8_909.61, abs=0.05)
    assert cip == pytest.approx(40.45, abs=0.05)
    assert resposta.json()["fatura"]["custo_total"] == pytest.approx(55_818.09, abs=1.00)


def test_breakpoints_iguais_busca_exaustiva_cemig_2023(banco):
    """Pontos de quebra dão o MESMO DC/custo da busca exaustiva (Verde, motor)."""
    from dataclasses import replace
    from datetime import date

    from core.motor_calculo import calcular_fatura
    from core.models import Consumidor
    from core.planejamento import CustoDemandaMensal, custo_demanda_mensal, otimizar_contrato
    from infra.database import create_session_factory
    from infra.repositories.tarifa_repository import TarifaRepository
    from services.calculo_service import CalculoService

    repo = TarifaRepository(create_session_factory())
    calculo = CalculoService(repo)
    base = Consumidor(
        distribuidora="CEMIG-D",
        subgrupo="A4",
        classe="Não se aplica",
        detalhe="Não se aplica",
    )

    medidas_verde = [
        max(m["d_med_ponta"], m["d_med_fora_ponta"]) for m in HISTORICO_2023
    ]
    parcelas_por_mes = []
    consumidores_por_mes = []
    for m in HISTORICO_2023:
        consumidor = replace(
            base,
            data_referencia=date.fromisoformat(m["data_referencia"]),
            consumo_ponta_kwh=m["e_ponta_kwh"],
            consumo_fora_ponta_kwh=m["e_fora_ponta_kwh"],
            demanda_medida_unica_kw=medidas_verde[len(consumidores_por_mes)],
        )
        parcelas, _nao, _avisos, _du = calculo.parcelas_vigentes(
            consumidor, "Verde", "Tarifa de Aplicação"
        )
        parcelas_por_mes.append(parcelas)
        consumidores_por_mes.append(consumidor)

    def verde_fn(dc, i):
        consumidor = replace(
            consumidores_por_mes[i], demanda_contratada_unica_kw=dc
        )
        fatura = calcular_fatura(
            consumidor,
            "Verde",
            parcelas_por_mes[i],
            demanda_unica=True,
            aplicar_tributos=True,
            pis=0.0078,
            cofins=0.0361,
            icms=0.18,
            tipo_icms="fora",
        )
        detalhe = custo_demanda_mensal(medidas_verde[i], dc, 1.0)
        return CustoDemandaMensal(
            faturavel_kw=detalhe.faturavel_kw,
            ultrapassagem_kw=detalhe.ultrapassagem_kw,
            ociosidade_kw=detalhe.ociosidade_kw,
            custo=fatura.custo_total,
        )

    rapido = otimizar_contrato(medidas_verde, verde_fn)  # breakpoints
    exaustivo = otimizar_contrato(medidas_verde, verde_fn, passo=1.0)

    assert rapido.dc == exaustivo.dc
    assert rapido.custo_anual == pytest.approx(exaustivo.custo_anual)
