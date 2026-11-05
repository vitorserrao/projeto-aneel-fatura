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
    POSTO_INTERMEDIARIO,
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
    if posto == POSTO_PONTA:
        return consumidor.consumo_ponta_kwh
    if posto == POSTO_INTERMEDIARIO:
        return consumidor.consumo_intermediario_kwh
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
MODALIDADES_GRUPO_A = ("AZUL", "VERDE", "OPTANTE B")
MODALIDADES_GRUPO_B = ("CONVENCIONAL MONÔMIA", "BRANCA")

_LIMITE_OPTANTE_B_KVA = 112.5
_LIMITE_OPTANTE_B_COOPERATIVA_KVA = 1125.0


def _subgrupo_b_por_atividade(atividade: str) -> str:
    """Mapeia a atividade econômica para o subgrupo B (B1/B2/B3)."""
    a = (atividade or "").strip().lower()
    if "residencial" in a:
        return "B1"
    if "rural" in a or "agropecu" in a:
        return "B2"
    return "B3"


def _classe_b_por_atividade(atividade: str) -> str | None:
    """Classe do Grupo B derivada da atividade, ou None (ambígua).

    Usada no Optante B (art. 292) para o usuário NÃO precisar informar a
    classe: residencial → Residencial; rural/agropecuária → Rural. Demais
    atividades (comercial/industrial/esportiva — B3) ficam sem classe
    derivada: o perfil informa a classe ou a guarda de ambiguidade (A5)
    recusa em vez de somar tarifas distintas.
    """
    a = (atividade or "").strip().lower()
    if "residencial" in a:
        return "Residencial"
    if "rural" in a or "agropecu" in a:
        return "Rural"
    return None


def _subclasse_b_por_atividade(atividade: str) -> str | None:
    """Subclasse do Grupo B derivada da atividade, ou None.

    O dataset ANEEL publica B1 em subclasses "Residencial" e "Baixa Renda"
    (valores distintos) e B2 em várias subclasses rurais — derivar só a
    classe ainda deixaria chaves ambíguas. Derivamos a subclasse neutra:
    residencial → "Residencial"; rural/agropecuária → "Não se aplica".
    """
    a = (atividade or "").strip().lower()
    if "residencial" in a:
        return "Residencial"
    if "rural" in a or "agropecu" in a:
        return "Não se aplica"
    return None


# Palavras-chave do critério de iluminação esportiva do art. 292: o benefício
# dos refletores ≥ 2/3 da carga vale para ATIVIDADES ESPORTIVAS ou PARQUES
# AGROPECUÁRIOS (fonte: REN 1.000/2021, art. 292 — ren1000_2021_formulas_dou.md).
_PALAVRAS_CHAVE_ATIVIDADE_ESPORTIVA = ("esportiv", "parque", "agropecu")


def _atividade_esportiva_parque(atividade: str | None) -> bool:
    """Atividade com iluminação esportiva/parque agropecuário (art. 292)."""
    a = (atividade or "").strip().casefold()
    return any(kw in a for kw in _PALAVRAS_CHAVE_ATIVIDADE_ESPORTIVA)


def elegivel_optante_b(consumidor) -> bool:
    """Art. 292: Grupo A pode ser faturado como Grupo B? (4 critérios).

    O critério de refletores exige atividade esportiva/parque agropecuário;
    sem essa atividade, vale apenas o limite de transformadores (ou
    hotelaria/turismo).
    """
    if consumidor.hotelaria_turismo:
        return True
    if (
        _atividade_esportiva_parque(consumidor.atividade)
        and consumidor.carga_refletores_kw > 0
        and consumidor.carga_instalada_total_kw > 0
        and consumidor.carga_refletores_kw
        >= (2.0 / 3.0) * consumidor.carga_instalada_total_kw
    ):
        return True
    limite = (
        _LIMITE_OPTANTE_B_COOPERATIVA_KVA
        if consumidor.cooperativa_eletrificacao_rural
        else _LIMITE_OPTANTE_B_KVA
    )
    return 0 < consumidor.potencia_transformadores_kva <= limite


