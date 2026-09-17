"""Serviço de EPI simplificado (assinaturas — Sprint "estrutura").

Caso de uso: dado um perfil de consumo e um preço de referência do ACL
(informado pelo usuário, sem integração externa), calcular o ponto de
indiferença simplificado.

A fórmula do EPI depende da regra regulatória (docs/premissas.md, P2) e não é
implementada aqui. O Service apenas define o contrato de orquestração:
    perfil + preço ACL -> tarifas do perfil (repo) -> core.epi.calcular_epi
"""

from __future__ import annotations

from core.models import Consumidor, ResultadoEPI


class EPIService:
    """Caso de uso: calcular o Preço de Indiferença (EPI) simplificado."""

    def __init__(self, tarifa_repository):
        self._repo = tarifa_repository

    def calcular(self, perfil: Consumidor, preco_referencia_acl: float) -> ResultadoEPI:
        """Calcula o EPI para o ``perfil`` dado o preço de referência do ACL.

        Fluxo (a implementar): buscar tarifas vigentes do perfil/contexto no
        repositório e chamar ``core.epi.calcular_epi`` com as variáveis que a
        fórmula validada exigir (docs/premissas.md, P2). Nenhuma fórmula foi
        inventada.

        Raises:
            NotImplementedError: fórmula do EPI pendente (P2).
        """
        raise NotImplementedError(
            "Cálculo do EPI ainda não implementado: depende da fórmula (P2) "
            "e das tarifas do perfil (busca via repositório)."
        )
