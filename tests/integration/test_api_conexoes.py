"""Regressão: a API não pode esgotar as conexões do PostgreSQL.

Cada dependência da API criava uma ``Engine`` nova (``create_session_factory()``
sem argumento) a cada request. Como cada engine tem o próprio pool e nunca é
descartada, o ``max_connections`` do PostgreSQL estoura depois de poucos
cálculos — o front dispara ~10 requests por análise:

    FATAL: sorry, too many clients already   → HTTP 500

A correção usa a session factory compartilhada (``get_session_factory``). Este
teste falha se alguém voltar a criar uma engine por request.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from infra.database import create_db_engine, get_engine, get_session_factory, ping_db

client = TestClient(app)


@pytest.fixture(scope="module")
def banco():
    eng = create_db_engine()
    try:
        ping_db(eng)
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"PostgreSQL nao disponivel: {exc}")
    return True


def test_session_factory_e_compartilhada():
    """A mesma factory (e a mesma engine) em todas as chamadas."""
    assert get_session_factory() is get_session_factory()
    assert get_engine() is get_engine()
    assert get_session_factory().kw["bind"] is get_engine()


def test_routers_usam_a_factory_compartilhada():
    """As dependências dos 4 routers apontam para a factory compartilhada."""
    from api.routers.calculo import _calculo_service, _epi_service
    from api.routers.epi import _epi_service as _epi_service_router
    from api.routers.planejamento import _planejamento_service
    from api.routers.tarifas import repo_dependency

    repos = [
        _calculo_service()._repo,
        _epi_service()._repo,
        _epi_service_router()._repo,
        _planejamento_service()._calculo._repo,
        repo_dependency(),
    ]
    for repo in repos:
        assert repo._session_factory is get_session_factory()


def test_muitos_requests_nao_esgotam_conexoes(banco):
    """30 cálculos seguidos (como 3 análises do front) sem nenhum 500."""
    payload = {
        "distribuidora": "COPEL-DIS",
        "subgrupo": "A4",
        "data_referencia": "2023-03-15",
        "consumo_ponta_kwh": 55,
        "consumo_fora_ponta_kwh": 9094,
        "demanda_medida_unica_kw": 150.65,
        "demanda_contratada_unica_kw": 260,
    }
    params = {
        "modalidade": "Verde",
        "aplicar_tributos": True,
        "pis": 0.0095,
        "cofins": 0.0438,
        "icms": 0.18,
        "tipo_icms": "fora",
        "arredondar_centavos": True,
        "demanda_isenta_icms": True,
        "demanda_isenta_icms_kw": 109.35,
    }

    status = []
    for _ in range(30):
        status.append(
            client.post("/api/calculo/fatura", json=payload, params=params).status_code
        )

    assert set(status) == {200}, f"status inesperados: {sorted(set(status))}"
