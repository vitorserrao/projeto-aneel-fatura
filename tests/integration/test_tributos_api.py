"""Teste de integração dos tributos via API (endpoint /api/calculo/fatura)."""

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


def _perfil():
    return {
        "distribuidora": "CPFL JAGUARI",
        "subgrupo": "A2",
        "classe": "Não se aplica",
        "detalhe": "Não se aplica",
        "data_referencia": "2010-06-01",
        "consumo_ponta_kwh": 100_000.0,
        "consumo_fora_ponta_kwh": 900_000.0,
        "demanda_ponta_kw": 1_000.0,
        "demanda_fora_ponta_kw": 2_000.0,
        "demanda_contratada_ponta_kw": 1_200.0,
        "demanda_contratada_fora_ponta_kw": 1_500.0,
    }


def test_fatura_com_tributos(banco):
    # Sem tributos.
    r_base = client.post(
        "/api/calculo/fatura",
        json=_perfil(),
        params={"modalidade": "Azul"},
    )
    assert r_base.status_code == 200, r_base.text
    total_liq = r_base.json()["fatura"]["custo_total"]

    # Com tributos (fórmula aditiva): fator esperado
    pis, cofins, icms = 0.0065, 0.03, 0.18
    fator = 1.0 / (1.0 - pis - cofins - icms)

    r_com = client.post(
        "/api/calculo/fatura",
        json=_perfil(),
        params={
            "modalidade": "Azul",
            "aplicar_tributos": True,
            "pis": pis,
            "cofins": cofins,
            "icms": icms,
            "tipo_icms": "dentro",
        },
    )
    assert r_com.status_code == 200, r_com.text
    fatura = r_com.json()["fatura"]
    assert fatura["aplicar_tributos"] is True
    # Apenas as linhas TARIFA escalam; encargos fixos (se houver) não.
    custo_tarifas_com = fatura["custo_tarifas"]
    custo_tarifas_base = r_base.json()["fatura"]["custo_tarifas"]
    assert abs(custo_tarifas_com / custo_tarifas_base - fator) < 1e-9


def test_tributos_invalidos_retornam_422(banco):
    r = client.post(
        "/api/calculo/fatura",
        json=_perfil(),
        params={
            "modalidade": "Azul",
            "aplicar_tributos": True,
            "pis": 0.5,
            "cofins": 0.4,
            "icms": 0.2,  # soma = 1.1 > 1 -> denominador <= 0
            "tipo_icms": "dentro",
        },
    )
    assert r.status_code == 422
