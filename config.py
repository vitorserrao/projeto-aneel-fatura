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

# TODO: confirmar lista na REN 1000/2021
# Quais feriados valem para a contagem de dias úteis dos postos tarifários.
# "fixos" cobre os feriados nacionais de data fixa; os demais são móveis
# (derivados da Páscoa) calculados em core/calendario.py.
FERIADOS_POSTO_TARIFARIO = (
    "fixos",
    "carnaval",
    "paixao_de_cristo",
    "corpus_christi",
)

# TODO: confirmar se a REN 1000/ANEEL considera para posto tarifário
# 20/11 (Consciência Negra) é item configurável e fica DESLIGADO por padrão.
INCLUIR_CONSCIENCIA_NEGRA = False

# Tolerância da contraprova com faturas reais: diferença aceitável no total
# da fatura simulada em relação à fatura real (fração; 0.01 = 1%).
TOLERANCIA_VALIDACAO = 0.01

# Súmula 391 do STJ: a demanda contratada e NÃO utilizada é isenta de ICMS
# (incide apenas PIS/COFINS). False = aplica a isenção (regra das faturas
# reais Copel/CEMIG); True = reproduz o comportamento antigo, com ICMS sobre
# toda a demanda faturada.
ICMS_DEMANDA_NAO_UTILIZADA = False
