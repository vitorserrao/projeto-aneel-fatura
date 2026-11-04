"""Serviço de otimização de modalidades (orquestração de cálculo por modalidade).

Este módulo implementa o caso de uso "comparar modalidades aplicáveis e
indicar a de menor custo no ACR". Orquestra o ``CalculoService`` para cada
modalidade candidata e o ``core.otimizador`` para a seleção determinística.

Regras usadas aqui:

- A lista de modalidades a comparar é passada explicitamente pelo chamador.
- Se nenhuma modalidade for informada, o padrão são as modalidades do Grupo A
  ELEGÍVEIS para o perfil (``core.motor_calculo.modalidades_elegiveis``):
  Azul sempre; Verde em A3a/A4/AS; Optante B quando atende o art. 292.

A escolha do menor custo é determinística (core.otimizador ordena por custo
total com desempate estável).
"""

from __future__ import annotations

from typing import Iterable

from core.models import Consumidor, ResultadoOtimizacao
from core.motor_calculo import modalidades_elegiveis
from core.otimizador import otimizar_modalidade

from .calculo_service import BASE_PADRAO


class OtimizacaoService:
    """Caso de uso: comparar modalidades e selecionar a de menor custo ACR."""

    def __init__(self, calculo_service):
        self._calculo = calculo_service

    def otimizar(
        self,
        consumidor: Consumidor,
        modalidades: Iterable[str] | None = None,
        base_tarifaria: str = BASE_PADRAO,
    ) -> ResultadoOtimizacao:
        """Calcula cada modalidade candidata e retorna a de menor custo.

        Args:
            consumidor: perfil do consumidor (com data de referência).
            modalidades: modalidades a comparar (ex.: ("AZUL", "VERDE")).
                Se ``None``, usa as modalidades do Grupo A elegíveis para o
                perfil (Azul sempre; Verde quando aplicável; Optante B quando
                atende o art. 292).
            base_tarifaria: base da fatura (padrão: Tarifa de Aplicação).

        Raises:
            ValueError: nenhuma modalidade fornecida (lista vazia), ou erro
                de cálculo em alguma modalidade (ex.: tarifa ausente).
        """
        candidatas = (
            tuple(modalidades)
            if modalidades is not None
            else tuple(modalidades_elegiveis(consumidor))
        )
        if not candidatas:
            raise ValueError("nenhuma modalidade para comparar")

        resultados = [
            self._calculo.calcular(consumidor, m, base_tarifaria)
            for m in candidatas
        ]
        return otimizar_modalidade(resultados)
