"""Testes do calendário de feriados de posto tarifário (sprint feriados)."""

from datetime import date

import pytest

import config
from core.calendario import (
    CHAVE_CARNAVAL,
    CHAVE_CONSCIENCIA_NEGRA,
    CHAVE_CORPUS,
    CHAVE_FIXOS,
    CHAVE_PAIXAO,
    feriados_postos_tarifarios,
    pascoa,
)
from core.otimizador import horas_ponta

_CONFIG_PADRAO = ("fixos", "carnaval", "paixao_de_cristo", "corpus_christi")


def test_pascoa_valores_conhecidos():
    assert pascoa(2024) == date(2024, 3, 31)
    assert pascoa(2025) == date(2025, 4, 20)
    assert pascoa(2026) == date(2026, 4, 5)


def test_moveis_2026_derivados_da_pascoa():
    feriados = feriados_postos_tarifarios(2026, _CONFIG_PADRAO)
    assert date(2026, 2, 17) in feriados  # Carnaval (Páscoa − 47)
    assert date(2026, 4, 3) in feriados   # Paixão de Cristo (Páscoa − 2)
    assert date(2026, 6, 4) in feriados   # Corpus Christi (Páscoa + 60)


def test_ciclo_com_carnaval_tem_3h_a_menos():
    com = feriados_postos_tarifarios(2026, _CONFIG_PADRAO)
    sem_carnaval = {d for d in com if d != date(2026, 2, 17)}
    ciclo = (date(2026, 2, 16), date(2026, 2, 20))
    assert horas_ponta(*ciclo, sem_carnaval, 3.0) == pytest.approx(12.0)
    assert horas_ponta(*ciclo, com, 3.0) == pytest.approx(9.0)


def test_ciclo_dez_jan_considera_feriados_dos_dois_anos():
    feriados = (
        feriados_postos_tarifarios(2025, _CONFIG_PADRAO)
        | feriados_postos_tarifarios(2026, _CONFIG_PADRAO)
    )
    # 29/12/2025 (seg) → 02/01/2026 (sex): 30/12, 31/12, 01/01 (feriado), 02/01.
    # Sem o 01/01 seriam 4 dias úteis; com o feriado, 3 dias úteis = 9 h.
    assert horas_ponta(
        date(2025, 12, 29), date(2026, 1, 2), feriados, 3.0
    ) == pytest.approx(9.0)
    assert date(2026, 1, 1) in feriados
    assert date(2025, 12, 25) in feriados


def test_feriado_em_fim_de_semana_nao_desconta_duas_vezes():
    # 15/11/2026 é domingo (Proclamação da República). Num ciclo que já exclui
    # o domingo, adicionar o feriado não pode reduzir as horas novamente.
    ciclo = (date(2026, 11, 13), date(2026, 11, 17))  # sex → ter
    sem = feriados_postos_tarifarios(2026, ("fixos",))
    com = sem | {date(2026, 11, 15)}
    assert horas_ponta(*ciclo, sem, 3.0) == horas_ponta(*ciclo, com, 3.0)
    assert horas_ponta(*ciclo, sem, 3.0) == pytest.approx(6.0)  # seg e ter


def test_consciencia_negra_configuravel_desligada_por_padrao():
    assert CHAVE_CONSCIENCIA_NEGRA not in config.FERIADOS_POSTO_TARIFARIO
    assert config.INCLUIR_CONSCIENCIA_NEGRA is False
    sem = feriados_postos_tarifarios(2026, _CONFIG_PADRAO)
    assert date(2026, 11, 20) not in sem
    com = feriados_postos_tarifarios(
        2026, _CONFIG_PADRAO + ("consciencia_negra",)
    )
    assert date(2026, 11, 20) in com
