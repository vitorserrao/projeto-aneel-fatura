"""Serviço de projeção experimental (assinaturas — Sprint "estrutura").

Caso de uso: projetar a evolução futura do custo no ACR a partir do histórico
tarifário. Trata-se de um módulo EXPERIMENTAL (fora do núcleo obrigatório do
MVP): o sistema funciona sem ele. O pipeline está em ``forecast/`` (baseline
estatístico simples antes de modelos mais complexos, conforme docs.
"""

from __future__ import annotations

from datetime import date


class ProjecaoService:
    """Caso de uso: projetar custo/índice do ACR para um contexto/componente.

    Experimental e não obrigatório no MVP. Assinatura definida de forma ampla
    para não travar o desenho; a implementação usa o módulo ``forecast``.
    """

    def __init__(self, tarifa_repository):
        # Reutiliza o repositório (histórico tarifário de distribuidora/
        # componente) como fonte da série para modelar.
        self._repo = tarifa_repository

    def projetar(
        self,
        *,
        sig_agente: str,
        componente: str,
        data_inicial: date,
        horizonte_meses: int = 24,
        **params,
    ) -> dict:
        """Projeta a evolução do ``componente`` para ``sig_agente``.

        Args:
            sig_agente: distribuidora (via repositório).
            componente: TE ou TUSD (filtro da série).
            data_inicial: ponto de partida do histórico usado como base.
            horizonte_meses: quantos meses à frente projetar.
            **params: parâmetros do modelo de baseline (a definir em forecast).

        Returns:
            dict com horizonte e valores projetados (a definir). Experimental.

        Raises:
            NotImplementedError: módulo forecast ainda não implementado.
        """
        raise NotImplementedError(
            "Projeção ainda não implementada (módulo forecast, experimental)."
        )
