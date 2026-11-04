"""Preço de Indiferença (PI) — decisão ACR × ACL.

Implementação em Python puro (sem banco, API, arquivos ou rede) do cálculo do
PI: o preço da energia no ACL (R$/MWh) que iguala o custo de energia entre
ACR e ACL.

Fórmula adaptada de Lemos (2025) — ver docs/epi.md. Este módulo recebe os
totais de energia e as TE (sem tributos) da modalidade de menor custo no ACR;
**não altera** as regras de faturamento do ``motor_calculo`` (a seleção da
modalidade de menor custo continua sendo responsabilidade de quem chama).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from .models import ResultadoPI


def _validar_aliquota(valor: float, nome: str) -> None:
    """Exige alíquota em [0, 1)."""
    if not 0.0 <= valor < 1.0:
        raise ValueError(f"{nome} deve estar em [0, 1) (recebido {valor!r})")


def _validar_nao_negativo(valor: float, nome: str) -> None:
    if valor < 0:
        raise ValueError(f"{nome} não pode ser negativo (recebido {valor!r})")


def _componentes_mes(
    e_ponta: float,
    e_fora_ponta: float,
    te_ponta: float,
    te_fora_ponta: float,
    pis: float,
    cofins: float,
    icms: float,
    bandeira: float,
    encargos: float,
    k: float,
    opex_mensal: float,
    capex: float,
    horizonte_meses: int,
) -> tuple[float, float, float, float, float]:
    """Valida e devolve ``(e, c_te, c_e_acr, custos_acl, base_acl)`` do mês."""
    _validar_nao_negativo(e_ponta, "e_ponta")
    _validar_nao_negativo(e_fora_ponta, "e_fora_ponta")
    e = e_ponta + e_fora_ponta
    if e <= 0:
        raise ValueError("consumo total (e_ponta + e_fora_ponta) deve ser > 0")

    _validar_nao_negativo(te_ponta, "te_ponta")
    _validar_nao_negativo(te_fora_ponta, "te_fora_ponta")
    _validar_nao_negativo(bandeira, "bandeira")
    _validar_nao_negativo(encargos, "encargos")
    _validar_nao_negativo(k, "k")
    _validar_nao_negativo(opex_mensal, "opex_mensal")
    _validar_nao_negativo(capex, "capex")

    _validar_aliquota(pis, "pis")
    _validar_aliquota(cofins, "cofins")
    _validar_aliquota(icms, "icms")

    denominador_tributos = (1.0 - pis - cofins) * (1.0 - icms)
    if denominador_tributos <= 0:
        raise ValueError(
            "tributos inválidos: (1 − PIS − COFINS) × (1 − ICMS) deve ser > 0"
        )

    if not isinstance(horizonte_meses, int) or isinstance(horizonte_meses, bool):
        raise ValueError("horizonte_meses deve ser inteiro > 0")
    if horizonte_meses <= 0:
        raise ValueError("horizonte_meses deve ser inteiro > 0")

    c_te = e_ponta * te_ponta + e_fora_ponta * te_fora_ponta
    c_e_acr = (c_te + e * bandeira) / denominador_tributos
    custos_acl = (
        opex_mensal + capex / horizonte_meses + e * (1.0 + k) * encargos
    )
    base_acl = e * (1.0 + k) / (1.0 - icms)
    return e, c_te, c_e_acr, custos_acl, base_acl


def _resultado(
    e: float,
    c_te: float,
    c_e_acr: float,
    custos_acl: float,
    base_acl: float,
    meses: int,
) -> ResultadoPI:
    pi = (c_e_acr - custos_acl) / base_acl
    aviso = (
        "PI ≤ 0: o custo ACR de energia não cobre os custos do ACL no "
        "horizonte informado (ACL vantajoso mesmo com preço de energia zero "
        "ou negativo)."
        if pi <= 0
        else None
    )
    return ResultadoPI(
        pi=pi,
        e=e,
        c_te=c_te,
        c_e_acr=c_e_acr,
        custos_acl=custos_acl,
        base_acl=base_acl,
        aviso=aviso,
        meses=meses,
    )


def calcular_pi(
    e_ponta: float,
    e_fora_ponta: float,
    te_ponta: float,
    te_fora_ponta: float,
    pis: float,
    cofins: float,
    icms: float,
    bandeira: float = 0.0,
    encargos: float = 0.0,
    k: float = 0.03,
    opex_mensal: float = 0.0,
    capex: float = 0.0,
    horizonte_meses: int = 60,
) -> ResultadoPI:
    """Calcula o Preço de Indiferença (PI) em R$/MWh.

    Fórmula (adaptada de Lemos, 2025)::

        E          = e_ponta + e_fora_ponta
        C_TE       = e_ponta·te_ponta + e_fora_ponta·te_fora_ponta
        C_E_ACR    = (C_TE + E·bandeira) / ((1 − pis − cofins)·(1 − icms))
        CUSTOS_ACL = opex_mensal + capex / horizonte_meses + E·(1+k)·encargos
        BASE_ACL   = E·(1 + k) / (1 − icms)
        PI         = (C_E_ACR − CUSTOS_ACL) / BASE_ACL

    Args:
        e_ponta: energia no posto ponta (MWh).
        e_fora_ponta: energia no posto fora de ponta (MWh).
        te_ponta: TE ponta sem tributos (R$/MWh) da modalidade de menor
            custo no ACR.
        te_fora_ponta: TE fora de ponta sem tributos (R$/MWh) da modalidade
            de menor custo no ACR.
        pis: alíquota de PIS (fração, 0 ≤ pis < 1).
        cofins: alíquota de COFINS (fração, 0 ≤ cofins < 1).
        icms: alíquota de ICMS (fração, 0 ≤ icms < 1).
        bandeira: bandeira tarifária (R$/MWh). Padrão 0.
        encargos: encargos do ACL por energia (R$/MWh, ex.: ESS). São custo
            do lado ACL — NÃO se somam à TE — e entram como
            ``E·(1+k)·encargos`` no numerador. Padrão 0.
        k: perdas na migração ao ACL (fração). Padrão 0,03.
        opex_mensal: OPEX do ACL (R$/mês). Padrão 0.
        capex: CAPEX do ACL (R$). Padrão 0.
        horizonte_meses: horizonte de amortização do CAPEX (meses).
            Padrão 60.

    Returns:
        ``ResultadoPI`` com o ``pi`` (R$/MWh) e os componentes do cálculo.
        ``aviso`` é preenchido quando ``pi ≤ 0``.

    Raises:
        ValueError: entrada inválida (alíquotas fora de [0, 1), consumo ≤ 0,
            custos negativos, horizonte ≤ 0 etc.).
    """
    e, c_te, c_e_acr, custos_acl, base_acl = _componentes_mes(
        e_ponta=e_ponta,
        e_fora_ponta=e_fora_ponta,
        te_ponta=te_ponta,
        te_fora_ponta=te_fora_ponta,
        pis=pis,
        cofins=cofins,
        icms=icms,
        bandeira=bandeira,
        encargos=encargos,
        k=k,
        opex_mensal=opex_mensal,
        capex=capex,
        horizonte_meses=horizonte_meses,
    )
    return _resultado(e, c_te, c_e_acr, custos_acl, base_acl, meses=1)


def calcular_pi_meses(
    meses: Iterable[Mapping[str, float]],
    pis: float,
    cofins: float,
    icms: float,
    encargos: float = 0.0,
    k: float = 0.03,
    opex_mensal: float = 0.0,
    capex: float = 0.0,
    horizonte_meses: int = 60,
) -> ResultadoPI:
    """Calcula o PI agregado de vários meses.

    Soma ``c_e_acr``, ``custos_acl`` e ``base_acl`` de **todos** os meses
    antes de dividir — **não** calcula nem faz média dos PIs mensais.

    Args:
        meses: sequência de meses; cada item é um mapping com as chaves
            ``e_ponta``, ``e_fora_ponta``, ``te_ponta``, ``te_fora_ponta`` e,
            opcionalmente, ``bandeira``.
        pis: alíquota de PIS (fração).
        cofins: alíquota de COFINS (fração).
        icms: alíquota de ICMS (fração).
        encargos: encargos do ACL por energia (R$/MWh, ex.: ESS). Padrão 0.
        k: perdas na migração ao ACL (fração). Padrão 0,03.
        opex_mensal: OPEX do ACL (R$/mês). Padrão 0.
        capex: CAPEX do ACL (R$). Padrão 0.
        horizonte_meses: horizonte de amortização do CAPEX (meses).
            Padrão 60.

    Returns:
        ``ResultadoPI`` com os componentes agregados e ``meses`` = quantidade
        de meses considerados.

    Raises:
        ValueError: ``meses`` vazio ou qualquer mês com entrada inválida.
    """
    lista = list(meses)
    if not lista:
        raise ValueError("meses não pode ser vazio")

    total_e = 0.0
    total_c_te = 0.0
    total_c_e_acr = 0.0
    total_custos_acl = 0.0
    total_base_acl = 0.0
    for mes in lista:
        try:
            e, c_te, c_e_acr, custos_acl, base_acl = _componentes_mes(
                e_ponta=mes["e_ponta"],
                e_fora_ponta=mes["e_fora_ponta"],
                te_ponta=mes["te_ponta"],
                te_fora_ponta=mes["te_fora_ponta"],
                pis=pis,
                cofins=cofins,
                icms=icms,
                bandeira=float(mes.get("bandeira", 0.0)),
                encargos=encargos,
                k=k,
                opex_mensal=opex_mensal,
                capex=capex,
                horizonte_meses=horizonte_meses,
            )
        except KeyError as exc:
            raise ValueError(
                f"mês sem a chave obrigatória {exc.args[0]!r}; use e_ponta, "
                "e_fora_ponta, te_ponta e te_fora_ponta"
            ) from exc
        total_e += e
        total_c_te += c_te
        total_c_e_acr += c_e_acr
        total_custos_acl += custos_acl
        total_base_acl += base_acl

    return _resultado(
        total_e,
        total_c_te,
        total_c_e_acr,
        total_custos_acl,
        total_base_acl,
        meses=len(lista),
    )
