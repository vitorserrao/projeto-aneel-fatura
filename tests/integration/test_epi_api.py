"""Teste de integração do endpoint /api/epi/calcular.

Valida o serviço de PI de ponta a ponta (repo → EPIService → core) usando o
caso CELESC A4 Azul do TCC:
- data 2025-12-01 (ciclo tarifário 2025-08-22..2025-12-31) → PI ≈ 318,20;
- data 2025-08-01 (ciclo 2024-08-22..2025-08-21, o usado pelo TCC) → 302,20.
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


def _payload(**overrides):
    payload = dict(
        distribuidora="CELESC",
        subgrupo="A4",
        data_referencia="2025-12-01",
        modalidade="Azul",
        consumo_ponta_kwh=1_425_830.0,  # 1.425,83 MWh
        consumo_fora_ponta_kwh=14_125_160.0,  # 14.125,16 MWh
        pis=0.0067,
        cofins=0.0307,
        icms=0.17,
        k=0.03,
        encargos=3.0,
        opex_mensal=0.0,
        capex=0.0,
        horizonte_meses=60,
    )
    payload.update(overrides)
    return payload


def test_epi_celesc_dez2025(banco):
    resposta = client.post("/api/epi/calcular", json=_payload())

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["pi"] == pytest.approx(318.20, abs=0.01)
    assert corpo["modalidade"] == "AZUL"
    assert corpo["e_mwh"] == pytest.approx(1425.83 + 14125.16, abs=0.01)


def test_epi_celesc_vigencia_anterior_reproduz_tcc(banco):
    resposta = client.post(
        "/api/epi/calcular", json=_payload(data_referencia="2025-08-01")
    )

    assert resposta.status_code == 200
    assert resposta.json()["pi"] == pytest.approx(302.20, abs=0.01)


def test_epi_modalidade_invalida_retorna_400(banco):
    resposta = client.post(
        "/api/epi/calcular", json=_payload(modalidade="Branca")
    )

    assert resposta.status_code == 400


def test_comparar_modalidades_inclui_pi_por_modalidade(banco):
    perfil = {
        "distribuidora": "CELESC",
        "subgrupo": "A4",
        "classe": "Não se aplica",
        "detalhe": "Não se aplica",
        "data_referencia": "2025-12-01",
        "consumo_ponta_kwh": 1_425_830.0,  # 1.425,83 MWh
        "consumo_fora_ponta_kwh": 14_125_160.0,  # 14.125,16 MWh
    }
    params = {
        "pis": 0.0067,
        "cofins": 0.0307,
        "icms": 0.17,
        "k": 0.03,
        "encargos": 3.0,
    }
    resposta = client.post(
        "/api/calculo/comparar", json=perfil, params=params
    )

    assert resposta.status_code == 200, resposta.text
    disponiveis = resposta.json()["comparacao"]["disponiveis"]
    por_modalidade = {d["modalidade"]: d for d in disponiveis}

    assert "Azul" in por_modalidade
    assert "Verde" in por_modalidade
    assert por_modalidade["Azul"]["pi"] == pytest.approx(318.20, abs=0.01)
    assert por_modalidade["Verde"]["pi"] is not None
