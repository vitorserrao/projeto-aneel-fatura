"""Motor de cálculo ACR determinístico.

Implementa apenas a aplicação linear de parcelas tarifárias normalizadas:

    custo = quantidade × valor unitário

A quantidade é determinada pela ``grandeza`` (ENERGIA/DEMANDA) e pelo ``posto``
(PONTA/FORA PONTA) da parcela, com conversão dimensional a partir da unidade.

Esta é a premissa estrutural A1 (docs/premissas.md) — não é uma regra
regulatória. As regras regulatórias de componentização/tratamento de TE e
TUSD, faturamento de demanda e tributação continuam pendentes
(docs/premissas.md, P1/P3/P5).
"""

from __future__ import annotations

from typing import Iterable

from .models import (
    COMPONENTE_TUSD,
    GRANDEZA_DEMANDA,
    GRANDEZA_ENERGIA,
    POSTO_FORA_PONTA,
    POSTO_PONTA,
    UNIDADE_R_KW,
    UNIDADE_R_KWH,
    UNIDADE_R_MWH,
    Consumidor,
    LinhaFatura,
    ParcelaCusto,
    ResultadoCalculo,
    ResultadoFatura,
)
from .tarifas import ParcelaTarifaria

_FATOR_KWH_PARA_MWH = 0.001


class UnidadeTarifariaNaoSuportada(ValueError):
    """Unidade incompatível com a grandeza da parcela tarifária."""


def _consumo_kwh(consumidor: Consumidor, posto: str) -> float:
    # ``posto`` já foi validado em ParcelaTarifaria: só PONTA ou FORA PONTA.
    if posto == POSTO_PONTA:
        return consumidor.consumo_ponta_kwh
    return consumidor.consumo_fora_ponta_kwh


def _demanda_kw(
    consumidor: Consumidor,
    posto: str,
    piso: float = 0.0,
    demanda_unica: bool = False,
) -> float:
    """Demanda FATURÁVEL do posto (maior entre contratada e medida).

    Regra oficial (REN 1.000/2021, arts. 292 e 301). O ``piso`` reproduz a
    simplificação do XLSM (`IF(faturado=0, 30, valor)`); default 0 = regra
    oficial pura. ``demanda_unica`` usa a demanda ÚNICA do consumidor
    (`máx(medida_única, contratada_única)`) — Verde (REN 1.000/2021: uma
    única tarifa de demanda).
    """
    if demanda_unica:
        return max(consumidor.demanda_faturavel_unica_kw, piso)
    return max(consumidor.demanda_faturavel_kw(posto), piso)


def _quantidade(
    parcela: ParcelaTarifaria,
    consumidor: Consumidor,
    piso: float = 0.0,
    demanda_unica: bool = False,
) -> float:
    """Quantidade na unidade da tarifa, derivada da grandeza e do posto."""
    if parcela.grandeza == GRANDEZA_ENERGIA:
        consumo_kwh = _consumo_kwh(consumidor, parcela.posto)
        if parcela.unidade == UNIDADE_R_MWH:
            return consumo_kwh * _FATOR_KWH_PARA_MWH
        if parcela.unidade == UNIDADE_R_KWH:
            return consumo_kwh
        raise UnidadeTarifariaNaoSuportada(
            f"unidade {parcela.unidade!r} não suportada para ENERGIA; "
            f"use {UNIDADE_R_MWH!r} ou {UNIDADE_R_KWH!r}"
        )

    if parcela.grandeza == GRANDEZA_DEMANDA:
        if parcela.unidade == UNIDADE_R_KW:
            return _demanda_kw(consumidor, parcela.posto, piso, demanda_unica)
        raise UnidadeTarifariaNaoSuportada(
            f"unidade {parcela.unidade!r} não suportada para DEMANDA; "
            f"use {UNIDADE_R_KW!r}"
        )

    # Defensivo: grandeza já validada na construção de ParcelaTarifaria.
    raise ValueError(f"grandeza não suportada: {parcela.grandeza!r}")


