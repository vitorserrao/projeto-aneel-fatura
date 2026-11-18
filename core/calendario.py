"""Calendário de feriados para postos tarifários (core puro).

Implementa apenas manipulação determinística de datas: a Páscoa pelo
algoritmo de Meeus/Jones/Butcher (calendário gregoriano) e os feriados
derivados dela. A LISTA de quais feriados valem para posto tarifário vem da
configuração (``lista_config``), mantendo o core sem dependência de
infraestrutura/configuração.

Feriados estaduais e municipais ficam fora (registrado em docs/regras.md).
"""

from __future__ import annotations

from datetime import date, timedelta

_FERIADOS_FIXOS = (
    (1, 1),   # Confraternização Universal
    (4, 21),  # Tiradentes
    (5, 1),   # Dia do Trabalho
    (9, 7),   # Independência
    (10, 12), # Nossa Senhora Aparecida
    (11, 2),  # Finados
    (11, 15), # Proclamação da República
    (12, 25), # Natal
)

# Chaves reconhecidas em ``lista_config``.
CHAVE_FIXOS = "fixos"
CHAVE_CARNAVAL = "carnaval"
CHAVE_PAIXAO = "paixao_de_cristo"
CHAVE_CORPUS = "corpus_christi"
CHAVE_CONSCIENCIA_NEGRA = "consciencia_negra"


def pascoa(ano: int) -> date:
    """Domingo de Páscoa no calendário gregoriano (Meeus/Jones/Butcher)."""
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)


def feriados_postos_tarifarios(ano: int, lista_config) -> set[date]:
    """Feriados de posto tarifário de um ano.

    Combina os feriados fixos nacionais e os móveis derivados da Páscoa
    (Carnaval = Páscoa − 47; Paixão de Cristo = Páscoa − 2; Corpus Christi =
    Páscoa + 60) conforme ``lista_config``. O 20/11 (Consciência Negra) é um
    item configurável — só entra quando a chave ``consciencia_negra`` está na
    lista (desligado por padrão na configuração).
    """
    config = set(lista_config)
    datas: set[date] = set()
    if CHAVE_FIXOS in config:
        datas.update(date(ano, mes, dia) for mes, dia in _FERIADOS_FIXOS)
    if CHAVE_CARNAVAL in config:
        datas.add(pascoa(ano) - timedelta(days=47))
    if CHAVE_PAIXAO in config:
        datas.add(pascoa(ano) - timedelta(days=2))
    if CHAVE_CORPUS in config:
        datas.add(pascoa(ano) + timedelta(days=60))
    if CHAVE_CONSCIENCIA_NEGRA in config:
        datas.add(date(ano, 11, 20))
    return datas
