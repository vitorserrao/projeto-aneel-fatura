"""Serviço de cálculo ACR (orquestração repo → adapter → core).

Este módulo implementa o caso de uso "calcular o custo no ACR de um perfil
para uma modalidade" como uma ORQUESTRAÇÃO das peças já existentes:

    consumidor (perfil)
        → [TarifaRepository] tarifas vigentes (filtros do perfil + data)
        → [adapter] ParcelaTarifaria (grandeza/posto mapeados do próprio dado)
        → [core.motor_calculo.calcular_custo_acr] ResultadoCalculo (fatura)

Regras usadas aqui (fonte: base de conhecimento PRORET 7.1):

- ``grandeza`` é derivada da unidade observada no dado:
  ``MWh``/``kWh`` → ENERGIA; ``kW`` → DEMANDA.
  (PRORET 7.1, pág. 2: demanda em R$/kW e energia em R$/MWh — regra explícita.)
- ``posto`` é derivado do posto observado no dado:
  ``Ponta`` → PONTA; ``Fora ponta`` → FORA PONTA.
  Postos que o core ainda não suporta (ex.: ``Intermediário``, ``seca/úmida``,
  ``Não se aplica``) NÃO são inventados: são devolvidos como "não mapeados"
  em ``calcular_detalhado`` para decisão futura (P5).

O que esta fatura NÃO inclui (limitações explícitas, sem silêncio):

- reativos usam proxy de tarifa de energia TUSD (refinamento pendente);
- as tarifas são da base escolhida (padrão: ``Tarifa de Aplicação`` — a base
  que chega ao consumidor, regra explícita do Guia ANEEL).

Portanto o resultado é uma ESTIMATIVA LINEAR da fatura, determinística.
"""

from __future__ import annotations

from core.motor_calculo import calcular_fatura
from core.models import (
    GRANDEZA_DEMANDA,
    GRANDEZA_ENERGIA,
    POSTO_FORA_PONTA,
    POSTO_PONTA,
    Consumidor,
    ModalidadeIndisponivel,
    ResultadoComparacao,
    ResultadoFatura,
)
from infra.repositories.adapter import tarifa_vigente_para_parcela
from infra.repositories.tarifa_repository import TarifaRepository, TarifaVigente

# Base padrão da fatura: a que efetivamente chega ao consumidor
# (regra explícita — Guia ANEEL "Base de Dados e Análise das Tarifas", pág. 2).
BASE_PADRAO = "Tarifa de Aplicação"


