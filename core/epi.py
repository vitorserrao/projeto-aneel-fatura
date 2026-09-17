"""Preço de Indiferença (EPI) simplificado.

PENDENTE — o cálculo simplificado do EPI a partir de um preço de referência do
ACL fornecido como entrada **não foi implementado**. A fórmula fechada
(componentes incluídos, tratamento de TE/TUSD, energia vs demanda) ainda não
foi validada (docs/premissas.md, P2).

Nenhuma fórmula é criada por suposição. Este módulo define apenas o contrato
de entrada/saída e falha explicitamente até que a fórmula seja validada.
"""

from __future__ import annotations

from .models import ResultadoEPI


class FormulaEPINaoDefinida(NotImplementedError):
    """Fórmula do EPI ainda pendente de validação (docs/premissas.md, P2)."""


def calcular_epi(
    preco_referencia_acl: float,
    **variaveis_formalmente_definidas,
) -> ResultadoEPI:
    """Calcula o Preço de Indiferença simplificado (PENDENTE).

    Args:
        preco_referencia_acl: preço de referência do ACL (entrada do usuário).
        **variaveis_formalmente_definidas: variáveis que a fórmula validada
            exigirá no futuro (a definir em P2).

    Raises:
        FormulaEPINaoDefinida: sempre, até que a fórmula seja validada.
    """
    raise FormulaEPINaoDefinida(
        "A fórmula do EPI simplificado ainda não foi validada; nenhuma regra "
        "foi inventada (docs/premissas.md, P2)."
    )
