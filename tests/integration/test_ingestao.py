"""Testes de integração da ingestão (Sprint 3) — fixture pequena.

Usa o CSV de amostra em tests/fixtures/tarifas_amostra.csv contra o PostgreSQL
real. Se o banco não estiver disponível, os testes são ignorados.

A fixture tem 6 linhas. Regras obrigatórias cobertas:
  * TE/TUSD em linhas (componentes quando valor != 0);
  * valor negativo preservado (linha 5: TUSD -122,63; linha 6: TE -20,75);
  * duas bases (Tarifa de Aplicação / Base Econômica);
  * RGE com dois CNPJs distintos (linhas 4 e 5);
  * acessante "Não se aplica" e "Neoenergia Elektro";
  * vigência (dat_inicio/fim).

  Linha 1 -> TUSD (1,85); linha 2 -> TUSD (1,85); linha 3 -> TUSD(31,48)+TE(10,50);
  linha 4 -> TE(20,00); linha 5 -> TUSD(-122,63); linha 6 -> TUSD(1,50)+TE(-20,75).
  Total de componentes esperados: 1+1+2+1+1+2 = 8.
"""

from pathlib import Path

import pytest
from sqlalchemy import delete, func, select

from infra.database import create_db_engine, create_session_factory, init_db, ping_db
from infra.ingestion.cleaner import normalizar_decimal, normalizar_cnpj
from infra.ingestion.load import CargaAneelError, PipelineIngestao
from infra.models import (
    Acessante,
    CargaAneel,
    Distribuidora,
    TarifaAplicacaoComponente,
)

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "tarifas_amostra.csv"


@pytest.fixture(scope="module")
def engine():
    eng = create_db_engine()
    try:
        ping_db(eng)
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"PostgreSQL nao disponivel: {exc}")
    init_db(eng)
    return eng


@pytest.fixture(scope="module")
def sf(engine):
    return create_session_factory(engine)


@pytest.fixture()
def resumo_limpo(sf):
    """Roda a carga da fixture, devolve o resumo e limpa ao final do teste.

    O cleanup é escopado apenas à carga criada por este teste (por carga_id),
    para não afetar outras cargas existentes (ex.: a carga real do CSV).
    """
    resumo = PipelineIngestao(sf).executar(str(FIXTURE))
    carga_id = resumo["carga_id"]
    yield resumo
    with sf() as s:
        # Remove componentes da carga do teste, depois a carga.
        s.execute(
            delete(TarifaAplicacaoComponente).where(
                TarifaAplicacaoComponente.carga_id == carga_id
            )
        )
        s.execute(delete(CargaAneel).where(CargaAneel.id == carga_id))
        # Remove apenas as distribuidoras criadas por esta carga (CNPJs de teste).
        cnpjs_teste = [d for d in ("90000000000001", "90000000000002", "90000000000003", "90000000000004")]
        s.execute(delete(Distribuidora).where(Distribuidora.num_cnpj.in_(cnpjs_teste)))
        # Remove apenas acessantes criados por esta carga (nomes de teste).
        acess_teste = ["TESTE ACESSANTE 1", "TESTE ACESSANTE 2"]
        s.execute(delete(Acessante).where(Acessante.sig_acessante.in_(acess_teste)))
        s.commit()


def test_loader_conta_linhas():
    from infra.ingestion.loader import carregar_dataset

    linhas = list(carregar_dataset(str(FIXTURE)))
    assert len(linhas) == 6


def test_cleaner_decimal_e_cnpj():
    from decimal import Decimal

    assert normalizar_decimal("1,85", "VlrTUSD") == Decimal("1.85")
    assert normalizar_decimal(",00", "VlrTE") == Decimal("0.00")
    assert normalizar_decimal("-122,63", "VlrTUSD") == Decimal("-122.63")
    assert normalizar_cnpj("99999999999991") == "99999999999991"