class CalculoService:
    """Caso de uso: calcular custo ACR de um perfil para uma modalidade."""

    def __init__(self, tarifa_repository: TarifaRepository):
        self._repo = tarifa_repository

    def calcular(
        self,
        consumidor: Consumidor,
        modalidade: str,
        base_tarifaria: str = BASE_PADRAO,
        aplicar_tributos: bool = False,
        pis: float = 0.0,
        cofins: float = 0.0,
        icms: float = 0.0,
        tipo_icms: str = "dentro",
    ) -> ResultadoFatura:
        """Calcula a fatura completa ACR do perfil na ``modalidade``.

        Busca no repositório as tarifas vigentes (filtradas por ``detalhe``),
        converte em parcelas e monta a fatura (linhas tarifárias + ultrapassagem
        + bandeira + CIP/COSIP + outros + reativos quando fp < 0,92).

        ``aplicar_tributos``/``pis``/``cofins``/``icms``: tributos opcionais
        (fórmula oficial aditiva). Base líquida por padrão.

        Raises:
            ValueError: perfil sem data de referência, ou nenhuma tarifa
                aplicável encontrada/vigente.
        """
        resultado, _nao_mapeadas = self.calcular_detalhado(
            consumidor, modalidade, base_tarifaria,
            aplicar_tributos=aplicar_tributos, pis=pis, cofins=cofins,
            icms=icms, tipo_icms=tipo_icms,
        )
        return resultado

    def comparar_modalidades(
        self,
        consumidor: Consumidor,
        base_tarifaria: str = BASE_PADRAO,
        modalidades: list[str] | None = None,
        aplicar_tributos: bool = False,
        pis: float = 0.0,
        cofins: float = 0.0,
        icms: float = 0.0,
        tipo_icms: str = "dentro",
    ) -> ResultadoComparacao:
        """Compara Azul × Verde (Grupo A) e devolve ranking + indisponíveis.

        ``modalidades`` permite fixar a lista a comparar; por padrão usa as
        elegíveis de ``core.motor_calculo.modalidades_elegiveis``. As demais
        modalidades do Grupo A entram em ``indisponiveis`` com o motivo da
        regra de elegibilidade. Tributos são propagados igualmente a todas.

        Retorna ``ResultadoComparacao`` com ``disponiveis`` ordenadas por
        menor ``custo_total`` e ``indisponiveis`` com ``(modalidade, motivo)``.
        """
        from core.motor_calculo import (
            MODALIDADES_GRUPO_A,
            modalidades_elegiveis,
            motivo_indisponibilidade,
        )

        alvos = modalidades if modalidades is not None else modalidades_elegiveis(consumidor)
        alvos_norm = [m.strip().upper() for m in alvos]

        disponiveis: list[ResultadoFatura] = []
        indisponiveis: list[ModalidadeIndisponivel] = []

        for modalidade in MODALIDADES_GRUPO_A:
            if modalidade in alvos_norm:
                # O dataset grafa "Azul", "Verde" (inicial maiúscula).
                modalidade_real = modalidade.strip().title()
                try:
                    fatura, _ = self.calcular_detalhado(
                        consumidor, modalidade_real, base_tarifaria,
                        aplicar_tributos=aplicar_tributos,
                        pis=pis,
                        cofins=cofins,
                        icms=icms,
                        tipo_icms=tipo_icms,
                    )
                except ValueError:
                    # Sem tarifa vigente para a modalidade nesta distribuidora.
                    indisponiveis.append(
                        ModalidadeIndisponivel(
                            modalidade=modalidade_real,
                            motivo="Sem tarifa vigente para a modalidade nesta distribuidora/data",
                        )
                    )
                    continue
                disponiveis.append(fatura)
            else:
                motivo = motivo_indisponibilidade(modalidade, consumidor)
                indisponiveis.append(
                    ModalidadeIndisponivel(
                        modalidade=modalidade.strip().title(),
                        motivo=motivo or "Fora da elegibilidade do Grupo A",
                    )
                )

        disponiveis.sort(key=lambda r: r.custo_total)
        return ResultadoComparacao(
            disponiveis=tuple(disponiveis),
            indisponiveis=tuple(indisponiveis),
        )

    def calcular_detalhado(
        self,
        consumidor: Consumidor,
        modalidade: str,
        base_tarifaria: str = BASE_PADRAO,
        aplicar_tributos: bool = False,
        pis: float = 0.0,
        cofins: float = 0.0,
        icms: float = 0.0,
        tipo_icms: str = "dentro",
    ) -> tuple[ResultadoFatura, list[TarifaVigente]]:
        """Igual a ``calcular``, devolvendo também as tarifas não mapeadas.

        ``aplicar_tributos``/``pis``/``cofins``/``icms``/``tipo_icms`` são
        propagados ao motor (fórmula aditiva "dentro" ou multiplicativa
        "fora").

        Observação de filtro: a busca filtra por distribuidora, subgrupo,
        modalidade e base, mas **não** por classe/subclasse — para o Grupo A
        (foco do MVP) a classe é "Não se aplica" e a distinção de classe não
        altera o subconjunto de tarifas; o filtro por classe/subclasse pode
        ser reintroduzido quando o domínio do Grupo B for tratado.

        Returns:
            Tupla ``(resultado, nao_mapeadas)`` — ``nao_mapeadas`` são as
            tarifas vigentes cujo posto o core ainda não suporta (ex.:
            Intermediário); ficam explicitamente fora da fatura até a regra
            de posto ser fechada (docs/premissas.md, P5).
        """
        if consumidor.data_referencia is None:
            raise ValueError(
                "data_referencia do consumidor é obrigatória para calcular a fatura"
            )

        tarifas = self._repo.buscar_tarifas(
            data=consumidor.data_referencia,
            sig_agente=consumidor.distribuidora,
            subgrupo=consumidor.subgrupo,
            modalidade=modalidade,
            # Filtro por detalhe (padrão 'Não se aplica' no schema): evita somar
            # linhas sobrepostas do mesmo contexto (ex.: APE vs Não se aplica),
            # que dobravam a parcela (pendência P6).
            detalhe=consumidor.detalhe or None,
            base_tarifaria=base_tarifaria,
        )

        # Detecção de vigência horo-sazonal POR CHAVE (componente+grandeza):
        # quando a MESMA chave aparece em posto simples E sazonal, o formato
        # oficial da época era horo-sazonal — o posto simples duplica o valor
        # (sobreposição P6) e deve ser ignorado.
        chaves_sazonais = {
            (t.componente, _grandeza_de(t))
            for t in tarifas
            if "seca" in t.posto.casefold() or "úmida" in t.posto.casefold()
        }

        parcelas = []
        nao_mapeadas = []
        for t in tarifas:
            grandeza = _grandeza_de(t)
            if grandeza is None:
                nao_mapeadas.append(t)
                continue
            posto = _posto_de(t)
            if posto is None and (
                t.posto.strip().casefold() == "não se aplica"
                and grandeza == GRANDEZA_DEMANDA
                and modalidade.strip().title() == "Verde"
            ):
                # Demanda ÚNICA da Verde: posto "Não se aplica" no dataset.
                # A quantidade real é máx(medida_única, contratada_única) —
                # aplicado no motor via demanda_unica=True; usa-se PONTA
                # apenas como posto normalizado da ParcelaTarifaria.
                posto = POSTO_PONTA
            if posto is None:
                # Posto horo-sazonal: mapeia pelo mês da data de referência.
                posto = _posto_sazonal_de(t, consumidor.data_referencia)
                if posto is None:
                    if "seca" in t.posto.casefold() or "úmida" in t.posto.casefold():
                        # Sazonal do OUTRO período (ex.: úmida em junho):
                        # inaplicável na data — descartado.
                        continue
                    nao_mapeadas.append(t)
                    continue
            if (t.componente, grandeza) in chaves_sazonais and not any(
                kw in t.posto.casefold() for kw in ("seca", "úmida")
            ):
                # Posto simples de uma chave que possui versão sazonal: o valor
                # já entra pelo posto sazonal do período — evita duplicar.
                continue
            parcelas.append(
                tarifa_vigente_para_parcela(t, grandeza=grandeza, posto=posto)
            )

        # Demanda ÚNICA da Verde (máx(medida, contratada) nos campos únicos)
        # — sinalizada ao motor via demanda_unica=True.
        demanda_unica = modalidade.strip().title() == "Verde"

        # Bandeira tarifária por competência: quando o consumidor não informou
        # adicional manual (0), busca no banco; competência < jan/2015 → sem
        # bandeira (adicional 0) — espelha o IFERROR(...,0) da planilha.
        bandeira_r_kwh = consumidor.bandeira_adicional_r_kwh
        if bandeira_r_kwh == 0.0:
            bandeira = self._repo.buscar_bandeira(consumidor.data_referencia)
            if bandeira is not None:
                bandeira_r_kwh = bandeira[1]

        consumidor_efetivo = consumidor
        if bandeira_r_kwh != consumidor.bandeira_adicional_r_kwh:
            consumidor_efetivo = _com_bandeira(consumidor, bandeira_r_kwh)

        return (
            calcular_fatura(
                consumidor_efetivo, modalidade, parcelas,
                demanda_unica=demanda_unica,
                aplicar_tributos=aplicar_tributos,
                pis=pis,
                cofins=cofins,
                icms=icms,
                tipo_icms=tipo_icms,
            ),
            nao_mapeadas,
        )