def modalidades_elegiveis(consumidor) -> list[str]:
    """Modalidades do Grupo A elegíveis para o perfil.

    Regras (REN 1.000/2021):
    - Azul: todos os subgrupos A.
    - Verde: apenas A3a/A4/AS.
    """
    elegiveis = ["AZUL"]
    if consumidor.subgrupo.strip().upper() in _SUBGRUPOS_VERDE:
        elegiveis.append("VERDE")
    if elegivel_optante_b(consumidor):
        elegiveis.append("OPTANTE B")
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
    if m == "OPTANTE B":
        if elegivel_optante_b(consumidor):
            return None
        return (
            "Optante B (art. 292): exige transformadores ≤ 112,5 kVA "
            "(ou ≤ 1.125 kVA se cooperativa de eletrificação rural), "
            "hotelaria/turismo ou iluminação esportiva ≥ 2/3 da carga "
            "(atividades esportivas/parques agropecuários)."
        )
    return f"Modalidade {modalidade!r} fora do escopo do Grupo A (Azul/Verde/Optante B)"


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
    vrere_r_mwh=None,
    vrdre_r_kw=None,
    reativos_direto=False,
    tarifa_reativo_energia_r_kvarh=None,
    tarifa_reativo_demanda_r_kvar=None,
    demanda_unica=False,
    tipo_icms="fora",
    arredondar_centavos=False,
    demanda_isenta_icms=False,
    demanda_isenta_icms_kw: float | None = None,
    tributar_reativos=False,
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
    ``tipo_icms`` às linhas **tarifárias e de ultrapassagem**:
    - ``"dentro"`` (aditiva): ``tarifa / (1 − pis − cofins − icms)``
    - ``"fora"`` (multiplicativa, **padrão** — validada em faturas reais Copel/CEMIG/Equatorial): 
      ``tarifa / ((1 − pis − cofins) × (1 − icms))``

    ``arredondar_centavos=True`` arredonda o ``custo`` de cada linha a centavos.
    ``demanda_isenta_icms=True`` divide a demanda faturável em parcela medida
    (com ICMS) e parcela ``faturada − medida`` **isenta de ICMS** (só
    PIS/COFINS), conforme faturas reais Copel/CEMIG/Equatorial.
    ``tributar_reativos=True`` aplica PIS/COFINS/ICMS também às linhas de
    reativos (CEMIG/Equatorial tributam; Copel/artigo não).
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

    # Reativos excedentes. Modo direto (faturas antigas): excedente pronto em
    # kVArh/kVAr cobrado com tarifas diretas. Modo art. 304: aproximação A6
    # com VRERE/VRDRE de referência.
    if reativos_direto:
        linhas.extend(
            _linhas_reativos_diretos(
                consumidor,
                tarifa_energia_r_kvarh=tarifa_reativo_energia_r_kvarh,
                tarifa_demanda_r_kvar=tarifa_reativo_demanda_r_kvar,
            )
        )
    else:
        linhas.extend(
            _linhas_reativos_excedentes(
                consumidor,
                vrere_r_mwh=vrere_r_mwh,
                vrdre_r_kw=vrdre_r_kw,
                demanda_unica=demanda_unica,
            )
        )

    if demanda_isenta_icms:
        linhas = _dividir_demanda_isenta(
            consumidor, linhas, demanda_unica, demanda_isenta_icms_kw
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
        denominador_isento = 1.0 - pis - cofins
        if denominador_isento <= 0:
            raise ValueError(
                "tributos inválidos: PIS + COFINS deve ser menor que 1"
            )
        fator_isento = 1.0 / denominador_isento

        def _fator_linha(l):
            if "ISENTA ICMS" in l.descricao:
                return fator_isento
            # Bandeira também é tributada (faturas reais: Equatorial cobra
            # PIS/COFINS/ICMS no "Adicional Bandeira"; ENEL embute o ICMS).
            if l.categoria in ("TARIFA", "ULTRAPASSAGEM", "BANDEIRA"):
                return fator
            if tributar_reativos and l.categoria == "REATIVOS":
                return fator
            return 1.0

        linhas = [
            LinhaFatura(
                descricao=l.descricao + " (com tributos)",
                categoria=l.categoria,
                quantidade=l.quantidade,
                tarifa=l.tarifa * _fator_linha(l),
                custo=l.custo * _fator_linha(l),
            )
            for l in linhas
        ]

    if arredondar_centavos:
        linhas = [
            LinhaFatura(
                descricao=l.descricao,
                categoria=l.categoria,
                quantidade=l.quantidade,
                tarifa=l.tarifa,
                custo=round(l.custo, 2),
            )
            for l in linhas
        ]

    return ResultadoFatura(
        modalidade=modalidade.strip(),
        linhas=tuple(linhas),
        aplicar_tributos=aplicar_tributos,
    )


def _dividir_demanda_isenta(consumidor, linhas, demanda_unica, isenta_kw=None):
    """Divide a demanda faturável em parcela normal e parcela isenta de ICMS.

    Se ``isenta_kw`` for informado (> 0), usa esse valor como parcela isenta;
    caso contrário calcula ``faturada − medida`` (regra das faturas reais).
    """
    novas = []
    for l in linhas:
        if l.categoria == "TARIFA" and "TUSD DEMANDA" in l.descricao:
            if demanda_unica:
                medida = consumidor.demanda_medida_unica_kw
            else:
                medida = (
                    consumidor.demanda_ponta_kw
                    if POSTO_PONTA in l.descricao
                    else consumidor.demanda_fora_ponta_kw
                )
            faturada = l.quantidade
            parcela_isenta = (
                isenta_kw if isenta_kw is not None else (faturada - medida)
            )
            if 0 < parcela_isenta < faturada:
                parcela_normal = faturada - parcela_isenta
                novas.append(
                    LinhaFatura(
                        descricao=l.descricao,
                        categoria=l.categoria,
                        quantidade=parcela_normal,
                        tarifa=l.tarifa,
                        custo=parcela_normal * l.tarifa,
                    )
                )
                novas.append(
                    LinhaFatura(
                        descricao=l.descricao + " ISENTA ICMS",
                        categoria=l.categoria,
                        quantidade=parcela_isenta,
                        tarifa=l.tarifa,
                        custo=parcela_isenta * l.tarifa,
                    )
                )
                continue
        novas.append(l)
    return novas


def _fp(ativa: float, reativa: float) -> float | None:
    """Fator de potência aproximado (premissa A6) ou None sem dados."""
    if ativa <= 0:
        return None
    return ativa / ((ativa**2 + reativa**2) ** 0.5)


def _excedente_energia_mwh(ativa_kwh: float, fp: float | None) -> float | None:
    """Quantidade de energia reativa excedente (em MWh, unidade do VRERE)."""
    if fp is None or fp >= _FATOR_POTENCIA_REF:
        return None
    return ativa_kwh * (_FATOR_POTENCIA_REF / fp - 1.0) * _FATOR_KWH_PARA_MWH


def _excedente_demanda_kw(medida_kw: float, daf_kw: float, fp: float | None) -> float | None:
    """Quantidade de demanda reativa excedente (kW) ou None."""
    if fp is None or fp >= _FATOR_POTENCIA_REF or medida_kw <= 0:
        return None
    excedente = medida_kw * (_FATOR_POTENCIA_REF / fp) - daf_kw
    if excedente <= 0:
        return None
    return excedente


_HORAS_CAPACITIVA = 6.0
_HORAS_FORA_PONTA_TOTAL = 21.0
_HORAS_INDUTIVA_FORA_PONTA = _HORAS_FORA_PONTA_TOTAL - _HORAS_CAPACITIVA

def _linhas_reativos_excedentes(consumidor, *, vrere_r_mwh, vrdre_r_kw, demanda_unica):
    """Linhas de reativos excedentes do art. 304 (categoria ``REATIVOS``)."""
    linhas: list[LinhaFatura] = []

    if vrere_r_mwh is not None and vrere_r_mwh > 0:
        fp_ponta = _fp(
            consumidor.consumo_ponta_kwh,
            consumidor.reativo_energia_ponta_kvArh,
        )
        if consumidor.reativo_energia_ponta_kvArh > 0:
            qtd = _excedente_energia_mwh(consumidor.consumo_ponta_kwh, fp_ponta)
            if qtd is not None:
                linhas.append(
                    LinhaFatura(
                        descricao="Energia Reativa Excedente Indutiva (Ponta)",
                        categoria="REATIVOS",
                        quantidade=qtd,
                        tarifa=vrere_r_mwh,
                        custo=qtd * vrere_r_mwh,
                    )
                )

        ativa_ind_fp = (
            consumidor.consumo_fora_ponta_kwh
            * (_HORAS_INDUTIVA_FORA_PONTA / _HORAS_FORA_PONTA_TOTAL)
        )
        if consumidor.reativo_energia_fora_ponta_kvArh > 0:
            fp_ind_fp = _fp(ativa_ind_fp, consumidor.reativo_energia_fora_ponta_kvArh)
            qtd = _excedente_energia_mwh(ativa_ind_fp, fp_ind_fp)
            if qtd is not None:
                linhas.append(
                    LinhaFatura(
                        descricao="Energia Reativa Excedente Indutiva (Fora Ponta)",
                        categoria="REATIVOS",
                        quantidade=qtd,
                        tarifa=vrere_r_mwh,
                        custo=qtd * vrere_r_mwh,
                    )
                )

        ativa_cap_fp = (
            consumidor.consumo_fora_ponta_kwh
            * (_HORAS_CAPACITIVA / _HORAS_FORA_PONTA_TOTAL)
        )
        if consumidor.reativo_energia_capacitiva_kvArh > 0:
            fp_cap = _fp(ativa_cap_fp, consumidor.reativo_energia_capacitiva_kvArh)
            qtd = _excedente_energia_mwh(ativa_cap_fp, fp_cap)
            if qtd is not None:
                linhas.append(
                    LinhaFatura(
                        descricao="Energia Reativa Excedente Capacitiva (Fora Ponta)",
                        categoria="REATIVOS",
                        quantidade=qtd,
                        tarifa=vrere_r_mwh,
                        custo=qtd * vrere_r_mwh,
                    )
                )

    if vrdre_r_kw is not None and vrdre_r_kw > 0:
        if demanda_unica:
            ativa_total = consumidor.consumo_total_kwh
            reativa_total = (
                consumidor.reativo_energia_ponta_kvArh
                + consumidor.reativo_energia_fora_ponta_kvArh
                + consumidor.reativo_energia_capacitiva_kvArh
            )
            fp_total = _fp(ativa_total, reativa_total)
            qtd = _excedente_demanda_kw(
                consumidor.demanda_medida_unica_kw,
                consumidor.demanda_faturavel_unica_kw,
                fp_total,
            )
            if qtd is not None:
                linhas.append(
                    LinhaFatura(
                        descricao="Demanda Reativa Excedente",
                        categoria="REATIVOS",
                        quantidade=qtd,
                        tarifa=vrdre_r_kw,
                        custo=qtd * vrdre_r_kw,
                    )
                )
        else:
            for posto, medida_kw, daf_kw, reativa_kvArh, ativa_kwh in (
                (
                    POSTO_PONTA,
                    consumidor.demanda_ponta_kw,
                    consumidor.demanda_faturavel_kw(POSTO_PONTA),
                    consumidor.reativo_energia_ponta_kvArh,
                    consumidor.consumo_ponta_kwh,
                ),
                (
                    POSTO_FORA_PONTA,
                    consumidor.demanda_fora_ponta_kw,
                    consumidor.demanda_faturavel_kw(POSTO_FORA_PONTA),
                    consumidor.reativo_energia_fora_ponta_kvArh
                    + consumidor.reativo_energia_capacitiva_kvArh,
                    consumidor.consumo_fora_ponta_kwh,
                ),
            ):
                fp_posto = _fp(ativa_kwh, reativa_kvArh)
                qtd = _excedente_demanda_kw(medida_kw, daf_kw, fp_posto)
                if qtd is not None:
                    linhas.append(
                        LinhaFatura(
                            descricao=f"Demanda Reativa Excedente ({posto.title()})",
                            categoria="REATIVOS",
                            quantidade=qtd,
                            tarifa=vrdre_r_kw,
                            custo=qtd * vrdre_r_kw,
                        )
                    )

    return linhas


def _linhas_reativos_diretos(consumidor, *, tarifa_energia_r_kvarh, tarifa_demanda_r_kvar):
    """Linhas de reativos no modo "excedente direto" (faturas antigas)."""
    linhas: list[LinhaFatura] = []
    if tarifa_energia_r_kvarh is not None and tarifa_energia_r_kvarh > 0:
        for posto, qtd in (
            (POSTO_PONTA, consumidor.reativo_energia_ponta_kvArh),
            (POSTO_FORA_PONTA, consumidor.reativo_energia_fora_ponta_kvArh),
        ):
            if qtd > 0:
                linhas.append(
                    LinhaFatura(
                        descricao=f"Consumo Excessivo de Energia Reativa ({posto.title()})",
                        categoria="REATIVOS",
                        quantidade=qtd,
                        tarifa=tarifa_energia_r_kvarh,
                        custo=qtd * tarifa_energia_r_kvarh,
                    )
                )
    if tarifa_demanda_r_kvar is not None and tarifa_demanda_r_kvar > 0:
        for posto, qtd in (
            (POSTO_PONTA, consumidor.reativo_demanda_ponta_kvAr),
            (POSTO_FORA_PONTA, consumidor.reativo_demanda_fora_ponta_kvAr),
        ):
            if qtd > 0:
                linhas.append(
                    LinhaFatura(
                        descricao=f"Demanda Excessiva de Potência Reativa ({posto.title()})",
                        categoria="REATIVOS",
                        quantidade=qtd,
                        tarifa=tarifa_demanda_r_kvar,
                        custo=qtd * tarifa_demanda_r_kvar,
                    )
                )
    return linhas

