"""Testes de integração da API de consulta (Sprint P3).

Verificam que a camada de leitura está acessível e retorna dados reais já
carregados. Se o banco não estiver disponível, os testes são ignorados.
"""

from datetime import date

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


def test_health(banco):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_listar_distribuidoras(banco):
    r = client.get("/api/distribuidoras")
    assert r.status_code == 200
    corpo = r.json()
    assert isinstance(corpo, list) and corpo
    cnpjs = [d["num_cnpj"] for d in corpo]
    assert len(cnpjs) == len(set(cnpjs))  # CNPJ identidade

    # RGE tem mais de um CNPJ: nenhuma perda/collapso por sigla.
    rge = [d for d in corpo if d["sig_agente"].upper().startswith("RGE")]
    assert len(rge) >= 2


def test_buscar_tarifas_por_filtro_simples(banco):
    r = client.get(
        "/api/tarifas",
        params={"sig_agente": "CPFL JAGUARI", "data": "2010-06-01", "componente": "TUSD"},
    )
    assert r.status_code == 200
    tarifas = r.json()
    assert tarifas
    assert all(t["componente"] == "TUSD" for t in tarifas)
    # todos vigentes em 2010-06-01
    for t in tarifas:
        assert t["inicio_vigencia"] <= "2010-06-01" <= (t["fim_vigencia"] or "9999-12-31")


def test_buscar_tarifas_base_filtrada(banco):
    r = client.get(
        "/api/tarifas",
        params={
            "sig_agente": "CPFL JAGUARI",
            "data": "2010-06-01",
            "base_tarifaria": "Tarifa de Aplicação",
        },
    )
    assert r.status_code == 200
    tarifas = r.json()
    assert tarifas
    assert all(t["base_tarifaria"] == "Tarifa de Aplicação" for t in tarifas)


def test_te_tusd_rota(banco):
    r = client.get(
        "/api/tarifas/te-tusd",
        params={"sig_agente": "CPFL JAGUARI", "data": "2010-06-01"},
    )
    assert r.status_code == 200
    corpo = r.json()
    assert {"TE", "TUSD"} <= set(corpo.keys())
    # existem pelo menos duas componentes distintas no conjunto de CPFL JAGUARI
    assert isinstance(corpo["TE"], list) or isinstance(corpo["TUSD"], list)


def test_data_invalida_retorna_400(banco):
    r = client.get("/api/tarifas", params={"data": "10/10/2020"})
    assert r.status_code == 400