def _com_bandeira(consumidor: Consumidor, valor_r_kwh: float) -> Consumidor:
    """Cópia do consumidor com o adicional de bandeira definido."""
    from dataclasses import replace

    return replace(consumidor, bandeira_adicional_r_kwh=valor_r_kwh)


def _grandeza_de(tarifa: TarifaVigente) -> str | None:
    """Deriva a grandeza da unidade observada (regra explícita PRORET 7.1)."""
    u = tarifa.unidade.strip().upper()
    if u in ("MWH", "KWH"):
        return GRANDEZA_ENERGIA
    if u == "KW":
        return GRANDEZA_DEMANDA
    return None  # unidade não observada: não inventar


def _posto_de(tarifa: TarifaVigente) -> str | None:
    """Deriva o posto normalizado do posto observado no dado.

    Apenas os postos literais do contrato são mapeados; variações legadas
    (``seca``/``úmida`` — metodologia antiga) e ``Intermediário`` permanecem
    não mapeadas até a regra ser fechada (P5), pois possuem valores próprios
    e não podem ser dobrados em Ponta/Fora ponta sem validação.
    """
    p = tarifa.posto.strip().casefold()
    if p == "ponta":
        return POSTO_PONTA
    if p in ("fora ponta", "fora de ponta"):
        return POSTO_FORA_PONTA
    return None  # Intermediário / seca / úmida / Não se aplica: pendente (P5)


