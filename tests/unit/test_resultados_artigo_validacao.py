"""Garante que os três casos do artigo ERIAC continuam reproduzindo as faturas reais.

Camada 1 (tarifas líquidas impressas na fatura), sem banco:
CEMIG 12/2023 (Verde), Copel 04/2023 (Verde) e Equatorial Tucuruí Núcleo
12/2024 (Optante B). Critério: ≤ R$ 0,05 por item e ≤ R$ 1,00 no total técnico.
"""
import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "resultados_artigo",
    Path(__file__).resolve().parents[2] / "scripts" / "resultados_artigo.py",
)
ra = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ra)


@pytest.mark.parametrize("cfg", ra.CASOS_ARTIGO + [ra.CASO_OPTANTE], ids=lambda c: c["id"])
def test_caso_do_artigo_reproduz_fatura_real(cfg):
    r = ra.validar(cfg)
    assert all(l["motor"] is not None for l in r["linhas"]), r["linhas"]
    assert r["max_delta_linha"] <= ra.TOLERANCIA_LINHA, r["linhas"]
    assert abs(r["delta_total"]) <= ra.TOLERANCIA_TOTAL


def test_bandeira_e_tributada():
    """Adicional de bandeira recebe PIS/COFINS/ICMS (fatura Equatorial)."""
    r = ra.validar(ra.CASO_OPTANTE)
    bandeira = next(l for l in r["linhas"] if l["item"] == "Adicional de bandeira")
    assert bandeira["motor"] == pytest.approx(18.47, abs=0.05)


def test_copel_nao_e_elegivel_ao_optante_b():
    """Art. 292: transformação > 112,5 kVA e atividade comercial → inelegível."""
    from datetime import date
    from core.models import Consumidor
    from core.motor_calculo import elegivel_optante_b

    copel = next(c for c in ra.CASOS_ARTIGO if c["id"] == "copel")
    perfil = Consumidor(data_referencia=date(2023, 3, 15), **copel["perfil"])
    assert elegivel_optante_b(perfil) is False