def calcular_parcela(
    parcela: ParcelaTarifaria,
    consumidor: Consumidor,
    piso: float = 0.0,
    demanda_unica: bool = False,
) -> ParcelaCusto:
    """Calcula uma parcela de custo (quantidade × tarifa), sem arredondamento.

    Premissa estrutural A4 (docs/premissas.md): o core não aplica política de
    arredondamento; resultados são ponto flutuante determinístico.
    """
    quantidade = _quantidade(parcela, consumidor, piso, demanda_unica)
    custo = quantidade * parcela.valor
    return ParcelaCusto(
        componente=parcela.componente,
        grandeza=parcela.grandeza,
        posto=parcela.posto,
        quantidade=quantidade,
        tarifa=parcela.valor,
        custo=custo,
    )


def calcular_custo_acr(
    consumidor: Consumidor,
    modalidade: str,
    parcelas: Iterable[ParcelaTarifaria],
) -> ResultadoCalculo:
    """Calcula energia, demanda, TE, TUSD e custo total ACR (determinístico).

    Args:
        consumidor: perfil do consumidor.
        modalidade: modalidade tarifária simulada (ex.: AZUL, VERDE).
        parcelas: parcelas tarifárias normalizadas aplicáveis ao consumidor.

    Returns:
        ResultadoCalculo com as parcelas calculadas e totais por componente
        (TE/TUSD) e por grandeza (energia/demanda).

    Raises:
        ValueError: modalidade vazia ou nenhuma parcela fornecida.
        UnidadeTarifariaNaoSuportada: unidade incompatível com a grandeza.
    """
    if not modalidade.strip():
        raise ValueError("modalidade não pode ser vazia")

    lista = list(parcelas)
    if not lista:
        raise ValueError("nenhuma parcela tarifária fornecida")

    calculadas = tuple(calcular_parcela(parcela, consumidor) for parcela in lista)
    return ResultadoCalculo(modalidade=modalidade.strip(), parcelas=calculadas)


# ---------------------------------------------------------------------------
# Fatura completa (estrutura do Simulador de Fatura do projeto anterior)
# ---------------------------------------------------------------------------
# Esta função reimplementa a estrutura de cobrança do simulador (linhas por
# modalidade + adicionais). É uma REFERÊNCIA metodológica, não a regra oficial
# de faturamento: as fórmulas de ultrapassagem/reativos seguem a REN 1.000/2021
# quando aplicável, e a tributação é opcional (base líquida por padrão).

_TOLERANCIA_ULTRAPASSAGEM = 0.05  # REN 1.000/2021 (consumidor geral)
_FATOR_POTENCIA_REF = 0.92  # REN 1.000/2021

# Subgrupos do Grupo A em que a Verde é admitida (REN 1.000/2021, art. 220).
_SUBGRUPOS_VERDE = {"A3A", "A4", "AS"}

# Modalidades do Grupo A suportadas pelo sistema.
MODALIDADES_GRUPO_A = ("AZUL", "VERDE")


def modalidades_elegiveis(consumidor) -> list[str]:
    """Modalidades do Grupo A elegíveis para o perfil.

    Regras (REN 1.000/2021):
    - Azul: todos os subgrupos A.
    - Verde: apenas A3a/A4/AS.
    """
    elegiveis = ["AZUL"]
    if consumidor.subgrupo.strip().upper() in _SUBGRUPOS_VERDE:
        elegiveis.append("VERDE")
    return elegiveis


def motivo_indisponibilidade(modalidade: str, consumidor) -> str | None:
    """Por que uma modalidade do Grupo A não é elegível (ou None se elegível).

    Mantém a regra centralizada e testável — usada pela API de comparação.
    """
    m = modalidade.strip().upper()
    if m == "AZUL":
        return None  # todos os subgrupos A
    if m == "VERDE":
        if consumidor.subgrupo.strip().upper() in _SUBGRUPOS_VERDE:
            return None
        return (
            "Verde é aplicável apenas aos subgrupos A3a, A4 e AS "
            f"(perfil: {consumidor.subgrupo.strip().upper()})"
        )
    return f"Modalidade {modalidade!r} fora do escopo do Grupo A (Azul/Verde)"