# ---------------------------------------------------------------------------
# Horo-sazonal (seca/úmida) — pendência P5 resolvida
# ---------------------------------------------------------------------------
# Antes da REN 1.000/2021 a tarifa de energia do Grupo A era horo-sazonal:
# Ponta/Fora ponta × Seco(maio–nov)/Úmido(dez–abr). O dataset grafa postos
# "Ponta seca", "Ponta úmida", "Fora ponta seca", "Fora ponta úmida".
# Mapeamos para PONTA/FORA PONTA usando o MÊS da data de referência,
# colapsando a sazonalidade anual (regra registrada em
# conhecimento/regras/horario_sazonal_seca_umida.md).

_MESES_SECO = {5, 6, 7, 8, 9, 10, 11}  # maio a novembro
_MESES_UMIDO = {12, 1, 2, 3, 4}  # dezembro a abril


def _periodo_sazonal(data_referencia) -> str:
    """Período sazonal oficial do mês: "seca" ou "úmida"."""
    if data_referencia.month in _MESES_SECO:
        return "seca"
    if data_referencia.month in _MESES_UMIDO:
        return "úmida"
    raise ValueError(f"mês inesperado: {data_referencia.month}")


def _posto_sazonal_de(tarifa: TarifaVigente, data_referencia) -> str | None:
    """Mapeia posto horo-sazonal para PONTA/FORA PONTA no período correto.

    Retorna None quando o posto é sazonal mas NÃO corresponde ao período da
    data (ex.: "Ponta úmida" em junho) — nesse caso a tarifa é descartada como
    inaplicável, mas não é "não mapeada" (o posto existe, só não vale na data).
    """
    p = tarifa.posto.strip().casefold()
    if "seca" not in p and "úmida" not in p:
        return None
    periodo = _periodo_sazonal(data_referencia)
    if periodo not in p:
        return None  # sazonal do outro período: inaplicável na data
    if p.startswith("ponta"):
        return POSTO_PONTA
    if p.startswith("fora"):
        return POSTO_FORA_PONTA
    return None
