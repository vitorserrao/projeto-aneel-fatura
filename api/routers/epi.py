"""Routers de PI (Preço de Indiferença) — expõe o ``EPIService``.

Recebe o perfil ACR + parâmetros do PI e devolve o preço de indiferença
(R$/MWh) com os componentes do cálculo (docs/epi.md).
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from core.models import Consumidor as CoreConsumidor
from infra.database import create_session_factory
from infra.repositories.tarifa_repository import TarifaRepository
from schemas.epi import EPIResultado, EPISolicitacao
from services.calculo_service import CalculoService
from services.epi_service import EPIService
from services.otimizacao_service import OtimizacaoService

router = APIRouter()


def _epi_service() -> EPIService:
    repo = TarifaRepository(create_session_factory())
    return EPIService(repo, OtimizacaoService(CalculoService(repo)))


_Epi = Annotated[EPIService, Depends(_epi_service)]


@router.post("/epi/calcular", response_model=EPIResultado, tags=["epi"])
def calcular_epi(solicitacao: EPISolicitacao, service: _Epi) -> EPIResultado:
    """Calcula o Preço de Indiferença (PI) para um perfil ACR.

    ``modalidade=None`` usa a modalidade de menor custo no ACR; informe uma
    modalidade (Azul/Verde/Optante B) para fixá-la.
    """
    perfil = CoreConsumidor(
        distribuidora=solicitacao.distribuidora,
        subgrupo=solicitacao.subgrupo,
        classe="Não se aplica",
        data_referencia=(
            date.fromisoformat(solicitacao.data_referencia)
            if solicitacao.data_referencia
            else None
        ),
        detalhe="Não se aplica",
        consumo_ponta_kwh=solicitacao.consumo_ponta_kwh,
        consumo_fora_ponta_kwh=solicitacao.consumo_fora_ponta_kwh,
    )

    try:
        resultado = service.calcular(
            perfil,
            pis=solicitacao.pis,
            cofins=solicitacao.cofins,
            icms=solicitacao.icms,
            k=solicitacao.k,
            encargos=solicitacao.encargos,
            opex_mensal=solicitacao.opex_mensal,
            capex=solicitacao.capex,
            horizonte_meses=solicitacao.horizonte_meses,
            modalidade=solicitacao.modalidade,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    r = resultado.resultado
    return EPIResultado(
        pi=r.pi,
        modalidade=resultado.modalidade,
        bandeira_r_mwh=resultado.bandeira_r_mwh,
        e_mwh=r.e,
        c_te=r.c_te,
        c_e_acr=r.c_e_acr,
        custos_acl=r.custos_acl,
        base_acl=r.base_acl,
        aviso=r.aviso,
    )
