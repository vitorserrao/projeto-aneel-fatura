"""Teste de integração da comparação de modalidades (API + banco)."""

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


def _perfil(**over):
    base = {
        "distribuidora": "Âmbar Amazonas",
        "subgrupo": "A4",
        "classe": "Não se aplica",
        "detalhe": "Não se aplica",
        "data_referencia": "2010-12-01",
        "consumo_ponta_kwh": 354.0,
        "consumo_fora_ponta_kwh": 3891.0,
        "demanda_medida_unica_kw": 100.0,
        "demanda_contratada_unica_kw": 100.0,
        "demanda_ponta_kw": 100.0,
        "demanda_fora_ponta_kw": 100.0,
        "demanda_contratada_ponta_kw": 100.0,
        "demanda_contratada_fora_ponta_kw": 100.0,
        "cip_cosip_rs": 133.2,
        "outros_rs": 50.0,
    }
    base.update(over)
    return base


def test_comparar_a4_azul_verde_ranqueado(banco):
    r = client.post("/api/calculo/comparar", json=_perfil())
    assert r.status_code == 200, r.text
    comp = r.json()["comparacao"]
    disponiveis = comp["disponiveis"]
    assert len(disponiveis) == 2, disponiveis
    mods = [d["modalidade"] for d in disponiveis]
    assert mods == ["Verde", "Azul"]  # ranqueado por menor custo no Caso 1
    assert comp["melhor"] == "Verde"
    # Nenhuma modalidade deve aparecer como "indisponível" aqui (Verde é
    # elegível em A4 e Azul é sempre elegível).
    assert comp["indisponiveis"] == []


def test_comparar_a2_somente_azul(banco):
    r = client.post(
        "/api/calculo/comparar",
        json=_perfil(subgrupo="A2", distribuidora="CPFL JAGUARI"),
    )
    assert r.status_code == 200, r.text
    comp = r.json()["comparacao"]
    disponiveis = comp["disponiveis"]
    assert [d["modalidade"] for d in disponiveis] == ["Azul"]
    indis = {i["modalidade"]: i["motivo"] for i in comp["indisponiveis"]}
    assert "Verde" in indis
    assert "A3a, A4 e AS" in indis["Verde"]


def test_comparar_propaga_tributos(banco):
    params = {
        "aplicar_tributos": "true",
        "pis": 0.0065,
        "cofins": 0.03,
        "icms": 0.18,
        "tipo_icms": "fora",
    }
    r = client.post(
        "/api/calculo/comparar", json=_perfil(), params=params
    )
    assert r.status_code == 200, r.text
    comp = r.json()["comparacao"]
    # Cada modalidade disponível deve ter aplicar_tributos=True.
    assert all(d["aplicar_tributos"] for d in comp["disponiveis"])
