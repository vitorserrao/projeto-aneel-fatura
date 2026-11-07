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
from infra.database import get_session_factory
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
from services.epi_service import EPIService
from services.otimizacao_service import OtimizacaoService

router = APIRouter()


def _calculo_service() -> CalculoService:
    # get_session_factory() é compartilhada: uma engine (um pool) por processo.
    # create_session_factory() abriria uma engine nova por request e esgotaria
    # o max_connections do PostgreSQL (ver tests/integration/test_api_conexoes.py).
    return CalculoService(TarifaRepository(get_session_factory()))


_Calculo = Annotated[CalculoService, Depends(_calculo_service)]


def _epi_service() -> EPIService:
    repo = TarifaRepository(get_session_factory())
    return EPIService(repo, OtimizacaoService(CalculoService(repo)))


_Epi = Annotated[EPIService, Depends(_epi_service)]


def _para_core(consumidor: Consumidor) -> CoreConsumidor:
    # Fallback Azul × Verde: se o perfil não informar a demanda POR POSTO
    # (exigida pela Azul) mas informar a demanda ÚNICA (Verde), usa o mesmo
    # valor para ponta e fora de ponta. Se o usuário informar o split
    # (ex.: colunas HP/HFP do "Histórico de Consumo" da fatura), prevalece.
    if not consumidor.demanda_ponta_kw and not consumidor.demanda_fora_ponta_kw:
        demanda_ponta_kw = consumidor.demanda_medida_unica_kw
        demanda_fora_ponta_kw = consumidor.demanda_medida_unica_kw
    else:
        demanda_ponta_kw = consumidor.demanda_ponta_kw
        demanda_fora_ponta_kw = consumidor.demanda_fora_ponta_kw

    if (
        not consumidor.demanda_contratada_ponta_kw
        and not consumidor.demanda_contratada_fora_ponta_kw
    ):
        demanda_contratada_ponta_kw = consumidor.demanda_contratada_unica_kw
        demanda_contratada_fora_ponta_kw = consumidor.demanda_contratada_unica_kw
    else:
        demanda_contratada_ponta_kw = consumidor.demanda_contratada_ponta_kw
        demanda_contratada_fora_ponta_kw = consumidor.demanda_contratada_fora_ponta_kw

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
        consumo_intermediario_kwh=consumidor.consumo_intermediario_kwh,
        demanda_ponta_kw=demanda_ponta_kw,
        demanda_fora_ponta_kw=demanda_fora_ponta_kw,
        demanda_contratada_ponta_kw=demanda_contratada_ponta_kw,
        demanda_contratada_fora_ponta_kw=demanda_contratada_fora_ponta_kw,
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
        reativo_energia_capacitiva_kvArh=consumidor.reativo_energia_capacitiva_kvArh,
        reativo_demanda_capacitiva_kvAr=consumidor.reativo_demanda_capacitiva_kvAr,
        atividade=consumidor.atividade,
        tipo_ligacao=consumidor.tipo_ligacao,
        pre_pagamento=consumidor.pre_pagamento,
        potencia_transformadores_kva=consumidor.potencia_transformadores_kva,
        cooperativa_eletrificacao_rural=consumidor.cooperativa_eletrificacao_rural,
        hotelaria_turismo=consumidor.hotelaria_turismo,
        carga_refletores_kw=consumidor.carga_refletores_kw,
        carga_instalada_total_kw=consumidor.carga_instalada_total_kw,
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
        default="fora",
        description="Tipo de faturamento do ICMS: 'dentro' (aditiva) ou 'fora' (multiplicativa)",
    ),
    reativos_direto: bool = Query(
        default=False,
        description="Modo de faturas antigas: reativo_* são excedentes prontos "
        "(kVArh/kVAr) cobrados com as tarifas informadas abaixo",
    ),
    tarifa_reativo_energia_r_kvarh: float | None = Query(
        default=None, ge=0, description="Tarifa do excedente de energia reativa (R$/kVArh)"
    ),
    tarifa_reativo_demanda_r_kvar: float | None = Query(
        default=None, ge=0, description="Tarifa do excedente de demanda reativa (R$/kVAr)"
    ),
    arredondar_centavos: bool = Query(
        default=False,
        description="Arredondar o custo de cada linha a centavos (2 casas)",
    ),
    demanda_isenta_icms: bool = Query(
        default=False,
        description="Dividir a demanda em parcela normal e parcela isenta de ICMS",
    ),
    demanda_isenta_icms_kw: float | None = Query(
        default=None,
        ge=0,
        description="Quantidade (kW) da parcela isenta de ICMS; se omitido, "
        "o motor usa faturada − medida",
    ),
    tributar_reativos: bool = Query(
        default=False,
        description="Aplicar PIS/COFINS/ICMS também às linhas de reativos",
    ),
) -> FaturaResponse:
    """Calcula a fatura ACR diretamente de um perfil de consumidor."""
    try:
        core_consumidor = _para_core(consumidor)
        # O dataset grafa as modalidades com inicial maiúscula ("Azul", "Verde");
        # o schema aceita tanto isso quanto caixa alta.
        modalidade_real = modalidade.strip().title()
        resultado, nao_mapeadas, avisos = svc.calcular_detalhado(
            core_consumidor, modalidade_real, base_tarifaria,
            aplicar_tributos=aplicar_tributos,
            pis=pis,
            cofins=cofins,
            icms=icms,
            tipo_icms=tipo_icms,
            reativos_direto=reativos_direto,
            tarifa_reativo_energia_r_kvarh=tarifa_reativo_energia_r_kvarh,
            tarifa_reativo_demanda_r_kvar=tarifa_reativo_demanda_r_kvar,
            arredondar_centavos=arredondar_centavos,
            demanda_isenta_icms=demanda_isenta_icms,
            demanda_isenta_icms_kw=demanda_isenta_icms_kw,
            tributar_reativos=tributar_reativos,
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
    for tipo, mensagem in avisos:
        notas.append(Nota(tipo=tipo, mensagem=mensagem))
    return FaturaResponse(fatura=fatura, notas=notas)


def _fatura_out(
    resultado,
    base_tarifaria: str,
    nao_mapeadas: int = 0,
    pi: float | None = None,
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
        pi=pi,
    )


@router.post(
    "/calculo/comparar", response_model=ComparacaoResponse, tags=["calculo"]
)
def comparar_modalidades(
    consumidor: Consumidor,
    svc: _Calculo,
    epi: _Epi,
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
        default="fora",
        description="Tipo de faturamento do ICMS: 'dentro' (aditiva) ou 'fora' (multiplicativa)",
    ),
    reativos_direto: bool = Query(
        default=False,
        description="Modo de faturas antigas: reativo_* são excedentes prontos "
        "(kVArh/kVAr) cobrados com as tarifas informadas abaixo",
    ),
    tarifa_reativo_energia_r_kvarh: float | None = Query(
        default=None, ge=0, description="Tarifa do excedente de energia reativa (R$/kVArh)"
    ),
    tarifa_reativo_demanda_r_kvar: float | None = Query(
        default=None, ge=0, description="Tarifa do excedente de demanda reativa (R$/kVAr)"
    ),
    k: float = Query(
        default=0.03, ge=0, description="Perdas na migração ao ACL (fração)"
    ),
    arredondar_centavos: bool = Query(
        default=False,
        description="Arredondar o custo de cada linha a centavos (2 casas)",
    ),
    demanda_isenta_icms: bool = Query(
        default=False,
        description="Dividir a demanda em parcela normal e parcela isenta de ICMS",
    ),
    demanda_isenta_icms_kw: float | None = Query(
        default=None,
        ge=0,
        description="Quantidade (kW) da parcela isenta de ICMS; se omitido, "
        "o motor usa faturada − medida",
    ),
    tributar_reativos: bool = Query(
        default=False,
        description="Aplicar PIS/COFINS/ICMS também às linhas de reativos",
    ),
    encargos: float = Query(
        default=0.0, ge=0, description="Encargos do ACL por energia (R$/MWh, ex.: ESS)"
    ),
    opex_mensal: float = Query(default=0.0, ge=0, description="OPEX do ACL (R$/mês)"),
    capex: float = Query(default=0.0, ge=0, description="CAPEX do ACL (R$)"),
    horizonte_meses: int = Query(
        default=60, gt=0, description="Horizonte de amortização do CAPEX (meses)"
    ),
) -> ComparacaoResponse:
    """Compara Azul × Verde × Optante B (Grupo A) e calcula o PI de cada modalidade."""
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
            reativos_direto=reativos_direto,
            tarifa_reativo_energia_r_kvarh=tarifa_reativo_energia_r_kvarh,
            tarifa_reativo_demanda_r_kvar=tarifa_reativo_demanda_r_kvar,
            arredondar_centavos=arredondar_centavos,
            demanda_isenta_icms=demanda_isenta_icms,
            demanda_isenta_icms_kw=demanda_isenta_icms_kw,
            tributar_reativos=tributar_reativos,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    disponiveis = []
    for f in resultado.disponiveis:
        pi = None
        try:
            pi = epi.calcular(
                core_consumidor,
                pis=pis,
                cofins=cofins,
                icms=icms,
                k=k,
                encargos=encargos,
                opex_mensal=opex_mensal,
                capex=capex,
                horizonte_meses=horizonte_meses,
                modalidade=f.modalidade,
            ).resultado.pi
        except ValueError:
            # Modalidade sem TE ponta/fora ponta disponível (ex.: Optante B
            # sem tarifa monômia no banco) — a fatura segue sem o PI.
            pi = None
        disponiveis.append(_fatura_out(f, base_tarifaria, pi=pi))

    comparacao = ComparacaoOut(
        disponiveis=disponiveis,
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