def _tarifa_demanda_posto(parcelas, componente, posto):
    """Tarifa de demanda (R$/kW) do componente/posto, ou None."""
    for p in parcelas:
        if (
            p.componente == componente
            and p.grandeza == GRANDEZA_DEMANDA
            and p.posto == posto
        ):
            return p.valor
    return None


def _linhas_tarifarias(
    consumidor, parcelas, piso=0.0, ratear_mes=True, demanda_unica=False
):
    linhas = []
    frac_ant = consumidor.percentual_mes_anterior if ratear_mes else 0.0
    for p in parcelas:
        if p.grandeza == GRANDEZA_ENERGIA and ratear_mes:
            # Rateio entre leituras (XLSM: F20=I6*I13 e F21=I6*(1-I13)):
            # uma linha para o mês anterior e outra para o mês atual.
            consumo = _consumo_kwh(consumidor, p.posto)
            q_ant = consumo * frac_ant
            q_atual = consumo * (1.0 - frac_ant)
            unidades = (UNIDADE_R_MWH, UNIDADE_R_KWH)
            fator = _FATOR_KWH_PARA_MWH if p.unidade == UNIDADE_R_MWH else 1.0
            if p.unidade not in unidades:
                raise UnidadeTarifariaNaoSuportada(
                    f"unidade {p.unidade!r} não suportada para ENERGIA"
                )
            rotulo = f"{p.componente} {p.grandeza} {p.posto}"
            if frac_ant > 0 and frac_ant < 1.0:
                if q_ant > 0:
                    linhas.append(
                        LinhaFatura(
                            descricao=f"{rotulo} (mês anterior)",
                            categoria="TARIFA",
                            quantidade=q_ant * fator,
                            tarifa=p.valor,
                            custo=q_ant * fator * p.valor,
                        )
                    )
                if q_atual > 0:
                    linhas.append(
                        LinhaFatura(
                            descricao=f"{rotulo} (mês atual)",
                            categoria="TARIFA",
                            quantidade=q_atual * fator,
                            tarifa=p.valor,
                            custo=q_atual * fator * p.valor,
                        )
                    )
            else:
                # Sem rateio efetivo: linha única, rótulo original.
                q = consumo * fator
                if q > 0:
                    linhas.append(
                        LinhaFatura(
                            descricao=rotulo,
                            categoria="TARIFA",
                            quantidade=q,
                            tarifa=p.valor,
                            custo=q * p.valor,
                        )
                    )
            continue
        quantidade = _quantidade(p, consumidor, piso, demanda_unica)
        rotulo = f"{p.componente} {p.grandeza} {p.posto}"
        linhas.append(
            LinhaFatura(
                descricao=rotulo,
                categoria="TARIFA",
                quantidade=quantidade,
                tarifa=p.valor,
                custo=quantidade * p.valor,
            )
        )
    return linhas


def _linha_ultrapassagem(consumidor, parcelas, posto, demanda_unica=False):
    """Linha de ultrapassagem (interpretação B — slide/XLSM).

    Regra adotada (decisão do usuário): gatilho de 5% (só cobra se a medida
    exceder a contratada em mais de 5%), e base = excedente TOTAL
    ``(PAM − PAC)`` — sem descontar a faixa de tolerância. Fator 2× a tarifa
    de demanda. Para a Verde usa os campos ÚNICOS de demanda.
    """
    if demanda_unica:
        medida = consumidor.demanda_medida_unica_kw
        contratada = consumidor.demanda_contratada_unica_kw
        tarifa = _tarifa_demanda_unica(parcelas)
        descricao = "Ultrapassagem de demanda"
    else:
        tarifa = _tarifa_demanda_posto(parcelas, COMPONENTE_TUSD, posto)
        if tarifa is None or tarifa <= 0:
            return None
        medida = (
            consumidor.demanda_ponta_kw
            if posto == POSTO_PONTA
            else consumidor.demanda_fora_ponta_kw
        )
        contratada = (
            consumidor.demanda_contratada_ponta_kw
            if posto == POSTO_PONTA
            else consumidor.demanda_contratada_fora_ponta_kw
        )
        descricao = f"Ultrapassagem de demanda {posto}"

    if tarifa is None or tarifa <= 0:
        return None
    if contratada <= 0:
        return None
    # Gatilho: só cobra quando a medida excede a contratada em mais de 5%.
    if medida <= contratada * (1 + _TOLERANCIA_ULTRAPASSAGEM):
        return None
    # Base: excedente TOTAL (interpretação B do slide/XLSM).
    excedente = medida - contratada
    return LinhaFatura(
        descricao=descricao,
        categoria="ULTRAPASSAGEM",
        quantidade=excedente,
        tarifa=2 * tarifa,
        custo=excedente * 2 * tarifa,
    )


