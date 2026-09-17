"""Testes do EPI (permanece pendente — premissa P2)."""

import pytest

from core.epi import FormulaEPINaoDefinida, calcular_epi


def test_calcular_epi_permanece_pendente_sem_inventar_formula():
    with pytest.raises(FormulaEPINaoDefinida):
        calcular_epi(preco_referencia_acl=250.0)
