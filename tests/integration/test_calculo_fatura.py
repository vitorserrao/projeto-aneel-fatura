"""Testes de integração do endpoint de cálculo de fatura (motor da fatura).

Usam os dados reais carregados. Se o banco não estiver disponível, são
ignorados (pytest.skip).
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


def _perfil(data="2010-06-01"):
    return {
        "distribuidora": "CPFL JAGUARI",
        "subgrupo": "A2",
        "classe": "Não se aplica",
        "subclasse": "Não se aplica",
        "detalhe": "Não se aplica",
        "data_referencia": data,
        "consumo_ponta_kwh": 100_000.0,
        "consumo_fora_ponta_kwh": 900_000.0,
        "demanda_ponta_kw": 1_000.0,
        "demanda_fora_ponta_kw": 2_000.0,
        "demanda_contratada_ponta_kw": 1_200.0,
        "demanda_contratada_fora_ponta_kw": 1_500.0,
    }


def test_health(banco):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_calcular_fatura_azul(banco):
    r = client.post(
        "/api/calculo/fatura",
        json=_perfil(),
        params={"modalidade": "Azul", "base_tarifaria": "Tarifa de Aplicação"},
    )
    assert r.status_code == 200, r.text
    fatura = r.json()["fatura"]

    assert fatura["modalidade"].lower() == "azul"
    assert fatura["linhas"], "deveria haver linhas na fatura"
    assert fatura["custo_total"] > 0

    # Linhas coerentes: toda linha tarifária tem custo = quantidade × tarifa.
    tarifarias = [l for l in fatura["linhas"] if l["categoria"] == "TARIFA"]
    assert tarifarias, "deveria haver linhas tarifárias"
    assert all(
        abs(l["custo"] - l["quantidade"] * l["tarifa"]) < 1e-6 for l in tarifarias
    )

    # A demanda faturável usa a CONTRATADA (1.200 kW > 1.000 kW medida) no posto
    # ponta: a linha de TUSD DEMANDA PONTA deve ter quantidade 1.200.
    demanda_ponta = [
        l
        for l in tarifarias
        if l["descricao"] == "TUSD DEMANDA PONTA"
    ]
    assert demanda_ponta, "linha de demanda ponta não encontrada"
    assert all(abs(l["quantidade"] - 1_200.0) < 1e-6 for l in demanda_ponta)

    # Sem duplicidade (filtro de detalhe resolveu o P6): TUSD DEMANDA PONTA
    # deve aparecer UMA única vez.
    assert len(demanda_ponta) == 1

    # Data legada (2010): TE usa postos seca/úmida, agora mapeados pelo
    # mês (P5 resolvido) — nada deve ficar não mapeado.
    assert fatura["tarifas_nao_mapeadas"] == 0
    te = [l for l in tarifarias if l["descricao"].startswith("TE ")]
    assert te, "TE deveria ser mapeada em data horo-sazonal"


def test_fatura_data_fora_vigencia(banco):
    r = client.post(
        "/api/calculo/fatura",
        json=_perfil(data="2030-01-01"),
        params={"modalidade": "Azul"},
    )
    assert r.status_code == 422
