"""Router da comparação Verde × Azul (a partir da fatura Verde)."""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from core.models import Consumidor as CoreConsumidor
from infra.database import get_session_factory
from infra.repositories.tarifa_repository import TarifaRepository
from schemas.comparacao import (
    ComparacaoVerdeAzulOut,
    ComparacaoVerdeAzulSolicitacao,
    DcOtimasOut,
)
from services.calculo_service import CalculoService
from services.comparacao_verde_azul import ComparacaoVerdeAzulService

router = APIRouter()


def _servico() -> ComparacaoVerdeAzulService:
    repo = TarifaRepository(get_session_factory())
    return ComparacaoVerdeAzulService(CalculoService(repo))


_Servico = Annotated[ComparacaoVerdeAzulService, Depends(_servico)]


@router.post(
    "/comparacao/verde-azul",
    response_model=ComparacaoVerdeAzulOut,
    tags=["comparacao"],
)
def comparar_verde_azul(
    solicitacao: ComparacaoVerdeAzulSolicitacao, servico: _Servico
) -> ComparacaoVerdeAzulOut:
    """Simula a modalidade Azul a partir de faturas Verde e devolve o veredito."""
    perfil_base = CoreConsumidor(
        distribuidora=solicitacao.distribuidora,
        subgrupo=solicitacao.subgrupo,
        classe=solicitacao.classe,
        data_referencia=(
            date.fromisoformat(solicitacao.data_referencia)
            if solicitacao.data_referencia
            else None
        ),
        detalhe=solicitacao.detalhe,
    )
    meses = [m.model_dump() for m in solicitacao.meses]
    try:
        resultado = servico.comparar(
            perfil_base,
            meses,
            pis=solicitacao.pis,
            cofins=solicitacao.cofins,
            icms=solicitacao.icms,
            tipo_icms=solicitacao.tipo_icms,
            contratada_atual=solicitacao.contratada_atual,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ComparacaoVerdeAzulOut(
        nivel=resultado.nivel,
        veredito=resultado.veredito,
        verde_atual=resultado.verde_atual,
        verde_otimizada=resultado.verde_otimizada,
        azul=resultado.azul,
        dc_otimas=DcOtimasOut(**resultado.dc_otimas),
        dp_equilibrio=resultado.dp_equilibrio,
        meses_analisados=resultado.meses_analisados,
        avisos=list(resultado.avisos),
    )
