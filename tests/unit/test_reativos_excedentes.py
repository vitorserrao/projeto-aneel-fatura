"""Testes da cobrança de reativos excedentes (REN 1.000/2021, art. 304).

Cobrem o motor (ERE/DRE com aproximação A6) e o serviço (busca de VRERE/VRDRE
e avisos quando a tarifa de referência está ausente/ambígua).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from core.motor_calculo import calcular_fatura
from core.models import Consumidor
from core.tarifas import ParcelaTarifaria
from infra.repositories.tarifa_repository import TarifaVigente
from services.calculo_service import CalculoService

FR = 0.92  # fator de potência de referência (art. 304)


def _consumidor(**over):
    base = dict(
        distribuidora="DIST",
        subgrupo="A4",
        classe="Não se aplica",
        data_referencia=date(2024, 1, 1),
        detalhe="Não se aplica",
        consumo_ponta_kwh=100_000.0,
        consumo_fora_ponta_kwh=900_000.0,
        demanda_ponta_kw=1_000.0,
        demanda_fora_ponta_kw=2_000.0,
        demanda_contratada_ponta_kw=1_200.0,
        demanda_contratada_fora_ponta_kw=1_500.0,
        demanda_medida_unica_kw=1_500.0,
        demanda_contratada_unica_kw=1_000.0,
    )
    base.update(over)
    return Consumidor(**base)


def _parcelas_azul():
    return [
        ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 20.0),
        ParcelaTarifaria("TUSD", "DEMANDA", "FORA PONTA", "R$/kW", 10.0),
        ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 300.0),
        ParcelaTarifaria("TUSD", "ENERGIA", "FORA PONTA", "R$/MWh", 200.0),
        ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 400.0),
        ParcelaTarifaria("TE", "ENERGIA", "FORA PONTA", "R$/MWh", 350.0),
    ]


def _parcelas_verde():
    return [
        ParcelaTarifaria("TUSD", "DEMANDA", "PONTA", "R$/kW", 12.0),
        ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 300.0),
        ParcelaTarifaria("TUSD", "ENERGIA", "FORA PONTA", "R$/MWh", 200.0),
        ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 400.0),
        ParcelaTarifaria("TE", "ENERGIA", "FORA PONTA", "R$/MWh", 350.0),
    ]


def _fp(ativa, reativa):
    return ativa / ((ativa**2 + reativa**2) ** 0.5)


def test_ere_indutiva_fora_ponta_quantidade_aproximacao_a6():
    fatura = calcular_fatura(
        _consumidor(reativo_energia_fora_ponta_kvArh=500_000.0),
        "Azul",
        _parcelas_azul(),
        vrere_r_mwh=350.0,
        vrdre_r_kw=10.0,
    )
    linhas = [
        l
        for l in fatura.linhas
        if l.descricao == "Energia Reativa Excedente Indutiva (Fora Ponta)"
    ]
    assert linhas
    linha = linhas[0]
    ativa = 900_000.0 * (15.0 / 21.0)
    esperado_mwh = ativa * (FR / _fp(ativa, 500_000.0) - 1.0) * 0.001
    assert linha.quantidade == pytest.approx(esperado_mwh, rel=1e-12)
    assert linha.tarifa == 350.0
    assert linha.custo == pytest.approx(esperado_mwh * 350.0, rel=1e-12)


def test_ere_capacitiva_fora_ponta():
    fatura = calcular_fatura(
        _consumidor(reativo_energia_capacitiva_kvArh=300_000.0),
        "Azul",
        _parcelas_azul(),
        vrere_r_mwh=350.0,
    )
    linhas = [
        l
        for l in fatura.linhas
        if l.descricao == "Energia Reativa Excedente Capacitiva (Fora Ponta)"
    ]
    assert linhas
    ativa = 900_000.0 * (6.0 / 21.0)
    esperado_mwh = ativa * (FR / _fp(ativa, 300_000.0) - 1.0) * 0.001
    assert linhas[0].quantidade == pytest.approx(esperado_mwh, rel=1e-12)


def test_dre_azul_por_posto():
    fatura = calcular_fatura(
        _consumidor(
            reativo_energia_ponta_kvArh=600_000.0,
            reativo_energia_fora_ponta_kvArh=500_000.0,
        ),
        "Azul",
        _parcelas_azul(),
        vrere_r_mwh=350.0,
        vrdre_r_kw=10.0,
    )
    por_posto = {
        l.descricao: l
        for l in fatura.linhas
        if l.categoria == "REATIVOS" and l.descricao.startswith("Demanda")
    }
    assert "Demanda Reativa Excedente (Ponta)" in por_posto
    assert "Demanda Reativa Excedente (Fora Ponta)" in por_posto
    for linha in por_posto.values():
        assert linha.tarifa == 10.0
        assert linha.custo == pytest.approx(linha.quantidade * 10.0, rel=1e-12)


def test_dre_verde_linha_unica_com_vrdre_azul_fp():
    fatura = calcular_fatura(
        _consumidor(reativo_energia_fora_ponta_kvArh=500_000.0),
        "Verde",
        _parcelas_verde(),
        vrere_r_mwh=350.0,
        vrdre_r_kw=10.0,
        demanda_unica=True,
    )
    linhas = [
        l for l in fatura.linhas if l.descricao == "Demanda Reativa Excedente"
    ]
    assert linhas
    # Verde: usa a demanda única (medida 1500 = faturável 1500) e o VRDRE da
    # Azul fora ponta (10.0), não a demanda da Verde (12.0).
    assert linhas[0].tarifa == 10.0
    ativa_total = 1_000_000.0
    fp_total = _fp(ativa_total, 500_000.0)
    esperado_kw = 1_500.0 * (FR / fp_total) - 1_500.0
    assert linhas[0].quantidade == pytest.approx(esperado_kw, rel=1e-12)


def test_fp_acima_do_limite_nao_gera_linhas():
    fatura = calcular_fatura(
        _consumidor(reativo_energia_fora_ponta_kvArh=100_000.0),
        "Azul",
        _parcelas_azul(),
        vrere_r_mwh=350.0,
        vrdre_r_kw=10.0,
    )
    assert not [l for l in fatura.linhas if l.categoria == "REATIVOS"]


# ---------------------------------------------------------------------------
# Serviço — busca das tarifas de referência
# ---------------------------------------------------------------------------


def _t(componente, valor, unidade, subgrupo, modalidade, posto):
    return TarifaVigente(
        num_cnpj="00000000000000",
        sig_agente="DIST",
        componente=componente,
        valor=Decimal(str(valor)),
        resolucao="REH",
        inicio_vigencia=date(2024, 1, 1),
        fim_vigencia=date(2024, 12, 31),
        base_tarifaria="Tarifa de Aplicação",
        subgrupo=subgrupo,
        modalidade=modalidade,
        classe="Não se aplica",
        subclasse="Não se aplica",
        detalhe="Não se aplica",
        posto=posto,
        unidade=unidade,
    )


class _RepoFake:
    """Repositório mínimo para exercitar apenas os reativos."""

    def __init__(self, tarifas, bandeira=None):
        self._tarifas = tarifas
        self._bandeira = bandeira
        self.ultimos_filtros = []

    def buscar_tarifas(self, **filtros):
        self.ultimos_filtros.append(filtros)
        resultado = []
        for t in self._tarifas:
            if filtros.get("data") and not (
                t.inicio_vigencia <= filtros["data"] <= t.fim_vigencia
            ):
                continue
            if (
                filtros.get("sig_agente") is not None
                and t.sig_agente != filtros["sig_agente"]
            ):
                continue
            if (
                filtros.get("subgrupo") is not None
                and t.subgrupo != filtros["subgrupo"]
            ):
                continue
            if (
                filtros.get("modalidade") is not None
                and t.modalidade != filtros["modalidade"]
            ):
                continue
            if (
                filtros.get("componente") is not None
                and t.componente != filtros["componente"]
            ):
                continue
            if (
                filtros.get("unidade") is not None
                and t.unidade != filtros["unidade"]
            ):
                continue
            if filtros.get("posto") is not None and t.posto != filtros["posto"]:
                continue
            if (
                filtros.get("detalhe") is not None
                and t.detalhe != filtros["detalhe"]
            ):
                continue
            if (
                filtros.get("base_tarifaria") is not None
                and t.base_tarifaria != filtros["base_tarifaria"]
            ):
                continue
            resultado.append(t)
        return resultado

    def buscar_bandeira(self, competencia):
        return self._bandeira


def test_servico_busca_vrere_e_vrdre_e_gera_linhas():
    tarifas = [
        # modalidade simulada (Azul A4)
        _t("TUSD", 10.0, "kW", "A4", "Azul", "Fora ponta"),
        _t("TUSD", 20.0, "kW", "A4", "Azul", "Ponta"),
        _t("TUSD", 200.0, "MWh", "A4", "Azul", "Fora ponta"),
        _t("TUSD", 300.0, "MWh", "A4", "Azul", "Ponta"),
        _t("TE", 350.0, "MWh", "A4", "Azul", "Fora ponta"),
        _t("TE", 400.0, "MWh", "A4", "Azul", "Ponta"),
        # referências do art. 304 (VRDRE usa a MESMA Azul FP da modalidade;
        # VRERE vem do B1)
        _t("TE", 260.0, "MWh", "B1", "Convencional", "Não se aplica"),
    ]
    svc = CalculoService(_RepoFake(tarifas))
    consumidor = _consumidor(reativo_energia_fora_ponta_kvArh=500_000.0)
    resultado, nao_mapeadas, avisos = svc.calcular_detalhado(
        consumidor, "Azul", "Tarifa de Aplicação"
    )
    assert not nao_mapeadas
    assert avisos == []
    reat = [l for l in resultado.linhas if l.categoria == "REATIVOS"]
    assert reat
    energia = [
        l
        for l in reat
        if l.descricao == "Energia Reativa Excedente Indutiva (Fora Ponta)"
    ]
    assert energia and energia[0].tarifa == 260.0  # VRERE do B1


def test_servico_sem_vrere_emite_aviso_e_omite_energia_reativa():
    tarifas = [
        _t("TUSD", 10.0, "kW", "A4", "Azul", "Fora ponta"),
        _t("TUSD", 20.0, "kW", "A4", "Azul", "Ponta"),
        _t("TUSD", 200.0, "MWh", "A4", "Azul", "Fora ponta"),
        _t("TUSD", 300.0, "MWh", "A4", "Azul", "Ponta"),
        _t("TE", 350.0, "MWh", "A4", "Azul", "Fora ponta"),
        _t("TE", 400.0, "MWh", "A4", "Azul", "Ponta"),
        # sem B1 TE e sem duplicata de Azul FP (VRDRE único acima)
    ]
    svc = CalculoService(_RepoFake(tarifas))
    resultado, _, avisos = svc.calcular_detalhado(
        _consumidor(reativo_energia_fora_ponta_kvArh=500_000.0),
        "Azul",
        "Tarifa de Aplicação",
    )
    assert any(tipo == "reativos_sem_tarifa_referencia" for tipo, _ in avisos)
    # VRERE ausente → nenhuma linha de ENERGIA reativa excedente.
    assert not [
        l for l in resultado.linhas if l.descricao.startswith("Energia Reativa")
    ]


def test_servico_vrdre_ambiguo_emite_aviso():
    tarifas = [
        _t("TUSD", 10.0, "kW", "A4", "Azul", "Fora ponta"),
        _t("TUSD", 11.0, "kW", "A4", "Azul", "Fora ponta"),  # ambíguo
        _t("TUSD", 20.0, "kW", "A4", "Azul", "Ponta"),
        _t("TUSD", 200.0, "MWh", "A4", "Azul", "Fora ponta"),
        _t("TUSD", 300.0, "MWh", "A4", "Azul", "Ponta"),
        _t("TE", 350.0, "MWh", "A4", "Azul", "Fora ponta"),
        _t("TE", 400.0, "MWh", "A4", "Azul", "Ponta"),
        _t("TE", 260.0, "MWh", "B1", "Convencional", "Não se aplica"),
    ]
    svc = CalculoService(_RepoFake(tarifas))
    resultado, _, avisos = svc.calcular_detalhado(
        _consumidor(reativo_energia_fora_ponta_kvArh=500_000.0),
        "Azul",
        "Tarifa de Aplicação",
    )
    assert any(tipo == "reativos_tarifa_referencia_ambigua" for tipo, _ in avisos)
    # Energia (VRERE ok) pode existir; demanda (VRDRE ambíguo) deve ser omitida.
    assert not [
        l for l in resultado.linhas if l.descricao.startswith("Demanda Reativa")
    ]

def test_servico_vrdre_nulo_usa_nivel_imediatamente_inferior():
    """Art. 304 §3º: sem TUSD Azul FP no A4, usa o nível inferior (AS)."""
    tarifas = [
        _t("TUSD", 10.0, "kW", "AS", "Azul", "Fora ponta"),  # nível inferior
        _t("TUSD", 20.0, "kW", "A4", "Azul", "Ponta"),
        _t("TUSD", 200.0, "MWh", "A4", "Azul", "Fora ponta"),
        _t("TUSD", 300.0, "MWh", "A4", "Azul", "Ponta"),
        _t("TE", 350.0, "MWh", "A4", "Azul", "Fora ponta"),
        _t("TE", 400.0, "MWh", "A4", "Azul", "Ponta"),
        _t("TE", 260.0, "MWh", "B1", "Convencional", "Não se aplica"),
    ]
    svc = CalculoService(_RepoFake(tarifas))
    resultado, _, avisos = svc.calcular_detalhado(
        _consumidor(reativo_energia_fora_ponta_kvArh=500_000.0),
        "Azul",
        "Tarifa de Aplicação",
    )
    assert avisos == []
    demanda = [
        l for l in resultado.linhas
        if l.descricao.startswith("Demanda Reativa")
    ]
    assert demanda
    assert all(l.tarifa == 10.0 for l in demanda)

def test_servico_reativos_direto_auto_tarifa_vrere_vrdre():
    """Modo direto sem tarifa manual: usa VRERE/1000 e VRDRE do banco."""
    tarifas = [
        _t("TUSD", 10.0, "kW", "A4", "Azul", "Fora ponta"),  # VRDRE
        _t("TUSD", 20.0, "kW", "A4", "Azul", "Ponta"),
        _t("TUSD", 200.0, "MWh", "A4", "Azul", "Fora ponta"),
        _t("TUSD", 300.0, "MWh", "A4", "Azul", "Ponta"),
        _t("TE", 350.0, "MWh", "A4", "Azul", "Fora ponta"),
        _t("TE", 400.0, "MWh", "A4", "Azul", "Ponta"),
        _t("TE", 260.0, "MWh", "B1", "Convencional", "Não se aplica"),  # VRERE
    ]
    svc = CalculoService(_RepoFake(tarifas))
    consumidor = _consumidor(
        reativo_energia_fora_ponta_kvArh=39.36,
        reativo_demanda_fora_ponta_kvAr=5.0,
    )
    resultado, _, avisos = svc.calcular_detalhado(
        consumidor, "Azul", "Tarifa de Aplicação",
        reativos_direto=True,  # sem tarifas manuais -> automático
    )
    assert avisos == []
    reat = [l for l in resultado.linhas if l.categoria == "REATIVOS"]
    energia = [l for l in reat if l.descricao.startswith("Consumo Excessivo")]
    demanda = [l for l in reat if l.descricao.startswith("Demanda Excessiva")]
    assert energia and energia[0].tarifa == pytest.approx(0.26)  # 260/1000
    assert demanda and demanda[0].tarifa == pytest.approx(10.0)  # VRDRE


def test_servico_reativos_direto_tarifa_manual_prioritaria():
    """Tarifa manual informada tem prioridade sobre o automático."""
    tarifas = [
        _t("TUSD", 10.0, "kW", "A4", "Azul", "Fora ponta"),
        _t("TUSD", 20.0, "kW", "A4", "Azul", "Ponta"),
        _t("TUSD", 200.0, "MWh", "A4", "Azul", "Fora ponta"),
        _t("TUSD", 300.0, "MWh", "A4", "Azul", "Ponta"),
        _t("TE", 350.0, "MWh", "A4", "Azul", "Fora ponta"),
        _t("TE", 400.0, "MWh", "A4", "Azul", "Ponta"),
        _t("TE", 260.0, "MWh", "B1", "Convencional", "Não se aplica"),
    ]
    svc = CalculoService(_RepoFake(tarifas))
    resultado, _, avisos = svc.calcular_detalhado(
        _consumidor(reativo_energia_fora_ponta_kvArh=39.36),
        "Azul",
        "Tarifa de Aplicação",
        reativos_direto=True,
        tarifa_reativo_energia_r_kvarh=0.37881,  # override manual
    )
    assert avisos == []
    energia = [
        l for l in resultado.linhas
        if l.categoria == "REATIVOS" and l.descricao.startswith("Consumo Excessivo")
    ]
    assert energia and energia[0].tarifa == pytest.approx(0.37881)

