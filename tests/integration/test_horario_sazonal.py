"""Teste de integração do mapeamento horo-sazonal (P5).

Valida que datas em vigência horo-sazonal mapeiam os postos seca/úmida
para Ponta/Fora ponta pelo MÊS da data de referência, incluem a TE e não
duplicam linhas (posto simples vs sazonal na mesma vigência).
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


def _perfil(data):
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


@pytest.mark.parametrize(
    "data,par_tarifa_ponta,par_tarifa_fp",
    [
        # junho = período seco (mai-nov)
        ("2010-06-01", 177.55, 158.62),
        # janeiro = período úmido (dez-abr)
        ("2011-01-15", 103.01, 92.04),
    ],
)
def test_horario_sazonal_mapeia_te(banco, data, par_tarifa_ponta, par_tarifa_fp):
    r = client.post(
        "/api/calculo/fatura",
        json=_perfil(data),
        params={"modalidade": "Azul", "base_tarifaria": "Tarifa de Aplicação"},
    )
    assert r.status_code == 200, r.text
    fatura = r.json()["fatura"]

    # Nada não mapeado: os postos sazonais foram resolvidos.
    assert fatura["tarifas_nao_mapeadas"] == 0

    te = [l for l in fatura["linhas"] if l["descricao"].startswith("TE ")]
    assert len(te) == 2, f"deveria ter TE ponta e fora ponta, veio: {te}"
    te_ponta = next(l for l in te if l["descricao"] == "TE ENERGIA PONTA")
    te_fp = next(l for l in te if l["descricao"] == "TE ENERGIA FORA PONTA")
    assert abs(te_ponta["tarifa"] - par_tarifa_ponta) < 1e-6
    assert abs(te_fp["tarifa"] - par_tarifa_fp) < 1e-6

    # Nenhuma linha duplicada: posto simples não é somado junto com o sazonal.
    descricoes = [l["descricao"] for l in fatura["linhas"]]
    assert len(descricoes) == len(set(descricoes)), "linhas duplicadas na fatura"
