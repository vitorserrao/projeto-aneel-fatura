"""Testes do Optante B (REN 1.000/2021, art. 292): elegibilidade e faturamento.

Cobrem:
- elegibilidade: refletores ≥ 2/3 apenas para atividades esportivas/parques
  agropecuários; hotelaria/turismo independente de potência;
- motor: fatura monômia (sem demanda, sem ultrapassagem);
- serviço: subgrupo B derivado da atividade, filtro por classe/subclasse,
  guarda de ambiguidade (premissa A5/P6) e custo de disponibilidade
  (arts. 290/291) aplicado ao Optante B.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from core.motor_calculo import calcular_fatura, modalidades_elegiveis
from core.models import Consumidor
from core.tarifas import ParcelaTarifaria
from infra.repositories.tarifa_repository import TarifaVigente
from services.calculo_service import CalculoService


def _consumidor(**over):
    base = dict(
        distribuidora="DIST",
        subgrupo="A4",
        classe="Não se aplica",
        subclasse="Não se aplica",
        data_referencia=date(2024, 1, 1),
        detalhe="Não se aplica",
        consumo_ponta_kwh=100.0,
        consumo_fora_ponta_kwh=900.0,
        demanda_ponta_kw=50.0,
        demanda_fora_ponta_kw=50.0,
        demanda_contratada_ponta_kw=100.0,
        demanda_contratada_fora_ponta_kw=100.0,
        potencia_transformadores_kva=100.0,
    )
    base.update(over)
    return Consumidor(**base)


def _t(
    componente,
    valor,
    unidade,
    subgrupo,
    modalidade,
    posto,
    classe="Não se aplica",
    subclasse="Não se aplica",
):
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
        classe=classe,
        subclasse=subclasse,
        detalhe="Não se aplica",
        posto=posto,
        unidade=unidade,
    )


class _RepoFake:
    """Repositório mínimo com filtros de classe/subclasse."""

    def __init__(self, tarifas):
        self._tarifas = tarifas
        self.ultimos_filtros = []

    def buscar_tarifas(self, **filtros):
        self.ultimos_filtros.append(filtros)
        resultado = []
        for t in self._tarifas:
            if filtros.get("data") is not None and not (
                t.inicio_vigencia <= filtros["data"] <= t.fim_vigencia
            ):
                continue
            if not all(
                filtros.get(campo) is None or getattr(t, campo) == filtros[campo]
                for campo in (
                    "sig_agente",
                    "subgrupo",
                    "modalidade",
                    "classe",
                    "subclasse",
                    "detalhe",
                    "posto",
                    "unidade",
                    "componente",
                    "base_tarifaria",
                )
            ):
                continue
            resultado.append(t)
        return resultado

    def buscar_bandeira(self, competencia):
        return None


# ---------------------------------------------------------------------------
# Elegibilidade (art. 292)
# ---------------------------------------------------------------------------


def test_refletores_apenas_para_atividade_esportiva_ou_parque():
    dados = dict(
        potencia_transformadores_kva=0.0,
        carga_refletores_kw=20.0,
        carga_instalada_total_kw=30.0,  # 2/3
    )
    assert "OPTANTE B" in modalidades_elegiveis(
        _consumidor(atividade="Esportivo ou Parque Agropecuário", **dados)
    )
    assert "OPTANTE B" not in modalidades_elegiveis(
        _consumidor(atividade="Comercial ou Industrial", **dados)
    )


def test_hotelaria_turismo_elegivel_independente_de_potencia():
    assert "OPTANTE B" in modalidades_elegiveis(
        _consumidor(hotelaria_turismo=True, potencia_transformadores_kva=0.0)
    )


# ---------------------------------------------------------------------------
# Motor: fatura monômia
# ---------------------------------------------------------------------------


def test_motor_optante_b_e_monomia_sem_demanda_nem_ultrapassagem():
    parcelas = [
        ParcelaTarifaria("TUSD", "ENERGIA", "PONTA", "R$/MWh", 50.0),
        ParcelaTarifaria("TUSD", "ENERGIA", "FORA PONTA", "R$/MWh", 50.0),
        ParcelaTarifaria("TE", "ENERGIA", "PONTA", "R$/MWh", 150.0),
        ParcelaTarifaria("TE", "ENERGIA", "FORA PONTA", "R$/MWh", 150.0),
    ]
    fatura = calcular_fatura(_consumidor(), "Optante B", parcelas)
    descricoes = [l.descricao for l in fatura.linhas]
    assert not any("DEMANDA" in d for d in descricoes)
    assert not any(l.categoria == "ULTRAPASSAGEM" for l in fatura.linhas)
    # Consumo total (100 + 900 kWh) × tarifa única (50 + 150 R$/MWh).
    assert fatura.custo_total == pytest.approx(1000.0 * 0.001 * 200.0)


# ---------------------------------------------------------------------------
# Serviço: subgrupo B, classe/subclasse, ambiguidade e disponibilidade
# ---------------------------------------------------------------------------


def test_servico_optante_b_usa_tarifa_b1_da_classe_do_perfil():
    tarifas = [
        # B1 Convencional: duas classes na mesma vigência — o filtro do
        # perfil (Residencial) deve escolher UMA tarifa, sem somar as duas.
        _t(
            "TE", 20.0, "MWh", "B1", "Convencional", "Não se aplica",
            classe="Residencial", subclasse="Residencial",
        ),
        _t(
            "TE", 30.0, "MWh", "B1", "Convencional", "Não se aplica",
            classe="Residencial Baixa Renda", subclasse="Residencial Baixa Renda",
        ),
    ]
    repo = _RepoFake(tarifas)
    svc = CalculoService(repo)
    consumidor = _consumidor(
        classe="Residencial", subclasse="Residencial", atividade="Residencial",
    )
    resultado, nao_mapeadas, avisos = svc.calcular_detalhado(
        consumidor, "Optante B", "Tarifa de Aplicação"
    )
    assert not nao_mapeadas
    assert avisos == []
    tarifarias = [l for l in resultado.linhas if l.categoria == "TARIFA"]
    assert len(tarifarias) == 2  # tarifa única → PONTA + FORA PONTA
    assert all(l.tarifa == 20.0 for l in tarifarias)
    assert resultado.custo_total == pytest.approx(1000.0 * 0.001 * 20.0)
    filtro = repo.ultimos_filtros[0]
    assert filtro["subgrupo"] == "B1"
    assert filtro["modalidade"] == "Convencional"
    assert filtro["classe"] == "Residencial"
    assert filtro["subclasse"] == "Residencial"


def test_servico_optante_b_deriva_classe_residencial_pela_atividade():
    """Optante B sem classe informada: deriva Residencial/Residencial."""
    tarifas = [
        _t(
            "TE", 20.0, "MWh", "B1", "Convencional", "Não se aplica",
            classe="Residencial", subclasse="Residencial",
        ),
        _t(
            "TE", 30.0, "MWh", "B1", "Convencional", "Não se aplica",
            classe="Residencial", subclasse="Baixa Renda",
        ),
    ]
    repo = _RepoFake(tarifas)
    svc = CalculoService(repo)
    # classe/subclasse "Não se aplica" (default) → derivação pela atividade.
    consumidor = _consumidor(atividade="Residencial")
    resultado, nao_mapeadas, avisos = svc.calcular_detalhado(
        consumidor, "Optante B", "Tarifa de Aplicação"
    )
    assert not nao_mapeadas
    assert avisos == []
    tarifarias = [l for l in resultado.linhas if l.categoria == "TARIFA"]
    assert len(tarifarias) == 2
    assert all(l.tarifa == 20.0 for l in tarifarias)
    filtro = repo.ultimos_filtros[0]
    assert filtro["subgrupo"] == "B1"
    assert filtro["classe"] == "Residencial"  # derivada da atividade
    assert filtro["subclasse"] == "Residencial"  # derivada da atividade


def test_servico_optante_b_deriva_subclasse_rural():
    """Atividade rural deriva B2 + classe Rural + subclasse 'Não se aplica'."""
    tarifas = [
        _t(
            "TE", 40.0, "MWh", "B2", "Convencional", "Não se aplica",
            classe="Rural", subclasse="Não se aplica",
        ),
        _t(
            "TE", 45.0, "MWh", "B2", "Convencional", "Não se aplica",
            classe="Rural", subclasse="Cooperativa de eletrificação rural",
        ),
    ]
    repo = _RepoFake(tarifas)
    svc = CalculoService(repo)
    consumidor = _consumidor(atividade="Rural")
    resultado, _, avisos = svc.calcular_detalhado(
        consumidor, "Optante B", "Tarifa de Aplicação"
    )
    assert avisos == []
    tarifarias = [l for l in resultado.linhas if l.categoria == "TARIFA"]
    assert all(l.tarifa == 40.0 for l in tarifarias)
    filtro = repo.ultimos_filtros[0]
    assert filtro["subgrupo"] == "B2"
    assert filtro["classe"] == "Rural"
    assert filtro["subclasse"] == "Não se aplica"


def test_servico_optante_b_classe_informada_tem_prioridade_sobre_derivacao():
    tarifas = [
        _t(
            "TE", 20.0, "MWh", "B1", "Convencional", "Não se aplica",
            classe="Residencial", subclasse="Residencial",
        ),
        _t(
            "TE", 30.0, "MWh", "B1", "Convencional", "Não se aplica",
            classe="Residencial", subclasse="Baixa Renda",
        ),
    ]
    repo = _RepoFake(tarifas)
    svc = CalculoService(repo)
    consumidor = _consumidor(
        atividade="Residencial",  # derivaria Residencial/Residencial...
        classe="Residencial",  # ...mas o perfil informa Baixa Renda
        subclasse="Baixa Renda",
    )
    resultado, _, avisos = svc.calcular_detalhado(
        consumidor, "Optante B", "Tarifa de Aplicação"
    )
    assert avisos == []
    tarifarias = [l for l in resultado.linhas if l.categoria == "TARIFA"]
    assert all(l.tarifa == 30.0 for l in tarifarias)
    assert repo.ultimos_filtros[0]["classe"] == "Residencial"
    assert repo.ultimos_filtros[0]["subclasse"] == "Baixa Renda"


def test_servico_optante_b_sem_classe_recusa_tarifa_ambigua():
    # B3 (Comercial × Industrial): atividade sem derivação de classe — a
    # guarda de ambiguidade (A5) recusa em vez de somar valores distintos.
    tarifas = [
        _t(
            "TE", 10.0, "MWh", "B3", "Convencional", "Não se aplica",
            classe="Comercial",
        ),
        _t(
            "TE", 15.0, "MWh", "B3", "Convencional", "Não se aplica",
            classe="Industrial",
        ),
    ]
    repo = _RepoFake(tarifas)
    svc = CalculoService(repo)
    consumidor = _consumidor(atividade="Comercial ou Industrial")
    with pytest.raises(ValueError, match="nenhuma tarifa aplicável"):
        svc.calcular_detalhado(consumidor, "Optante B", "Tarifa de Aplicação")
    filtro = repo.ultimos_filtros[0]
    assert filtro["classe"] is None  # B3: nenhuma derivação automática
    assert filtro["subclasse"] is None


def test_servico_optante_b_deriva_b3_e_aplica_custo_de_disponibilidade():
    tarifas = [
        _t(
            "TE", 10.0, "MWh", "B3", "Convencional", "Não se aplica",
            classe="Comercial", subclasse="Comercial",
        ),
    ]
    repo = _RepoFake(tarifas)
    svc = CalculoService(repo)
    consumidor = _consumidor(
        atividade="Comercial ou Industrial",
        classe="Comercial",
        subclasse="Comercial",
        tipo_ligacao="Trifásico",  # mínimo 100 kWh
        consumo_ponta_kwh=10.0,
        consumo_fora_ponta_kwh=20.0,  # total 30 < 100 → fatura o mínimo
    )
    resultado, _, avisos = svc.calcular_detalhado(
        consumidor, "Optante B", "Tarifa de Aplicação"
    )
    assert avisos == []
    tarifarias = [l for l in resultado.linhas if l.categoria == "TARIFA"]
    total_kwh = sum(l.quantidade for l in tarifarias) * 1000.0
    assert total_kwh == pytest.approx(100.0)  # mínimo faturado (art. 290/291)
    assert resultado.custo_total == pytest.approx(100.0 * 0.001 * 10.0)
    assert repo.ultimos_filtros[0]["subgrupo"] == "B3"
