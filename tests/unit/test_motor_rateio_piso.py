"""Testes do rateio de consumo por leitura e do piso de demanda (motor)."""

from datetime import date

from core.motor_calculo import calcular_fatura
from core.models import Consumidor
from core.tarifas import ParcelaTarifaria


def _consumidor(**over):
    base = dict(
        distribuidora="DIST",
        subgrupo="A4",
        classe="Não se aplica",
        data_referencia=date(2024, 1, 1),
        detalhe="Não se aplica",
        consumo_ponta_kwh=1000.0,
        consumo_fora_ponta_kwh=2000.0,
        demanda_ponta_kw=100.0,
        demanda_fora_ponta_kw=200.0,
        demanda_contratada_ponta_kw=120.0,
        demanda_contratada_fora_ponta_kw=180.0,
    )
    base.update(over)
    return Consumidor(**base)


def _parcelas():
    return [
        ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 300.0),
        ParcelaTarifaria("TUSD", "ENERGIA", "FORA PONTA", "R$/MWh", 200.0),
        ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 20.0),
        ParcelaTarifaria("TUSD", "DEMANDA", "FORA PONTA", "R$/kW", 10.0),
    ]


def test_rateio_mes_anterior_e_atual():
    fatura = calcular_fatura(
        _consumidor(percentual_mes_anterior=0.3), "Azul", _parcelas()
    )
    linhas = fatura.linhas
    # energia ponta: 2 linhas (mês anterior + atual)
    ponta = [l for l in linhas if l.descricao.startswith("TUSD ENERGIA PONTA")]
    assert len(ponta) == 2
    ant = next(l for l in ponta if "anterior" in l.descricao)
    atual = next(l for l in ponta if "atual" in l.descricao)
    # quantidade em MWh (1000 kWh = 1.0 MWh)
    assert abs(ant.quantidade - 0.3) < 1e-9
    assert abs(atual.quantidade - 0.7) < 1e-9
    # soma das duas deve dar a quantidade total original (1.0 MWh)
    assert abs(ant.quantidade + atual.quantidade - 1.0) < 1e-9


def test_sem_rateio_linha_unica():
    fatura = calcular_fatura(_consumidor(), "Azul", _parcelas())
    ponta = [l for l in fatura.linhas if "TUSD ENERGIA PONTA" in l.descricao]
    assert len(ponta) == 1
    assert abs(ponta[0].quantidade - 1.0) < 1e-9


def test_piso_demanda():
    # demanda faturável máx(contratada, medida) já dá 120/180; com piso 200
    # a ponta (120) sobe para 200.
    fatura = calcular_fatura(_consumidor(), "Azul", _parcelas(), piso_demanda_kw=200.0)
    demanda_ponta = [l for l in fatura.linhas if l.descricao == "TUSD DEMANDA PONTA"]
    assert demanda_ponta, "linha de demanda ponta ausente"
    assert abs(demanda_ponta[0].quantidade - 200.0) < 1e-9


def test_tributos_aditivos():
    sem = calcular_fatura(_consumidor(), "Azul", _parcelas())
    com = calcular_fatura(
        _consumidor(), "Azul", _parcelas(),
        aplicar_tributos=True, pis=0.0065, cofins=0.03, icms=0.18,
        tipo_icms="dentro",
    )
    # fator = 1 / (1 - 0.0065 - 0.03 - 0.18) = 1 / 0.7835
    fator_esperado = 1.0 / 0.7835
    assert com.custo_tarifas > 0
    # Apenas as linhas TARIFA escalam pelo fator (ultrapassagem/encargos não).
    assert abs((com.custo_tarifas / sem.custo_tarifas) - fator_esperado) < 1e-9


def test_tributos_invalidos():
    import pytest
    with pytest.raises(ValueError):
        calcular_fatura(
            _consumidor(), "Azul", _parcelas(),
            aplicar_tributos=True, pis=0.3, cofins=0.4, icms=0.4,
            tipo_icms="dentro",
        )


def test_tributos_padrao_multiplicativo():
    # Padrão = forma multiplicativa ("fora"), validada nas faturas reais
    # (Copel, CEMIG, Equatorial): fator = 1 / ((1 - PIS - COFINS) × (1 - ICMS)).
    sem = calcular_fatura(_consumidor(), "Azul", _parcelas())
    com = calcular_fatura(
        _consumidor(), "Azul", _parcelas(),
        aplicar_tributos=True, pis=0.0065, cofins=0.03, icms=0.18,
    )
    fator_esperado = 1.0 / ((1 - 0.0065 - 0.03) * (1 - 0.18))
    assert abs((com.custo_tarifas / sem.custo_tarifas) - fator_esperado) < 1e-9
