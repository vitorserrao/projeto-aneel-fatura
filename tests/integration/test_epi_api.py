"""Teste de integração do endpoint /api/epi/calcular.

Valida o serviço de PI de ponta a ponta (repo → EPIService → core) usando o
caso CELESC A4 Azul do TCC.

Atenção à bandeira: quando estes testes foram escritos, a tabela
``bandeira_tarifaria`` ia só até 06/2025, então o PI de 2025 saía **sem
bandeira**. Com o histórico oficial da ANEEL carregado
(``scripts/cargar_bandeiras_aneel.py``), as competências passaram a ter:

- 2025-12-01 → Amarela R$ 18,85/MWh  → PI ≈ 337,21 (era 318,20 sem bandeira);
- 2025-08-01 → Vermelha P2 R$ 78,77/MWh → PI ≈ 381,65 (era 302,20).

O ``bandeira_r_mwh`` é conferido junto para deixar explícito de onde vem a
diferença em relação ao número publicado no TCC (que não considerou bandeira).
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
    # Bandeira Amarela de 12/2025 (ANEEL, REH 3.306/2024): R$ 18,85/MWh.
    assert corpo["bandeira_r_mwh"] == pytest.approx(18.85, abs=0.01)
    # PI do TCC (318,20) + bandeira: o TCC não considerava bandeira.
    assert corpo["pi"] == pytest.approx(337.21, abs=0.01)
    assert corpo["modalidade"] == "AZUL"
    assert corpo["e_mwh"] == pytest.approx(1425.83 + 14125.16, abs=0.01)


def test_epi_celesc_vigencia_anterior_reproduz_tcc(banco):
    resposta = client.post(
        "/api/epi/calcular", json=_payload(data_referencia="2025-08-01")
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    # Bandeira Vermelha P2 de 08/2025 (ANEEL, REH 3.306/2024): R$ 78,77/MWh.
    assert corpo["bandeira_r_mwh"] == pytest.approx(78.77, abs=0.01)
    assert corpo["pi"] == pytest.approx(381.65, abs=0.01)


def test_epi_sem_bandeira_usa_zero(banco):
    """Competência anterior a jan/2015: sem bandeira, adicional 0 (não é erro)."""
    resposta = client.post(
        "/api/epi/calcular", json=_payload(data_referencia="2014-06-01")
    )

    assert resposta.status_code == 200
    assert resposta.json()["bandeira_r_mwh"] == 0.0


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
    # Mesmo perfil/data do teste do E-PI: PI com a bandeira Amarela de 12/2025.
    assert por_modalidade["Azul"]["pi"] == pytest.approx(337.21, abs=0.01)
    assert por_modalidade["Verde"]["pi"] is not None
