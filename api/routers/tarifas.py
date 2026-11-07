""""Routers de consulta (leitura) de tarifas (Sprint P3).

Somente leitura: devolvem tarifas/distribuidoras já carregadas no PostgreSQL,
sem nenhum cálculo. Usam ``TarifaRepository`` por injeção de dependência.

Grupo de rotas (via prefixo montado em api/main.py):
- GET /distribuidoras          -> lista de distribuidoras
- GET /tarifas                 -> tarifas vigentes por filtros
- GET /tarifas/te-tusd         -> TE e TUSD de um perfil (sem somar)
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.exc import SQLAlchemyError

from infra.repositories.tarifa_repository import TarifaRepository, TarifaVigente
from schemas.consulta import DistribuidoraOut, TarifaConsultaOut

router = APIRouter()


def repo_dependency() -> TarifaRepository:
    """Fornece o TarifaRepository (usa a session factory compartilhada)."""
    from infra.database import get_session_factory

    return TarifaRepository(get_session_factory())


_Repo = Annotated[TarifaRepository, Depends(repo_dependency)]


def _to_out(t: TarifaVigente) -> TarifaConsultaOut:
    return TarifaConsultaOut(
        num_cnpj=t.num_cnpj,
        sig_agente=t.sig_agente,
        componente=t.componente,
        valor=float(t.valor),
        resolucao=t.resolucao,
        inicio_vigencia=t.inicio_vigencia.isoformat() if t.inicio_vigencia else None,
        fim_vigencia=t.fim_vigencia.isoformat() if t.fim_vigencia else None,
        base_tarifaria=t.base_tarifaria,
        subgrupo=t.subgrupo,
        modalidade=t.modalidade,
        classe=t.classe,
        subclasse=t.subclasse,
        detalhe=t.detalhe,
        posto=t.posto,
        unidade=t.unidade,
    )


@router.get("/distribuidoras", response_model=list[DistribuidoraOut], tags=["consulta"])
def listar_distribuidoras(repo: _Repo) -> list[DistribuidoraOut]:
    """Retorna as distribuidoras cadastradas (identidade = CNPJ)."""
    try:
        dists = repo.listar_distribuidoras()
    except SQLAlchemyError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"falha ao consultar distribuidoras: {exc}")
    return [DistribuidoraOut(num_cnpj=d.num_cnpj, sig_agente=d.sig_agente) for d in dists]


@router.get("/tarifas", response_model=list[TarifaConsultaOut], tags=["consulta"])
def buscar_tarifas(
    repo: _Repo,
    num_cnpj: str | None = Query(default=None),
    sig_agente: str | None = Query(default=None),
    data: str | None = Query(default=None, description="AAAA-MM-DD (vigência)"),
    subgrupo: str | None = Query(default=None),
    modalidade: str | None = Query(default=None),
    classe: str | None = Query(default=None),
    subclasse: str | None = Query(default=None),
    detalhe: str | None = Query(default=None),
    posto: str | None = Query(default=None),
    unidade: str | None = Query(default=None),
    componente: str | None = Query(default=None),
    base_tarifaria: str | None = Query(default=None),
) -> list[TarifaConsultaOut]:
    """Busca tarifas vigentes (intervalo inclusivo) segundo os filtros."""
    try:
        data_dt = date.fromisoformat(data) if data else None
    except ValueError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"data inválida: {data!r}")

    try:
        tarifas = repo.buscar_tarifas(
            data=data_dt,
            num_cnpj=num_cnpj,
            sig_agente=sig_agente,
            subgrupo=subgrupo,
            modalidade=modalidade,
            classe=classe,
            subclasse=subclasse,
            detalhe=detalhe,
            posto=posto,
            unidade=unidade,
            componente=componente,
            base_tarifaria=base_tarifaria,
        )
    except SQLAlchemyError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"falha ao consultar tarifas: {exc}")
    return [_to_out(t) for t in tarifas]


@router.get("/tarifas/te-tusd", tags=["consulta"])
def buscar_te_tusd(
    repo: _Repo,
    num_cnpj: str | None = Query(default=None),
    sig_agente: str | None = Query(default=None),
    data: str | None = Query(default=None),
    subgrupo: str | None = Query(default=None),
    modalidade: str | None = Query(default=None),
    posto: str | None = Query(default=None),
    base_tarifaria: str | None = Query(default=None),
):
    """Retorna TE e TUSD de um perfil/contexto, SEM somar (dict: TE/TUSD)."""
    try:
        data_dt = date.fromisoformat(data) if data else None
    except ValueError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"data inválida: {data!r}")
    try:
        comps = repo.buscar_componentes(
            data=data_dt,
            num_cnpj=num_cnpj,
            sig_agente=sig_agente,
            subgrupo=subgrupo,
            modalidade=modalidade,
            posto=posto,
            base_tarifaria=base_tarifaria,
        )
    except SQLAlchemyError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"falha: {exc}")
    return {
        "TE": [_to_out(t) for t in comps["TE"]],
        "TUSD": [_to_out(t) for t in comps["TUSD"]],
    }

@router.get("/subgrupos", response_model=list[str], tags=["consulta"])
def listar_subgrupos(repo: _Repo) -> list[str]:
    """Retorna a lista de subgrupos distintos já carregados no banco."""
    try:
        subgrupos = repo.listar_subgrupos()
    except SQLAlchemyError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"falha ao consultar subgrupos: {exc}")
    return subgrupos


@router.get("/bandeira", tags=["consulta"])
def consultar_bandeira(
    repo: _Repo,
    competencia: str = Query(..., description="AAAA-MM-DD (competência da fatura)"),
) -> dict:
    """Retorna a bandeira tarifária vigente na competência (ou null)."""
    from fastapi import HTTPException

    try:
        data_dt = date.fromisoformat(competencia)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"competência inválida: {competencia!r}")

    try:
        bandeira = repo.buscar_bandeira(data_dt)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"falha ao consultar bandeira: {exc}")

    if bandeira is None:
        return {
            "competencia": competencia,
            "bandeira": None,
            "valor_kwh": 0.0,
            "valor_mwh": 0.0,
            "observacao": "Sem bandeira para competências anteriores a jan/2015.",
        }
    nome, valor_kwh, valor_mwh = bandeira
    return {
        "competencia": competencia,
        "bandeira": nome,
        "valor_kwh": valor_kwh,
        "valor_mwh": valor_mwh,
    }


@router.get("/bandeiras", tags=["consulta"])
def listar_bandeiras(
    repo: _Repo,
    competencia: str = Query(..., description="AAAA-MM-DD (competência da fatura)"),
) -> dict:
    """Retorna as opções de bandeira e seus valores vigentes na competência."""
    from fastapi import HTTPException

    try:
        data_dt = date.fromisoformat(competencia)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"competência inválida: {competencia!r}")

    try:
        valores = repo.buscar_bandeiras(data_dt)
        ativa = repo.buscar_bandeira(data_dt)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"falha ao consultar bandeiras: {exc}")

    return {
        "competencia": competencia,
        "ativa": ativa[0] if ativa else None,
        "opcoes": [
            {"bandeira": nome, "valor_kwh": valor}
            for nome, valor in valores.items()
        ],
    }


@router.get("/modalidades", response_model=list[str], tags=["consulta"])
def listar_modalidades(repo: _Repo) -> list[str]:
    """Modalidades tarifárias presentes no banco."""
    return repo.listar_modalidades()


@router.get("/classes", response_model=list[str], tags=["consulta"])
def listar_classes(repo: _Repo) -> list[str]:
    """Classes tarifárias presentes no banco."""
    return repo.listar_classes()


@router.get("/componentes", response_model=list[str], tags=["consulta"])
def listar_componentes(repo: _Repo) -> list[str]:
    """Componentes tarifários presentes no banco (TE/TUSD)."""
    return repo.listar_componentes()


@router.get("/bases-tarifarias", response_model=list[str], tags=["consulta"])
def listar_bases_tarifarias(repo: _Repo) -> list[str]:
    """Bases tarifárias presentes no banco."""
    return repo.listar_bases_tarifarias()


@router.get("/acessantes", response_model=list[str], tags=["consulta"])
def listar_acessantes(repo: _Repo) -> list[str]:
    """Acessantes presentes no banco (útil p/ estudos de geração/GD)."""
    return repo.listar_acessantes()

