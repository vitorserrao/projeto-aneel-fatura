"""Optante B no E-PI e paridade de flags entre /calculo/comparar e /calculo/fatura.

Dois defeitos de integração cobertos aqui:

1. ``POST /api/epi/calcular`` com ``modalidade="Optante B"`` devolvia
   HTTP 400 ("TE indisponível"): o E-PI buscava a modalidade literal
   "Optante B", que **não existe** no dataset ANEEL (art. 292 manda faturar
   pela Convencional do Grupo B derivado da atividade). A fatura já usava a
   regra; o E-PI não.

2. ``POST /api/calculo/comparar`` ignorava em silêncio as flags
   ``demanda_isenta_icms``, ``demanda_isenta_icms_kw``, ``arredondar_centavos``
   e ``tributar_reativos`` — os totais divergiam do ``/calculo/fatura`` para o
   mesmo perfil (Copel 03/2023: 10.297,70 × 9.851,96).
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from infra.database import create_db_engine, ping_db

client = TestClient(app)

# Caso real: Copel A4, conta de 03/2023 (docs/validacao_conta_real_copel_verde_2023.md)
PERFIL = {
    "distribuidora": "COPEL-DIS",
    "subgrupo": "A4",
    "classe": "Não se aplica",
    "subclasse": "Não se aplica",
    "detalhe": "Não se aplica",
    "data_referencia": "2023-03-15",
    "consumo_ponta_kwh": 55,
    "consumo_fora_ponta_kwh": 9094,
    "demanda_medida_unica_kw": 150.65,
    "demanda_contratada_unica_kw": 260,
    "outros_rs": 115.01,
    "reativo_energia_fora_ponta_kvArh": 9,
    "potencia_transformadores_kva": 100,
    "atividade": "Comercial ou Industrial",
}

FLAGS = {
    "base_tarifaria": "Tarifa de Aplicação",
    "aplicar_tributos": True,
    "pis": 0.0095,
    "cofins": 0.0438,
    "icms": 0.18,
    "tipo_icms": "fora",
    "reativos_direto": False,
    "arredondar_centavos": True,
    "demanda_isenta_icms": True,
    "demanda_isenta_icms_kw": 109.35,
}

EPI = {
    "distribuidora": "COPEL-DIS",
    "subgrupo": "A4",
    "data_referencia": "2023-03-15",
    "modalidade": "Optante B",
    "atividade": "Comercial ou Industrial",
    "consumo_ponta_kwh": 55,
    "consumo_fora_ponta_kwh": 9094,
    "pis": 0.0095,
    "cofins": 0.0438,
    "icms": 0.18,
}


@pytest.fixture(scope="module")
def banco():
    eng = create_db_engine()
    try:
        ping_db(eng)
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"PostgreSQL nao disponivel: {exc}")
    return True


def test_epi_optante_b_calcula(banco):
    """E-PI do Optante B devolve PI (antes: HTTP 400 'TE indisponível')."""
    resposta = client.post("/api/epi/calcular", json=EPI)

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["modalidade"] == "OPTANTE B"
    assert corpo["pi"] > 0
    assert corpo["c_te"] > 0
    assert corpo["e_mwh"] == pytest.approx(9.149, abs=0.001)


def test_epi_optante_b_usa_a_te_da_fatura(banco):
    """A TE do E-PI é a mesma que a fatura Optante B usa (art. 292)."""
    params = {**FLAGS, "modalidade": "Optante B", "aplicar_tributos": False}
    fatura = client.post("/api/calculo/fatura", json=PERFIL, params=params)
    assert fatura.status_code == 200, fatura.text

    linhas_te = [l for l in fatura.json()["fatura"]["linhas"] if l["descricao"].startswith("TE ")]
    assert linhas_te, "a fatura Optante B precisa ter linha de TE"
    te_media = sum(l["custo"] for l in linhas_te) / sum(l["quantidade"] for l in linhas_te)

    epi = client.post("/api/epi/calcular", json=EPI)
    assert epi.status_code == 200, epi.text
    corpo = epi.json()
    # Perfil só com consumo fora ponta: c_te / e_mwh é a TE aplicada (R$/MWh).
    assert corpo["c_te"] / corpo["e_mwh"] == pytest.approx(te_media, abs=0.01)


def test_comparar_e_fatura_dao_o_mesmo_total(banco):
    """As flags do /fatura precisam valer também no /comparar."""
    fatura = client.post(
        "/api/calculo/fatura", json=PERFIL, params={**FLAGS, "modalidade": "Verde"}
    )
    assert fatura.status_code == 200, fatura.text
    total_fatura = fatura.json()["fatura"]["custo_total"]

    comparacao = client.post("/api/calculo/comparar", json=PERFIL, params=FLAGS)
    assert comparacao.status_code == 200, comparacao.text
    verdes = [
        f for f in comparacao.json()["comparacao"]["disponiveis"] if f["modalidade"] == "Verde"
    ]
    assert verdes, comparacao.json()["comparacao"]

    assert verdes[0]["custo_total"] == pytest.approx(total_fatura, abs=0.01)
    # Valor de referência da conta real (03/2023), com o Δ conhecido do reativo.
    assert verdes[0]["custo_total"] == pytest.approx(9851.96, abs=0.01)
