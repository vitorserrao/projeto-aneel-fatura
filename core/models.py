"""Modelos de domínio do núcleo tarifário.

Esta camada contém apenas estruturas de dados e o vocabulário de contrato do
core. Nenhuma fórmula regulatória é definida aqui — fórmulas vivem em
``motor_calculo``/``otimizador``/``epi`` e apenas quando formalmente validadas
(docs/premissas.md e docs/regras_tarifarias.md).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

# ---------------------------------------------------------------------------
# Vocabulário normalizado do contrato do core
# ---------------------------------------------------------------------------
# A ingestão (Sprint 2) deve converter os valores reais do dataset ANEEL para
# estes identificadores antes de chamar o motor. A correspondência com os
# códigos oficiais do dataset é pendência documental (docs/premissas.md, P5).

POSTO_PONTA = "PONTA"
POSTO_FORA_PONTA = "FORA PONTA"
POSTO_INTERMEDIARIO = "INTERMEDIARIO"
POSTOS_SUPORTADOS = (POSTO_PONTA, POSTO_FORA_PONTA, POSTO_INTERMEDIARIO)

GRANDEZA_ENERGIA = "ENERGIA"
GRANDEZA_DEMANDA = "DEMANDA"
GRANDEZAS_SUPORTADAS = (GRANDEZA_ENERGIA, GRANDEZA_DEMANDA)

COMPONENTE_TE = "TE"
COMPONENTE_TUSD = "TUSD"
COMPONENTES_SUPORTADOS = (COMPONENTE_TE, COMPONENTE_TUSD)

UNIDADE_R_MWH = "R$/MWh"
UNIDADE_R_KWH = "R$/kWh"
UNIDADE_R_KW = "R$/kW"


def _exigir_texto(valor: str, campo: str) -> None:
    if not valor.strip():
        raise ValueError(f"{campo} não pode ser vazio")


def _exigir_nao_negativo(valor: float, campo: str) -> None:
    if valor < 0:
        raise ValueError(f"{campo} não pode ser negativo (recebido {valor!r})")


@dataclass(frozen=True)
class Consumidor:
    """Perfil físico/contratual do consumidor para simulação.

    A modalidade tarifária é um parâmetro da simulação (``motor_calculo``/
    ``otimizador``), não uma propriedade fixa do consumidor — isso permite
    comparar o mesmo perfil sob modalidades diferentes (escopo do MVP).
    """

    distribuidora: str
    subgrupo: str
    classe: str
    data_referencia: date | None = None
    subclasse: str = ""
    detalhe: str = "Não se aplica"
    consumo_ponta_kwh: float = 0.0
    consumo_fora_ponta_kwh: float = 0.0
    consumo_intermediario_kwh: float = 0.0
    demanda_ponta_kw: float = 0.0
    demanda_fora_ponta_kw: float = 0.0
    # Demanda CONTRATADA (kW). A demanda faturável é o MAIOR valor entre a
    # contratada e a medida (REN ANEEL nº 1.000/2021, arts. 292 e 301).
    demanda_contratada_ponta_kw: float = 0.0
    demanda_contratada_fora_ponta_kw: float = 0.0
    # Demanda ÚNICA (sem posto) — usada na Verde (REN 1.000/2021: única
    # tarifa de demanda). Demanda faturável = máx(medida única, contratada
    # única).
    demanda_medida_unica_kw: float = 0.0
    demanda_contratada_unica_kw: float = 0.0
    # Linhas adicionais da fatura (referência: Simulador de Fatura do projeto
    # anterior; valores 0 = linha não aplicável).
    bandeira_adicional_r_kwh: float = 0.0
    cip_cosip_rs: float = 0.0
    outros_rs: float = 0.0
    # Reativos por posto (REN 1.000/2021, art. 304). Os campos abaixo são a
    # parcela INDUTIVA (horas complementares à janela capacitiva, 6h–24h).
    # A parcela CAPACITIVA (janela de 6h definida pela distribuidora entre
    # 23h30 e 6h30, sempre fora ponta) é informada separadamente nos campos
    # ``reativo_*_capacitiva_*`` (premissa A6 — aproximação por agregado mensal).
    reativo_energia_ponta_kvArh: float = 0.0
    reativo_energia_fora_ponta_kvArh: float = 0.0
    reativo_demanda_ponta_kvAr: float = 0.0
    reativo_demanda_fora_ponta_kvAr: float = 0.0
    reativo_energia_capacitiva_kvArh: float = 0.0
    reativo_demanda_capacitiva_kvAr: float = 0.0
    # Rateio de consumo entre leituras (Simulador: "% do consumo no mês
    # anterior", cols L13/M13). Fração ∈ [0,1]; 0 = tudo no mês atual.
    percentual_mes_anterior: float = 0.0
    # Optante B (REN 1.000/2021, art. 292): Grupo A faturado como Grupo B.
    atividade: str = "Comercial ou Industrial"
    tipo_ligacao: str = "Trifásico"
    pre_pagamento: bool = False
    potencia_transformadores_kva: float = 0.0
    cooperativa_eletrificacao_rural: bool = False
    hotelaria_turismo: bool = False
    carga_refletores_kw: float = 0.0
    carga_instalada_total_kw: float = 0.0

    def __post_init__(self) -> None:
        _exigir_texto(self.distribuidora, "distribuidora")
        _exigir_texto(self.subgrupo, "subgrupo")
        _exigir_texto(self.classe, "classe")
        _exigir_nao_negativo(self.consumo_ponta_kwh, "consumo_ponta_kwh")
        _exigir_nao_negativo(self.consumo_fora_ponta_kwh, "consumo_fora_ponta_kwh")
        _exigir_nao_negativo(self.demanda_ponta_kw, "demanda_ponta_kw")
        _exigir_nao_negativo(self.demanda_fora_ponta_kw, "demanda_fora_ponta_kw")
        _exigir_nao_negativo(
            self.demanda_contratada_ponta_kw, "demanda_contratada_ponta_kw"
        )
        _exigir_nao_negativo(
            self.demanda_contratada_fora_ponta_kw, "demanda_contratada_fora_ponta_kw"
        )
        _exigir_nao_negativo(self.demanda_medida_unica_kw, "demanda_medida_unica_kw")
        _exigir_nao_negativo(
            self.demanda_contratada_unica_kw, "demanda_contratada_unica_kw"
        )
        _exigir_nao_negativo(
            self.bandeira_adicional_r_kwh, "bandeira_adicional_r_kwh"
        )
        _exigir_nao_negativo(self.cip_cosip_rs, "cip_cosip_rs")
        _exigir_nao_negativo(self.outros_rs, "outros_rs")
        _exigir_nao_negativo(
            self.reativo_energia_ponta_kvArh, "reativo_energia_ponta_kvArh"
        )
        _exigir_nao_negativo(
            self.reativo_energia_fora_ponta_kvArh, "reativo_energia_fora_ponta_kvArh"
        )
        _exigir_nao_negativo(
            self.reativo_demanda_ponta_kvAr, "reativo_demanda_ponta_kvAr"
        )
        _exigir_nao_negativo(
            self.reativo_demanda_fora_ponta_kvAr, "reativo_demanda_fora_ponta_kvAr"
        )
        _exigir_nao_negativo(
            self.reativo_energia_capacitiva_kvArh, "reativo_energia_capacitiva_kvArh"
        )
        _exigir_nao_negativo(
            self.reativo_demanda_capacitiva_kvAr, "reativo_demanda_capacitiva_kvAr"
        )
        if not 0.0 <= self.percentual_mes_anterior <= 1.0:
            raise ValueError(
                "percentual_mes_anterior deve estar entre 0 e 1 "
                f"(recebido {self.percentual_mes_anterior!r})"
            )

    @property
    def consumo_total_kwh(self) -> float:
        """Consumo total de energia (grandeza aditiva entre postos)."""
        return (
            self.consumo_ponta_kwh
            + self.consumo_fora_ponta_kwh
            + self.consumo_intermediario_kwh
        )

    def demanda_faturavel_kw(self, posto: str) -> float:
        """Demanda faturável do posto = MAIOR entre contratada e medida.

        Regra oficial: REN ANEEL nº 1.000/2021 (arts. 292 e 301).
        """
        if posto == POSTO_PONTA:
            medida = self.demanda_ponta_kw
            contratada = self.demanda_contratada_ponta_kw
        else:
            medida = self.demanda_fora_ponta_kw
            contratada = self.demanda_contratada_fora_ponta_kw
        return max(medida, contratada)

    @property
    def demanda_faturavel_unica_kw(self) -> float:
        """Demanda fat. ÚNICA (Verde/Convencional) = máx(medida, contratada).

        REN 1.000/2021: modalidade com UMA única tarifa de demanda — não há
        separação por posto. Substitui a regra LARGE(P/FP) do XLSM.
        """
        return max(self.demanda_medida_unica_kw, self.demanda_contratada_unica_kw)


@dataclass(frozen=True)
class ParcelaCusto:
    """Parcela já calculada (quantidade × tarifa), rastreável e determinística."""

    componente: str
    grandeza: str
    posto: str
    quantidade: float
    tarifa: float
    custo: float


@dataclass(frozen=True)
class ResultadoCalculo:
    """Resultado determinístico do cálculo ACR para uma modalidade."""

    modalidade: str
    parcelas: tuple[ParcelaCusto, ...] = ()

    def __post_init__(self) -> None:
        _exigir_texto(self.modalidade, "modalidade")

    @property
    def custo_energia(self) -> float:
        return sum(p.custo for p in self.parcelas if p.grandeza == GRANDEZA_ENERGIA)

    @property
    def custo_demanda(self) -> float:
        return sum(p.custo for p in self.parcelas if p.grandeza == GRANDEZA_DEMANDA)

    @property
    def custo_te(self) -> float:
        return sum(p.custo for p in self.parcelas if p.componente == COMPONENTE_TE)

    @property
    def custo_tusd(self) -> float:
        return sum(p.custo for p in self.parcelas if p.componente == COMPONENTE_TUSD)

    @property
    def custo_total(self) -> float:
        return sum(p.custo for p in self.parcelas)


@dataclass(frozen=True)
class LinhaFatura:
    """Uma linha da fatura (tarifária ou adicional), como no simulador.

    ``categoria`` ∈ {"TARIFA", "ULTRAPASSAGEM", "REATIVOS", "BANDEIRA",
    "ENCARGO", "OUTROS"}. ``quantidade``/``tarifa``/``custo`` seguem a unidade
    da linha (kW, MWh, kVAr, R$ fixo...).
    """

    descricao: str
    categoria: str
    quantidade: float
    tarifa: float
    custo: float


@dataclass(frozen=True)
class ResultadoFatura:
    """Fatura completa de uma modalidade (linhas + totais)."""

    modalidade: str
    linhas: tuple[LinhaFatura, ...] = ()
    aplicar_tributos: bool = False

    def __post_init__(self) -> None:
        _exigir_texto(self.modalidade, "modalidade")

    @property
    def custo_tarifas(self) -> float:
        return sum(l.custo for l in self.linhas if l.categoria == "TARIFA")

    @property
    def custo_total(self) -> float:
        return sum(l.custo for l in self.linhas)


@dataclass(frozen=True)
class ModalidadeIndisponivel:
    """Modalidade não disponível para o perfil e o motivo (elegibilidade)."""

    modalidade: str
    motivo: str


@dataclass(frozen=True)
class ResultadoComparacao:
    """Comparação Azul × Verde (Grupo A) para um perfil.

    ``disponiveis`` vem ordenado por menor ``custo_total``; ``indisponiveis``
    lista as modalidades fora da elegibilidade (ex.: Verde fora de A3a/A4/AS).
    """

    disponiveis: tuple[ResultadoFatura, ...] = ()
    indisponiveis: tuple[ModalidadeIndisponivel, ...] = ()

    @property
    def melhor(self) -> ResultadoFatura | None:
        """Modalidade disponível de menor custo (primeira do ranking)."""
        return self.disponiveis[0] if self.disponiveis else None


@dataclass(frozen=True)
class ResultadoOtimizacao:
    """Resultado da comparação entre modalidades tarifárias."""

    modalidade_escolhida: str
    ranking: tuple[ResultadoCalculo, ...]
    empate: bool = False
    economia_vs_segunda: float = 0.0


@dataclass(frozen=True)
class ResultadoPI:
    """Resultado do Preço de Indiferença (PI) — ver docs/epi.md.

    O ``pi`` (R$/MWh) é o preço da energia no ACL que iguala o custo de
    energia entre ACR e ACL. Os demais campos são os componentes
    intermediários da fórmula (adaptada de Lemos, 2025), para auditoria e
    rastreabilidade do cálculo.
    """

    pi: float
    e: float
    c_te: float
    c_e_acr: float
    custos_acl: float
    base_acl: float
    aviso: str | None = None
    meses: int = 1


# Alias de compatibilidade: o contrato anterior chamava o resultado de EPI.
ResultadoEPI = ResultadoPI
