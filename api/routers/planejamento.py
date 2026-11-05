"""Routers do planejamento anual de modalidades."""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from core.models import Consumidor as CoreConsumidor
from infra.database import create_session_factory
from infra.repositories.tarifa_repository import TarifaRepository
from schemas.planejamento import PlanejamentoSolicitacao
from services.calculo_service import CalculoService
from services.epi_service import EPIService
from services.otimizacao_service import OtimizacaoService
from services.planejamento_service import PlanejamentoService

router = APIRouter()


def _planejamento_service() -> PlanejamentoService:
    repo = TarifaRepository(create_session_factory())
    calculo = CalculoService(repo)
    return PlanejamentoService(
        calculo,
        EPIService(repo, OtimizacaoService(calculo)),
    )


_Planejamento = Annotated[PlanejamentoService, Depends(_planejamento_service)]


@router.post("/planejamento/comparar", tags=["planejamento"])
def comparar_planejamento_anual(
    solicitacao: PlanejamentoSolicitacao, servico: _Planejamento
) -> dict:
    """Compara Azul × Verde × Optante B em 12 meses, com dois cenários."""
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
        atividade=solicitacao.atividade,
        tipo_ligacao=solicitacao.tipo_ligacao,
    )
    meses = [m.model_dump() for m in solicitacao.meses]

    try:
        planejamento, pi_por_modalidade = servico.comparar(
            perfil_base,
            meses,
            pis=solicitacao.pis,
            cofins=solicitacao.cofins,
            icms=solicitacao.icms,
            tipo_icms=solicitacao.tipo_icms,
            demanda_isenta_icms=solicitacao.demanda_isenta_icms,
            tributar_reativos=solicitacao.tributar_reativos,
            modalidade_atual=solicitacao.modalidade_atual,
            dc_atual_verde=solicitacao.dc_atual_verde,
            dc_atual_azul_ponta=solicitacao.dc_atual_azul_ponta,
            dc_atual_azul_fora=solicitacao.dc_atual_azul_fora,
            k=solicitacao.k,
            encargos=solicitacao.encargos,
            opex_mensal=solicitacao.opex_mensal,
            capex=solicitacao.capex,
            horizonte_meses=solicitacao.horizonte_meses,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "melhor_contrato_atual": planejamento.melhor_contrato_atual,
        "melhor_demanda_otimizada": planejamento.melhor_demanda_otimizada,
        "ganho": {
            "total": planejamento.ganho.ganho_total,
            "demanda": planejamento.ganho.ganho_demanda,
            "modalidade": planejamento.ganho.ganho_modalidade,
        },
        "modalidades": [
            {
                "modalidade": m.modalidade,
                "custo_contrato_atual": m.custo_contrato_atual,
                "custo_demanda_otimizada": m.custo_demanda_otimizada,
                "dc_atual": m.dc_atual,
                "dc_otima": m.dc_otima,
                "pi": pi_por_modalidade.get(m.modalidade),
            }
            for m in planejamento.modalidades
        ],
        "equilibrio": (
            {
                "dp_eq": planejamento.equilibrio.dp_eq,
                "mensagem": planejamento.equilibrio.mensagem,
            }
            if planejamento.equilibrio
            else None
        ),
        "avisos": list(planejamento.avisos),
    }
