"""Testes da camada de consultas (Sprint 4).

Usam os dados reais carregados na Sprint 3, sempre com filtros específicos
(nada de contagens globais frágeis). Se o PostgreSQL não estiver disponível,
os testes são ignorados.
"""

from datetime import date, timedelta

import pytest
from sqlmodel import func, select

from infra.database import create_db_engine, create_session_factory, ping_db
from infra.models import Distribuidora, TarifaAplicacaoComponente
from infra.repositories.tarifa_repository import TarifaRepository


@pytest.fixture(scope="module")
def repo():
    eng = create_db_engine()
    try:
        ping_db(eng)
    except Exception as exc:  # pragma: no cover - ambiente sem banco
        pytest.skip(f"PostgreSQL nao disponivel: {exc}")
    return TarifaRepository(create_session_factory(eng))


# CPFL JAGUARI / A2 / Azul / Tarifa de Aplicação: vigência 2010-02-03 a
# 2011-02-02 (primeiras linhas do CSV real).
DIST = "CPFL JAGUARI"
SUB = "A2"
MOD = "Azul"
BASE = "Tarifa de Aplicação"
DATA_DENTRO = date(2010, 6, 1)
DATA_FORA = date(2025, 6, 1)


def test_consulta_por_distribuidora(repo):
    r = repo.buscar_tarifas(
        sig_agente=DIST,
        data=DATA_DENTRO,
        subgrupo=SUB,
        modalidade=MOD,
        base_tarifaria=BASE,
    )
    assert r
    assert all(x.sig_agente == DIST for x in r)


def test_filtro_componente_tusd(repo):
    r = repo.buscar_tarifas(
        sig_agente=DIST,
        data=DATA_DENTRO,
        subgrupo=SUB,
        modalidade=MOD,
        base_tarifaria=BASE,
        componente="TUSD",
    )
    assert r
    assert all(x.componente == "TUSD" for x in r)


def test_filtro_base_tarifaria(repo):
    r = repo.buscar_tarifas(
        sig_agente=DIST,
        data=DATA_DENTRO,
        subgrupo=SUB,
        modalidade=MOD,
        base_tarifaria=BASE,
    )
    assert r
    assert all(x.base_tarifaria == BASE for x in r)


def test_vigencia_dentro_e_fora(repo):
    dentro = repo.buscar_tarifas(
        sig_agente=DIST,
        data=DATA_DENTRO,
        subgrupo=SUB,
        modalidade=MOD,
        base_tarifaria=BASE,
        componente="TUSD",
    )
    assert dentro
    assert all(
        x.inicio_vigencia <= DATA_DENTRO <= x.fim_vigencia for x in dentro
    )

    fora = repo.buscar_tarifas(
        sig_agente=DIST,
        data=DATA_FORA,
        subgrupo=SUB,
        modalidade=MOD,
        base_tarifaria=BASE,
        componente="TUSD",
    )
    # O registro de 2010-02-03..2011-02-02 não pode aparecer em 2025.
    registro_2010 = [
        x
        for x in fora
        if x.inicio_vigencia == date(2010, 2, 3)
        and x.fim_vigencia == date(2011, 2, 2)
    ]
    assert registro_2010 == []


def _combo_com_te_e_tusd():
    """Encontra um combo real que possui TE e TUSD na mesma vigência."""
    eng = create_db_engine()
    with create_session_factory(eng)() as s:
        return s.execute(
            select(
                Distribuidora.num_cnpj,
                TarifaAplicacaoComponente.dsc_sub_grupo,
                TarifaAplicacaoComponente.dsc_modalidade_tarifaria,
                TarifaAplicacaoComponente.dsc_base_tarifaria,
                TarifaAplicacaoComponente.dat_inicio_vigencia,
                TarifaAplicacaoComponente.dat_fim_vigencia,
            )
            .join(
                Distribuidora,
                Distribuidora.id == TarifaAplicacaoComponente.distribuidora_id,
            )
            .where(TarifaAplicacaoComponente.componente.in_(("TE", "TUSD")))
            .group_by(
                Distribuidora.num_cnpj,
                TarifaAplicacaoComponente.dsc_sub_grupo,
                TarifaAplicacaoComponente.dsc_modalidade_tarifaria,
                TarifaAplicacaoComponente.dsc_base_tarifaria,
                TarifaAplicacaoComponente.dat_inicio_vigencia,
                TarifaAplicacaoComponente.dat_fim_vigencia,
            )
            .having(
                func.count(func.distinct(TarifaAplicacaoComponente.componente))
                == 2
            )
            .limit(1)
        ).first()


def test_te_e_tusd_identificaveis(repo):
    combo = _combo_com_te_e_tusd()
    assert combo is not None, "nenhum combo TE+TUSD encontrado nos dados reais"
    cnpj, sub, mod, base, ini, fim = combo
    data = ini + (fim - ini) // 2
    r = repo.buscar_componentes(
        num_cnpj=cnpj,
        data=data,
        subgrupo=sub,
        modalidade=mod,
        base_tarifaria=base,
    )
    assert set(r) == {"TE", "TUSD"}
    assert any(x.componente == "TE" for x in r["TE"])
    assert any(x.componente == "TUSD" for x in r["TUSD"])


def test_filtros_combinados(repo):
    r = repo.buscar_tarifas(
        sig_agente=DIST,
        data=DATA_DENTRO,
        subgrupo=SUB,
        modalidade=MOD,
        base_tarifaria=BASE,
        componente="TUSD",
    )
    assert r
    assert all(
        x.sig_agente == DIST
        and x.subgrupo == SUB
        and x.modalidade == MOD
        and x.base_tarifaria == BASE
        and x.componente == "TUSD"
        for x in r
    )


def test_rge_cnpjs_distintos(repo):
    # RGE tem mais de um CNPJ no dataset. Cada CNPJ deve retornar apenas
    # os próprios registros (CNPJ é identidade; sig é atributo).
    cnpjs = [
        d.num_cnpj
        for d in repo.listar_distribuidoras()
        if d.sig_agente.upper().startswith("RGE")
    ]
    assert len(cnpjs) >= 2
    for cnpj in cnpjs:
        r = repo.buscar_tarifas(num_cnpj=cnpj)
        assert r
        assert {x.num_cnpj for x in r} == {cnpj}


def test_listar_filtros_auxiliares(repo):
    assert "A4" in repo.listar_subgrupos()
    assert "Azul" in repo.listar_modalidades()
    assert repo.listar_classes()
    assert set(repo.listar_componentes()) == {"TE", "TUSD"}
    assert set(repo.listar_bases_tarifarias()) == {
        "Tarifa de Aplicação",
        "Base Econômica",
    }


def test_listar_distribuidoras_identidade_cnpj(repo):
    dists = repo.listar_distribuidoras()
    assert dists
    cnpjs = [d.num_cnpj for d in dists]
    assert len(cnpjs) == len(set(cnpjs))  # CNPJ único entre distribuidoras
