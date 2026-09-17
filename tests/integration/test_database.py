"""Testes de integração do banco: conexão, schema e repository (consulta).

Estes testes usam o PostgreSQL local (docker compose, container
projeto-aneel-db). Se o banco não estiver disponível, são ignorados com
``pytest.skip`` — a suíte unitária continua independente.

Os dados inseridos são removidos ao final de cada teste (cleanup) para
garantir idempotência entre execuções.
"""

from datetime import date

import pytest
from sqlalchemy import delete

from infra.database import create_db_engine, create_session_factory, init_db, ping_db
from infra.models import Acessante, CargaAneel, Distribuidora, TarifaAplicacaoComponente
from infra.repositories.tarifa_repository import TarifaRepository

# Sufixo único por execução do teste, para não colidir com dados persistentes.
import uuid

_SUFIXO = uuid.uuid4().hex[:8]


def _cnpj() -> str:
    return f"{_SUFIXO[:8]}0001{_SUFIXO[-4:]}"[:14]


@pytest.fixture(scope="module")
def engine():
    eng = create_db_engine()
    try:
        ping_db(eng)
    except Exception as exc:  # pragma: no cover - ambiente sem banco
        pytest.skip(f"PostgreSQL nao disponivel: {exc}")
    init_db(eng)
    return eng


@pytest.fixture()
def session_factory(engine):
    return create_session_factory(engine)


def test_schema_criado(engine):
    from sqlalchemy import inspect

    insp = inspect(engine)
    tabelas = set(insp.get_table_names())
    esperadas = {
        "distribuidora",
        "acessante",
        "carga_aneel",
        "tarifa_aplicacao_componente",
    }
    assert esperadas <= tabelas


def test_conexao_ping(engine):
    assert ping_db(engine) is True


def test_repository_consulta_vigencia_e_filtros(engine, session_factory):
    cnpj = _cnpj()
    with session_factory() as s:
        dist = Distribuidora(num_cnpj=cnpj, sig_agente=f"DIST {_SUFIXO}")
        ac = Acessante(sig_acessante=f"ACESSANTE {_SUFIXO}")
        s.add_all([dist, ac])
        s.flush()

        carga = CargaAneel(
            arquivo_origem=f"data/raw/teste-{_SUFIXO}.csv",
            sha256_arquivo=_SUFIXO.ljust(64, "a")[:64],
            dat_geracao_conjunto=date(2026, 8, 31),
            num_registros=1,
        )
        s.add(carga)
        s.flush()

        linha = TarifaAplicacaoComponente(
            carga_id=carga.id,
            distribuidora_id=dist.id,
            acessante_id=ac.id,
            dsc_reh="REH TESTE",
            dat_inicio_vigencia=date(2026, 1, 1),
            dat_fim_vigencia=date(2027, 8, 27),
            dsc_base_tarifaria="Tarifa de Aplicação",
            dsc_sub_grupo="A4",
            dsc_modalidade_tarifaria="Azul",
            dsc_classe="Não se aplica",
            dsc_sub_classe="Não se aplica",
            dsc_detalhe="Não se aplica",
            nom_posto_tarifario="Ponta",
            dsc_unidade_terciaria="MWh",
            componente="TE",
            valor=300.0,
            linha_origem=1,
            hash_linha=_SUFIXO.ljust(64, "b")[:64],
        )
        s.add(linha)
        s.commit()
        carga_id = carga.id

    try:
        repo = TarifaRepository(session_factory)
        resultado = repo.buscar_tarifas(
            data=date(2026, 6, 1),
            num_cnpj=cnpj,
            subgrupo="A4",
            modalidade="Azul",
            posto="Ponta",
            componente="TE",
        )
        assert len(resultado) == 1
        tarifa = resultado[0]
        assert tarifa.componente == "TE"
        assert tarifa.valor == 300.0
        assert tarifa.subgrupo == "A4"
        assert tarifa.num_cnpj == cnpj

        # Data fora de vigência retorna vazio.
        fora = repo.buscar_tarifas(
            data=date(2028, 1, 1),
            num_cnpj=cnpj,
            subgrupo="A4",
            modalidade="Azul",
            posto="Ponta",
            componente="TE",
        )
        assert fora == []
    finally:
        # Cleanup: remove os dados inseridos neste teste.
        with session_factory() as s:
            s.execute(
                delete(TarifaAplicacaoComponente).where(
                    TarifaAplicacaoComponente.carga_id == carga_id
                )
            )
            s.execute(delete(CargaAneel).where(CargaAneel.id == carga_id))
            s.execute(delete(Distribuidora).where(Distribuidora.num_cnpj == cnpj))
            s.execute(delete(Acessante).where(Acessante.sig_acessante == f"ACESSANTE {_SUFIXO}"))
            s.commit()


def test_repository_listar_distribuidoras_nao_vazio(session_factory):
    repo = TarifaRepository(session_factory)
    dists = repo.listar_distribuidoras()
    assert dists
    cnpjs = [d.num_cnpj for d in dists]
    assert len(cnpjs) == len(set(cnpjs))  # CNPJ é identidade única