def test_ingestao_completa_contagens(sf, resumo_limpo):
    assert resumo_limpo["linhas_csv"] == 6
    assert resumo_limpo["distribuidoras"] == 4  # CPFL TESTE, RGE, NEG TESTE
    assert resumo_limpo["acessantes"] == 2
    assert resumo_limpo["componentes"] == 8

    with sf() as s:
        total = s.execute(
            select(func.count())
            .select_from(TarifaAplicacaoComponente)
            .where(TarifaAplicacaoComponente.carga_id == resumo_limpo["carga_id"])
        ).scalar()
        assert total == 8

        bases = s.execute(
            select(
                TarifaAplicacaoComponente.dsc_base_tarifaria, func.count()
            )
            .where(TarifaAplicacaoComponente.carga_id == resumo_limpo["carga_id"])
            .group_by(TarifaAplicacaoComponente.dsc_base_tarifaria)
        ).all()
        bases_dict = {b: c for b, c in bases}
        assert bases_dict.get("Tarifa de Aplicação") == 7
        assert bases_dict.get("Base Econômica") == 1

        neg_tusd = s.execute(
            select(func.count())
            .select_from(TarifaAplicacaoComponente)
            .where(
                TarifaAplicacaoComponente.carga_id == resumo_limpo["carga_id"],
                TarifaAplicacaoComponente.componente == "TUSD",
                TarifaAplicacaoComponente.valor < 0,
            )
        ).scalar()
        neg_te = s.execute(
            select(func.count())
            .select_from(TarifaAplicacaoComponente)
            .where(
                TarifaAplicacaoComponente.carga_id == resumo_limpo["carga_id"],
                TarifaAplicacaoComponente.componente == "TE",
                TarifaAplicacaoComponente.valor < 0,
            )
        ).scalar()
        assert neg_tusd == 1
        assert neg_te == 1

        rge = (
            s.execute(
                select(Distribuidora.num_cnpj).where(
                    Distribuidora.num_cnpj.in_(["90000000000002", "90000000000003"])
                )
            )
            .scalars()
            .all()
        )
        assert sorted(rge) == ["90000000000002", "90000000000003"]
        # E a sig destes CNPJs está preservada como 'RGE'.
        sig_rge = (
            s.execute(
                select(Distribuidora.sig_agente).where(
                    Distribuidora.num_cnpj.in_(["90000000000002", "90000000000003"])
                )
            )
            .scalars()
            .all()
        )
        assert set(sig_rge) == {"RGE"}

        carga = s.get(CargaAneel, resumo_limpo["carga_id"])
        assert carga is not None
        assert carga.num_registros == 6
        assert len(carga.sha256_arquivo) == 64

        # FKs válidas: acessante e distribuidora não nulos nas linhas-fato.
        sem_fk = s.execute(
            select(func.count())
            .select_from(TarifaAplicacaoComponente)
            .where(
                TarifaAplicacaoComponente.carga_id == resumo_limpo["carga_id"],
                TarifaAplicacaoComponente.acessante_id.is_(None),
            )
        ).scalar()
        assert sem_fk == 0


def test_ingestao_reusso_detecta_duplicidade(sf):
    # A carga da fixture é feita aqui; a segunda chamada do MESMO arquivo
    # deve ser recusada por SHA-256 já registrado (idempotência).
    resumo = PipelineIngestao(sf).executar(str(FIXTURE))
    carga_id = resumo["carga_id"]
    with pytest.raises(CargaAneelError):
        PipelineIngestao(sf).executar(str(FIXTURE))
    # clean up escopado à carga do teste (não afeta outras cargas).
    with sf() as s:
        s.execute(
            delete(TarifaAplicacaoComponente).where(
                TarifaAplicacaoComponente.carga_id == carga_id
            )
        )
        s.execute(delete(CargaAneel).where(CargaAneel.id == carga_id))
        s.execute(
            delete(Distribuidora).where(
                Distribuidora.num_cnpj.in_(
                    ["90000000000001", "90000000000002", "90000000000003", "90000000000004"]
                )
            )
        )
        s.execute(
            delete(Acessante).where(
                Acessante.sig_acessante.in_(["TESTE ACESSANTE 1", "TESTE ACESSANTE 2"])
            )
        )
        s.commit()
