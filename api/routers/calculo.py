"""Routers de cálculo de fatura (orquestração repo → adapter → core).

Recebe o perfil (``schemas/consumidor.Consumidor``) e devolve a fatura
(``schemas/fatura.FaturaResponse``) com as linhas de cobrança do simulador.
Não contém fórmula tarifária — apenas expõe o ``CalculoService``.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from core.models import Consumidor as CoreConsumidor
from infra.database import create_session_factory
from infra.repositories.tarifa_repository import TarifaRepository
from schemas.consumidor import Consumidor
from schemas.fatura import (
    ComparacaoOut,
    ComparacaoResponse,
    FaturaOut,
    FaturaResponse,
    LinhaFaturaOut,
    ModalidadeIndisponivelOut,
    Nota,
)
from services.calculo_service import CalculoService

router = APIRouter()


def _calculo_service() -> CalculoService:
    return CalculoService(TarifaRepository(create_session_factory()))


_Calculo = Annotated[CalculoService, Depends(_calculo_service)]


def _para_core(consumidor: Consumidor) -> CoreConsumidor:
    return CoreConsumidor(
        distribuidora=consumidor.distribuidora,
        subgrupo=consumidor.subgrupo,
        classe=consumidor.classe,
        data_referencia=(
            date.fromisoformat(consumidor.data_referencia)
            if consumidor.data_referencia
            else date.today()
        ),
        subclasse=consumidor.subclasse,
        detalhe=consumidor.detalhe,
        consumo_ponta_kwh=consumidor.consumo_ponta_kwh,
        consumo_fora_ponta_kwh=consumidor.consumo_fora_ponta_kwh,
        demanda_ponta_kw=consumidor.demanda_ponta_kw,
        demanda_fora_ponta_kw=consumidor.demanda_fora_ponta_kw,
        demanda_contratada_ponta_kw=consumidor.demanda_contratada_ponta_kw,
        demanda_contratada_fora_ponta_kw=consumidor.demanda_contratada_fora_ponta_kw,
        demanda_medida_unica_kw=consumidor.demanda_medida_unica_kw,
        demanda_contratada_unica_kw=consumidor.demanda_contratada_unica_kw,
        percentual_mes_anterior=consumidor.percentual_mes_anterior,
        bandeira_adicional_r_kwh=consumidor.bandeira_adicional_r_kwh,
        cip_cosip_rs=consumidor.cip_cosip_rs,
        outros_rs=consumidor.outros_rs,
        reativo_energia_ponta_kvArh=consumidor.reativo_energia_ponta_kvArh,
        reativo_energia_fora_ponta_kvArh=consumidor.reativo_energia_fora_ponta_kvArh,
        reativo_demanda_ponta_kvAr=consumidor.reativo_demanda_ponta_kvAr,
        reativo_demanda_fora_ponta_kvAr=consumidor.reativo_demanda_fora_ponta_kvAr,
    )


@router.post("/calculo/fatura", response_model=FaturaResponse, tags=["calculo"])
def calcular_fatura(
    consumidor: Consumidor,
    svc: _Calculo,
    modalidade: str = Query(
        default="AZUL", description="Modalidade a simular (AZUL, VERDE)"
    ),
    base_tarifaria: str = Query(
        default="Tarifa de Aplicação", description="Base da fatura"
    ),
    aplicar_tributos: bool = Query(
        default=False,
        description="Aplicar PIS/COFINS/ICMS (fórmula oficial aditiva)",
    ),
    pis: float = Query(default=0.0, ge=0, le=1, description="PIS/PASEP (fração)"),
    cofins: float = Query(default=0.0, ge=0, le=1, description="COFINS (fração)"),
    icms: float = Query(default=0.0, ge=0, le=1, description="ICMS (fração)"),
    tipo_icms: str = Query(
        default="dentro",
        description="Tipo de faturamento do ICMS: 'dentro' (aditiva) ou 'fora' (multiplicativa)",
    ),
) -> FaturaResponse:
    """Calcula a fatura ACR diretamente de um perfil de consumidor."""
    try:
        core_consumidor = _para_core(consumidor)
        # O dataset grafa as modalidades com inicial maiúscula ("Azul", "Verde");
        # o schema aceita tanto isso quanto caixa alta.
        modalidade_real = modalidade.strip().title()
        resultado, nao_mapeadas = svc.calcular_detalhado(
            core_consumidor, modalidade_real, base_tarifaria,
            aplicar_tributos=aplicar_tributos,
            pis=pis,
            cofins=cofins,
            icms=icms,
            tipo_icms=tipo_icms,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    fatura = FaturaOut(
        modalidade=resultado.modalidade,
        base_tarifaria=base_tarifaria,
        linhas=[
            LinhaFaturaOut(
                descricao=l.descricao,
                categoria=l.categoria,
                quantidade=l.quantidade,
                tarifa=l.tarifa,
                custo=l.custo,
            )
            for l in resultado.linhas
        ],
        custo_tarifas=resultado.custo_tarifas,
        custo_total=resultado.custo_total,
        aplicar_tributos=resultado.aplicar_tributos,
        tarifas_nao_mapeadas=len(nao_mapeadas),
    )
    notas = []
    if nao_mapeadas:
        notas.append(
            Nota(
                tipo="tarifas_nao_mapeadas",
                mensagem=(
                    f"{len(nao_mapeadas)} tarifa(s) vigente(s) com posto "
                    "ainda não suportado ficaram fora da fatura (P5)."
                ),
            )
        )
    return FaturaResponse(fatura=fatura, notas=notas)


def _fatura_out(
    resultado,
    base_tarifaria: str,
    nao_mapeadas: int = 0,
) -> FaturaOut:
    """Converte um ``ResultadoFatura`` do core no contrato de saída."""
    return FaturaOut(
        modalidade=resultado.modalidade,
        base_tarifaria=base_tarifaria,
        linhas=[
            LinhaFaturaOut(
                descricao=l.descricao,
                categoria=l.categoria,
                quantidade=l.quantidade,
                tarifa=l.tarifa,
                custo=l.custo,
            )
            for l in resultado.linhas
        ],
        custo_tarifas=resultado.custo_tarifas,
        custo_total=resultado.custo_total,
        aplicar_tributos=resultado.aplicar_tributos,
        tarifas_nao_mapeadas=nao_mapeadas,
    )


@router.post(
    "/calculo/comparar", response_model=ComparacaoResponse, tags=["calculo"]
)
def comparar_modalidades(
    consumidor: Consumidor,
    svc: _Calculo,
    base_tarifaria: str = Query(
        default="Tarifa de Aplicação", description="Base da fatura"
    ),
    aplicar_tributos: bool = Query(
        default=False,
        description="Aplicar PIS/COFINS/ICMS a todas as modalidades",
    ),
    pis: float = Query(default=0.0, ge=0, le=1, description="PIS/PASEP (fração)"),
    cofins: float = Query(default=0.0, ge=0, le=1, description="COFINS (fração)"),
    icms: float = Query(default=0.0, ge=0, le=1, description="ICMS (fração)"),
    tipo_icms: str = Query(
        default="dentro",
        description="Tipo de faturamento do ICMS: 'dentro' (aditiva) ou 'fora' (multiplicativa)",
    ),
) -> ComparacaoResponse:
    """Compara Azul × Verde (Grupo A) para o perfil e ranqueia por menor custo."""
    try:
        core_consumidor = _para_core(consumidor)
        resultado = svc.comparar_modalidades(
            core_consumidor,
            base_tarifaria=base_tarifaria,
            aplicar_tributos=aplicar_tributos,
            pis=pis,
            cofins=cofins,
            icms=icms,
            tipo_icms=tipo_icms,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    comparacao = ComparacaoOut(
        disponiveis=[
            _fatura_out(f, base_tarifaria) for f in resultado.disponiveis
        ],
        indisponiveis=[
            ModalidadeIndisponivelOut(
                modalidade=i.modalidade,
                motivo=i.motivo,
            )
            for i in resultado.indisponiveis
        ],
        melhor=(
            resultado.melhor.modalidade if resultado.melhor is not None else None
        ),
    )
    return ComparacaoResponse(
        comparacao=comparacao,
        notas=[],
    )
