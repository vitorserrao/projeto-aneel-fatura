"""Parâmetros regulatórios e de configuração (sprint Verde × Azul).

Nenhum valor deste módulo é fórmula tarifária — as tarifas continuam vindo
sempre do ``TarifaRepository``. Os parâmetros abaixo são os números
regulatórios usados pela simulação e ficam AQUI, nunca fixados no ``core``:
a camada de serviço os lê e repassa explicitamente para as funções puras do
core (o core não importa este módulo e continua importável sem infra).
"""

from __future__ import annotations

# TODO: confirmar artigo REN 1000/2021
DEMANDA_MINIMA_KW = 30.0

# TODO: confirmar artigo REN 1000/2021
TOLERANCIA_ULTRAPASSAGEM = 0.05

# TODO: confirmar artigo REN 1000/2021
FATOR_ULTRAPASSAGEM = 2.0

# TODO: confirmar artigo REN 1000/2021
# Por distribuidora, se o dado existir. Valor usado como padrão quando a
# distribuidora não publica as horas de ponta.
HORAS_PONTA_POR_DIA = 3.0

# Feriados nacionais fixos (mês, dia) usados para contar dias úteis no ciclo
# de leitura. Feriados móveis, estaduais e municipais ficam fora por ora
# (pendência registrada em docs/regras.md).
FERIADOS_NACIONAIS = (
    (1, 1),   # Confraternização Universal
    (4, 21),  # Tiradentes
    (5, 1),   # Dia do Trabalho
    (9, 7),   # Independência
    (10, 12), # Nossa Senhora Aparecida
    (11, 2),  # Finados
    (11, 15), # Proclamação da República
    (12, 25), # Natal
)
