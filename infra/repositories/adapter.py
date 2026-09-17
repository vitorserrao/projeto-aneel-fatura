"""Adapter Repository → Core (Sprint P2).

Converte o resultado de leitura (``TarifaVigente`` do repositório) no contrato
do core (``TarifaAcr`` / ``ParcelaTarifaria``) para que as rotas de consulta e,
futuramente, o motor de cálculo consumam um tipo estável.

Princípio (não inventar regra): o mapeamento de ``componente``→TE/TUSD é direto
(coluna já normalizada na ingestão) e a cópia para ``TarifaAcr`` é perda-zero
(preserva todos os campos do dataset). Já o mapeamento de
``dsc_detalhe``/``dsc_unidade_terciaria``/``nom_posto_tarifario`` →
grandeza (ENERGIA/DEMANDA) e posto normalizado (PONTA/FORA PONTA) é uma decisão
de domínio pendente (docs/premissas.md, P5). Por isso a construção de uma
``ParcelaTarifaria`` exige que quem chama informe a ``grandeza`` e o ``posto``
de forma explícita — o adapter não os adivinha.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from core.tarifas import ParcelaTarifaria, TarifaAcr
from .tarifa_repository import TarifaVigente


def tarifa_vigente_para_tarifa_acr(v: TarifaVigente) -> TarifaAcr:
    """Copia perda-zero de uma tarifa vigente para o contrato ``TarifaAcr``.

    Nenhum campo é derivado/inventado aqui; apenas espelha o que já existe na
    linha do banco (incluindo a resolução ``dsc_reh``, exposta como
    ``resolucao`` no ``TarifaVigente``).
    """
    return TarifaAcr(
        distribuidora=v.sig_agente,
        resolucao=v.resolucao,
        inicio_vigencia=v.inicio_vigencia,
        fim_vigencia=v.fim_vigencia,
        base_tarifaria=v.base_tarifaria,
        subgrupo=v.subgrupo,
        modalidade=v.modalidade,
        classe=v.classe,
        subclasse=v.subclasse,
        detalhe=v.detalhe,
        tipo_acesso="",  # dataset real não tem este campo nesta versão (P5)
        posto=v.posto,
        unidade=v.unidade,
        # Como um registro é de UM componente (TE ou TUSD), apenas o lado
        # correspondente recebe o valor; o outro fica 0.
        te=float(v.valor) if v.componente == "TE" else 0.0,
        tusd=float(v.valor) if v.componente == "TUSD" else 0.0,
    )


def tarifa_vigente_para_parcela(
    v: TarifaVigente,
    *,
    grandeza: str,
    posto: str,
) -> ParcelaTarifaria:
    """Constrói uma ``ParcelaTarifaria`` exigindo ``grandeza`` e ``posto``.

    ``grandeza`` ∈ {ENERGIA, DEMANDA} e ``posto`` ∈ {PONTA, FORA PONTA} devem
    vir da camada que conhece a regra de domínio (P5), NÃO são inferidos aqui.
    ``valor`` é convertido de ``Decimal`` para ``float`` (o motor trabalha em
    float; a precisão é preservada na origem/ingestão).
    """
    _checar_decimal_ok(v.valor)
    # Validamos componente em ParcelaTarifaria.__post_init__; aqui apenas
    # mapeia a unidade bruta do dataset para a unidade do contrato do core.
    unidade = _unidade_para_contrato(v.unidade)
    return ParcelaTarifaria(
        componente=v.componente,
        grandeza=grandeza,
        posto=posto,
        unidade=unidade,
        valor=float(v.valor),
    )


def _unidade_para_contrato(unidade_bruta: str) -> str:
    """Traduz a unidade observada no dataset para o vocabulário do core.

    Correção técnica simples (não regulatória) do formato da unidade:
    o core espera 'R$/MWh'/'R$/kWh'/'R$/kW'. Como é só um rótulo de unidade
    (não muda valor), a conversão é direta:
        dataset 'MWh' -> 'R$/MWh' ; dataset 'kW' -> 'R$/kW'
    Não cobre outros rótulos não observados no CSV atual.
    """
    u = unidade_bruta.strip()
    mapa = {"MWh": "R$/MWh", "kWh": "R$/kWh", "kW": "R$/kW"}
    if u in mapa:
        return mapa[u]
    # Não assumir para rótulos desconhecidos: exige explicitação.
    raise ValueError(
        f"unidade '{unidade_bruta}' não mapeada para o contrato; "
        "preencha manualmente (P5)."
    )


def _checar_decimal_ok(valor: Decimal) -> None:
    if valor is None or not isinstance(valor, Decimal):
        raise TypeError("valor deve ser Decimal (preservar precisão de origem)")