def _tarifa_demanda_unica(parcelas):
    """Tarifa de demanda ÚNICA (R$/kW) para a Verde."""
    for p in parcelas:
        if p.componente == COMPONENTE_TUSD and p.grandeza == GRANDEZA_DEMANDA:
            return p.valor
    return None


def calcular_fatura(
    consumidor,
    modalidade,
    parcelas,
    *,
    pis=0.0,
    cofins=0.0,
    icms=0.0,
    aplicar_tributos=False,
    piso_demanda_kw=0.0,
    ratear_mes=True,
    tarifa_reativos=None,
    demanda_unica=False,
    tipo_icms="dentro",
):
    """Monta a fatura completa de uma modalidade (linhas + totais).

    Reimplementa a estrutura de cobrança do simulador: linhas tarifárias
    (TUSD demanda/energia + TE) + ultrapassagem + bandeira + CIP/COSIP +
    outros + reativos (fp < 0,92). Ajustes desta sprint:

    - ``ratear_mes=True``: o consumo é rateado pelas frações do mês anterior
      (`consumidor.percentual_mes_anterior`) — cada linha de energia passa a
      aparecer DUAS vezes (mês anterior/mês atual), como na planilha
      (`F20 = I6*I13` e `F21 = I6*(1-I13)`).
    - ``piso_demanda_kw``: piso de demanda faturável (simplificação do XLSM,
      `IF(faturado=0, 30, valor)`) — por padrão 0 (regra oficial pura).

    Quando ``aplicar_tributos=True``, aplica a tributação conforme
    ``tipo_icms``:
    - ``"dentro"`` (aditiva, padrão): ``tarifa / (1 − pis − cofins − icms)``
    - ``"fora"`` (multiplicativa, XLSM Fatura-1): 
      ``tarifa / ((1 − pis − cofins) × (1 − icms))``
    """
    if tipo_icms not in ("dentro", "fora"):
        raise ValueError("tipo_icms deve ser 'dentro' ou 'fora'")
    linhas = _linhas_tarifarias(
        consumidor, parcelas, piso=piso_demanda_kw, ratear_mes=ratear_mes,
        demanda_unica=demanda_unica,
    )
    if not any(l.categoria == "TARIFA" for l in linhas):
        raise ValueError(
            "nenhuma tarifa aplicável encontrada/vigente para o perfil"
        )

    # Ultrapassagem de demanda.
    if demanda_unica:
        # Verde: UMA única ultrapassagem (campos únicos).
        ul = _linha_ultrapassagem(consumidor, parcelas, POSTO_PONTA, True)
        if ul is not None:
            linhas.append(ul)
    else:
        for posto in (POSTO_PONTA, POSTO_FORA_PONTA):
            ul = _linha_ultrapassagem(consumidor, parcelas, posto, False)
            if ul is not None:
                linhas.append(ul)

    # Bandeira tarifária (adicional por kWh consumido).
    if consumidor.bandeira_adicional_r_kwh > 0:
        consumo_kwh = consumidor.consumo_total_kwh
        linhas.append(
            LinhaFatura(
                descricao="Adicional Bandeira Tarifária",
                categoria="BANDEIRA",
                quantidade=consumo_kwh,
                tarifa=consumidor.bandeira_adicional_r_kwh,
                custo=consumo_kwh * consumidor.bandeira_adicional_r_kwh,
            )
        )

    # CIP/COSIP (imposto municipal, valor fixo em R$).
    if consumidor.cip_cosip_rs > 0:
        linhas.append(
            LinhaFatura(
                descricao="Imposto Municipal — CIP/COSIP",
                categoria="ENCARGO",
                quantidade=1.0,
                tarifa=consumidor.cip_cosip_rs,
                custo=consumidor.cip_cosip_rs,
            )
        )

    # Outros valores (R$ fixo).
    if consumidor.outros_rs > 0:
        linhas.append(
            LinhaFatura(
                descricao="Outros valores",
                categoria="OUTROS",
                quantidade=1.0,
                tarifa=consumidor.outros_rs,
                custo=consumidor.outros_rs,
            )
        )

    # Reativos excedentes (fp < 0,92): registra a linha informativa quando há
    # reativos informados, usando tarifa de energia TUSD por posto.
    fp = _fator_potencia(consumidor)
    if fp is not None and fp < _FATOR_POTENCIA_REF:
        reat_ener = (
            consumidor.reativo_energia_ponta_kvArh
            + consumidor.reativo_energia_fora_ponta_kvArh
        )
        tarifa_tusd_e = (
            tarifa_reativos
            if tarifa_reativos is not None
            else next(
                (
                    p.valor
                    for p in parcelas
                    if p.componente == COMPONENTE_TUSD
                    and p.grandeza == GRANDEZA_ENERGIA
                ),
                0.0,
            )
        )
        if reat_ener > 0 and tarifa_tusd_e > 0:
            linhas.append(
                LinhaFatura(
                    descricao="Reativos excedentes (fp < 0,92)",
                    categoria="REATIVOS",
                    quantidade=reat_ener,
                    tarifa=tarifa_tusd_e,
                    custo=reat_ener * tarifa_tusd_e,
                )
            )

    # Tributos opcionais (base líquida por padrão). Duas formas de ICMS:
    # "dentro" = aditiva; "fora" = multiplicativa (como no XLSM Fatura-1).
    if aplicar_tributos:
        if tipo_icms == "fora":
            denominador_aux = (1.0 - pis - cofins) * (1.0 - icms)
            if denominador_aux <= 0:
                raise ValueError(
                    "tributos inválidos: (1 − PIS − COFINS) × (1 − ICMS) "
                    "deve ser maior que 0"
                )
            fator = 1.0 / denominador_aux
        else:
            denominador = 1.0 - pis - cofins - icms
            if denominador <= 0:
                raise ValueError(
                    "tributos inválidos: PIS + COFINS + ICMS deve ser menor "
                    "que 1"
                )
            fator = 1.0 / denominador
        linhas = [
            LinhaFatura(
                descricao=l.descricao + " (com tributos)",
                categoria=l.categoria,
                quantidade=l.quantidade,
                tarifa=l.tarifa * fator if l.categoria == "TARIFA" else l.tarifa,
                custo=l.custo * fator if l.categoria == "TARIFA" else l.custo,
            )
            for l in linhas
        ]

    return ResultadoFatura(
        modalidade=modalidade.strip(),
        linhas=tuple(linhas),
        aplicar_tributos=aplicar_tributos,
    )


def _fator_potencia(consumidor):
    """Fator de potência aproximado a partir do consumo (kWh) e reativos
    (kVArh), ou None quando não há dados para calcular."""
    ativa = consumidor.consumo_total_kwh
    reativa = (
        consumidor.reativo_energia_ponta_kvArh
        + consumidor.reativo_energia_fora_ponta_kvArh
    )
    if ativa <= 0:
        return None
    fp = ativa / ((ativa**2 + reativa**2) ** 0.5)
    return fp
