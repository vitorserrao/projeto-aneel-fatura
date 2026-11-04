"""Testes unitários do CalculoService (mapeamento grandeza/posto) sem banco.

Cobrem as funções puras de derivação de ``grandeza``/``posto`` a partir de uma
``TarifaVigente`` (contrato do repositório), sem conexão de banco.
"""

from datetime import date
from decimal import Decimal

from infra.repositories.tarifa_repository import TarifaVigente
from core.models import POSTO_INTERMEDIARIO
from services.calculo_service import _grandeza_de, _posto_de


def _t(unidade: str, posto: str) -> TarifaVigente:
    return TarifaVigente(
        num_cnpj="00000000000000",
        sig_agente="DIST",
        componente="TUSD",
        valor=Decimal("10.0"),
        resolucao="REH",
        inicio_vigencia=date(2024, 1, 1),
        fim_vigencia=date(2024, 12, 31),
        base_tarifaria="Tarifa de Aplicação",
        subgrupo="A4",
        modalidade="Azul",
        classe="Não se aplica",
        subclasse="Não se aplica",
        detalhe="Não se aplica",
        posto=posto,
        unidade=unidade,
    )


def test_grandeza_mwh_e_kw():
    assert _grandeza_de(_t("MWh", "Ponta")) == "ENERGIA"
    assert _grandeza_de(_t("kWh", "Ponta")) == "ENERGIA"
    assert _grandeza_de(_t("kW", "Ponta")) == "DEMANDA"


def test_grandeza_desconhecida_nao_mapeada():
    assert _grandeza_de(_t("kvarh", "Ponta")) is None


def test_posto_literal():
    assert _posto_de(_t("kW", "Ponta")) == "PONTA"
    assert _posto_de(_t("kW", "Fora ponta")) == "FORA PONTA"
    assert _posto_de(_t("kW", "Fora de ponta")) == "FORA PONTA"


def test_posto_legado_nao_mapeado():
    # seca/úmida/intermediário não dobram em Ponta/Fora (regra P5 pendente)
    assert _posto_de(_t("MWh", "Ponta seca")) is None
    assert _posto_de(_t("MWh", "Fora ponta úmida")) is None
    assert _posto_de(_t("MWh", "Intermediário")) == POSTO_INTERMEDIARIO
    assert _posto_de(_t("MWh", "Não se aplica")) is None
