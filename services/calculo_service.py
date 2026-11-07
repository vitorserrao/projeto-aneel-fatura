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

- reativos excedentes seguem o art. 304 com as tarifas de referência
  ``VRERE`` (TE do B1, bandeira verde) e ``VRDRE`` (TUSD demanda fora ponta
  da Azul) buscadas no banco; se a tarifa de referência não existir ou for
  ambígua, as linhas de reativos são omitidas e um aviso é devolvido;
- as tarifas são da base escolhida (padrão: ``Tarifa de Aplicação`` — a base
  que chega ao consumidor, regra explícita do Guia ANEEL).

Portanto o resultado é uma ESTIMATIVA LINEAR da fatura, determinística.
"""

from __future__ import annotations

from dataclasses import replace

from core.motor_calculo import (
    _classe_b_por_atividade,
    _subclasse_b_por_atividade,
    _subgrupo_b_por_atividade,
    calcular_fatura,
)
from core.models import (
    GRANDEZA_DEMANDA,
    GRANDEZA_ENERGIA,
    POSTO_FORA_PONTA,
    POSTO_INTERMEDIARIO,
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
        tipo_icms: str = "fora",
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
        resultado, _nao_mapeadas, _avisos = self.calcular_detalhado(
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
        tipo_icms: str = "fora",
        reativos_direto: bool = False,
        tarifa_reativo_energia_r_kvarh: float | None = None,
        tarifa_reativo_demanda_r_kvar: float | None = None,
        arredondar_centavos: bool = False,
        demanda_isenta_icms: bool = False,
        demanda_isenta_icms_kw: float | None = None,
        tributar_reativos: bool = False,
    ) -> ResultadoComparacao:
        """Compara Azul × Verde (Grupo A) e devolve ranking + indisponíveis.

        ``modalidades`` permite fixar a lista a comparar; por padrão usa as
        elegíveis de ``core.motor_calculo.modalidades_elegiveis``. As demais
        modalidades do Grupo A entram em ``indisponiveis`` com o motivo da
        regra de elegibilidade. Tributos são propagados igualmente a todas.

        As flags ``arredondar_centavos``, ``demanda_isenta_icms``,
        ``demanda_isenta_icms_kw`` e ``tributar_reativos`` são repassadas a
        cada fatura: sem elas os totais daqui divergiriam de
        ``POST /calculo/fatura`` para o mesmo perfil (antes eram ignoradas).

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
                    fatura, _, _avisos = self.calcular_detalhado(
                        consumidor, modalidade_real, base_tarifaria,
                        aplicar_tributos=aplicar_tributos,
                        pis=pis,
                        cofins=cofins,
                        icms=icms,
                        tipo_icms=tipo_icms,
                        reativos_direto=reativos_direto,
                        tarifa_reativo_energia_r_kvarh=tarifa_reativo_energia_r_kvarh,
                        tarifa_reativo_demanda_r_kvar=tarifa_reativo_demanda_r_kvar,
                        arredondar_centavos=arredondar_centavos,
                        demanda_isenta_icms=demanda_isenta_icms,
                        demanda_isenta_icms_kw=demanda_isenta_icms_kw,
                        tributar_reativos=tributar_reativos,
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

    def parcelas_vigentes(
        self,
        consumidor: Consumidor,
        modalidade: str,
        base_tarifaria: str = BASE_PADRAO,
    ) -> tuple[list, list, list, bool]:
        """Busca as tarifas vigentes e monta as parcelas (sem calcular a fatura).

        Espelha a etapa de busca/mapeamento de ``calcular_detalhado`` para o
        planejamento anual reutilizar as MESMAS regras (filtros, ambiguidade,
        sazonalidade) sem refazer a consulta para cada candidato de demanda.
        Retorna ``(parcelas, nao_mapeadas, avisos, demanda_unica)``.
        """
        if consumidor.data_referencia is None:
            raise ValueError(
                "data_referencia do consumidor é obrigatória para calcular a fatura"
            )

        m = modalidade.strip().title()
        caminho_b = m in ("Optante B", "Convencional Monômia", "Branca")
        classe_filtro = _filtro_b_ou_none(consumidor.classe) if caminho_b else None
        subclasse_filtro = (
            _filtro_b_ou_none(consumidor.subclasse) if caminho_b else None
        )
        if m == "Optante B":
            subgrupo_busca = _subgrupo_b_por_atividade(consumidor.atividade)
            modalidade_busca = "Convencional"
            if classe_filtro is None:
                classe_filtro = _classe_b_por_atividade(consumidor.atividade)
                subclasse_filtro = _subclasse_b_por_atividade(consumidor.atividade)
        elif m == "Convencional Monômia":
            subgrupo_busca = consumidor.subgrupo
            modalidade_busca = "Convencional"
        elif m == "Branca":
            subgrupo_busca = consumidor.subgrupo
            modalidade_busca = "Branca"
        else:
            subgrupo_busca = consumidor.subgrupo
            modalidade_busca = modalidade

        tarifas = self._repo.buscar_tarifas(
            data=consumidor.data_referencia,
            sig_agente=consumidor.distribuidora,
            subgrupo=subgrupo_busca,
            modalidade=modalidade_busca,
            detalhe=consumidor.detalhe or None,
            base_tarifaria=base_tarifaria,
            classe=classe_filtro,
            subclasse=subclasse_filtro,
        )

        avisos: list[tuple[str, str]] = []
        chaves_ambiguas: set[tuple] = set()
        chaves_processadas: set[tuple] = set()
        if caminho_b:
            valor_por_chave: dict[tuple, object] = {}
            for t in tarifas:
                grandeza = _grandeza_de(t)
                if grandeza is None:
                    continue
                chave = (t.componente, grandeza, t.posto.strip().casefold())
                if chave in valor_por_chave:
                    if valor_por_chave[chave] != t.valor:
                        chaves_ambiguas.add(chave)
                else:
                    valor_por_chave[chave] = t.valor
            for componente, grandeza, posto in sorted(chaves_ambiguas):
                avisos.append(
                    (
                        "tarifa_ambigua",
                        f"Tarifa ambígua ({componente} {grandeza} {posto}): "
                        "múltiplos valores vigentes simultâneos (P6) — "
                        "parcelas omitidas da fatura. Informe classe/subclasse "
                        "para desambiguar.",
                    )
                )

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
            chave = (t.componente, grandeza, t.posto.strip().casefold())
            if chave in chaves_ambiguas or chave in chaves_processadas:
                continue
            chaves_processadas.add(chave)
            if m in ("Optante B", "Convencional Monômia"):
                if grandeza == GRANDEZA_DEMANDA:
                    continue
                if t.posto.strip().casefold() == "não se aplica":
                    parcelas.append(
                        tarifa_vigente_para_parcela(
                            t, grandeza=grandeza, posto=POSTO_PONTA
                        )
                    )
                    parcelas.append(
                        tarifa_vigente_para_parcela(
                            t, grandeza=grandeza, posto=POSTO_FORA_PONTA
                        )
                    )
                    continue
            posto = _posto_de(t)
            if posto is None and (
                t.posto.strip().casefold() == "não se aplica"
                and grandeza == GRANDEZA_DEMANDA
                and modalidade.strip().title() == "Verde"
            ):
                posto = POSTO_PONTA
            if posto is None:
                posto = _posto_sazonal_de(t, consumidor.data_referencia)
                if posto is None:
                    if "seca" in t.posto.casefold() or "úmida" in t.posto.casefold():
                        continue
                    nao_mapeadas.append(t)
                    continue
            if (t.componente, grandeza) in chaves_sazonais and not any(
                kw in t.posto.casefold() for kw in ("seca", "úmida")
            ):
                continue
            parcelas.append(
                tarifa_vigente_para_parcela(t, grandeza=grandeza, posto=posto)
            )

        demanda_unica = m == "Verde"
        return parcelas, nao_mapeadas, avisos, demanda_unica

    def calcular_detalhado(
        self,
        consumidor: Consumidor,
        modalidade: str,
        base_tarifaria: str = BASE_PADRAO,
        aplicar_tributos: bool = False,
        pis: float = 0.0,
        cofins: float = 0.0,
        icms: float = 0.0,
        tipo_icms: str = "fora",
        reativos_direto: bool = False,
        tarifa_reativo_energia_r_kvarh: float | None = None,
        tarifa_reativo_demanda_r_kvar: float | None = None,
        arredondar_centavos: bool = False,
        demanda_isenta_icms: bool = False,
        demanda_isenta_icms_kw: float | None = None,
        tributar_reativos: bool = False,
    ) -> tuple[ResultadoFatura, list[TarifaVigente], list[tuple[str, str]]]:
        """Igual a ``calcular``, devolvendo também as tarifas não mapeadas.

        ``aplicar_tributos``/``pis``/``cofins``/``icms``/``tipo_icms`` são
        propagados ao motor (fórmula aditiva "dentro" ou multiplicativa
        "fora").

        Observação de filtro: a busca filtra por distribuidora, subgrupo,
        modalidade e base. Para o Grupo A a classe é "Não se aplica" e o
        filtro é inócuo; para o **Grupo B** (Optante B, Convencional Monômia
        e Branca) a **classe/subclasse** do perfil filtram a tarifa (ex.: B1
        Residencial × Residencial Baixa Renda). Sem classe informada e com
        valores ambíguos vigentes na mesma chave, as parcelas são omitidas
        com aviso ``tarifa_ambigua`` (premissa A5/P6) — nunca somadas.

        Returns:
            Tupla ``(resultado, nao_mapeadas, avisos)`` — ``nao_mapeadas`` são
            as tarifas vigentes cujo posto o core ainda não suporta (ex.:
            Intermediário); ficam explicitamente fora da fatura até a regra
            de posto ser fechada (docs/premissas.md, P5). ``avisos`` são pares
            ``(tipo, mensagem)`` (ex.: tarifa de referência de reativos
            indisponível/ambígua → reativos omitidos).
        """
        if consumidor.data_referencia is None:
            raise ValueError(
                "data_referencia do consumidor é obrigatória para calcular a fatura"
            )

        m = modalidade.strip().title()
        caminho_b = m in ("Optante B", "Convencional Monômia", "Branca")
        classe_filtro = _filtro_b_ou_none(consumidor.classe) if caminho_b else None
        subclasse_filtro = (
            _filtro_b_ou_none(consumidor.subclasse) if caminho_b else None
        )
        if m == "Optante B":
            # Grupo A faturado como Grupo B (art. 292): usa a tarifa
            # Convencional do subgrupo B derivado da atividade econômica.
            subgrupo_busca = _subgrupo_b_por_atividade(consumidor.atividade)
            modalidade_busca = "Convencional"
            if classe_filtro is None:
                # Decisão do usuário: o optante NÃO precisa informar a
                # categoria — classe e subclasse são derivadas da atividade
                # (residencial → Residencial/Residencial; rural →
                # Rural/Não se aplica). O dataset publica B1/B2 em várias
                # subclasses com valores distintos, então a subclasse também
                # é derivada. Atividades ambíguas (B3) caem na guarda de
                # ambiguidade (A5) se houver valores distintos.
                classe_filtro = _classe_b_por_atividade(consumidor.atividade)
                subclasse_filtro = _subclasse_b_por_atividade(consumidor.atividade)
        elif m == "Convencional Monômia":
            subgrupo_busca = consumidor.subgrupo
            modalidade_busca = "Convencional"
        elif m == "Branca":
            subgrupo_busca = consumidor.subgrupo
            modalidade_busca = "Branca"
        else:
            subgrupo_busca = consumidor.subgrupo
            modalidade_busca = modalidade

        tarifas = self._repo.buscar_tarifas(
            data=consumidor.data_referencia,
            sig_agente=consumidor.distribuidora,
            subgrupo=subgrupo_busca,
            modalidade=modalidade_busca,
            # Filtro por detalhe (padrão 'Não se aplica' no schema): evita somar
            # linhas sobrepostas do mesmo contexto (ex.: APE vs Não se aplica),
            # que dobravam a parcela (pendência P6).
            detalhe=consumidor.detalhe or None,
            base_tarifaria=base_tarifaria,
            # No Grupo B a classe/subclasse discriminam a tarifa (ex.: B1
            # Residencial × Residencial Baixa Renda); no Grupo A o dataset
            # grafa "Não se aplica" e o filtro é inócuo (mantido sem filtro).
            classe=classe_filtro,
            subclasse=subclasse_filtro,
        )

        # Guarda de ambiguidade do caminho B (premissa A5, pendência P6):
        # quando a MESMA chave (componente+grandeza+posto) tem mais de um valor
        # vigente distinto (ex.: B1 Residencial × Baixa Renda sem classe
        # informada), as parcelas são OMITIDAS com aviso — nunca somadas
        # silenciosamente. Repetições com o MESMO valor são deduplicadas.
        avisos: list[tuple[str, str]] = []
        chaves_ambiguas: set[tuple] = set()
        chaves_processadas: set[tuple] = set()
        if caminho_b:
            valor_por_chave: dict[tuple, object] = {}
            for t in tarifas:
                grandeza = _grandeza_de(t)
                if grandeza is None:
                    continue
                chave = (t.componente, grandeza, t.posto.strip().casefold())
                if chave in valor_por_chave:
                    if valor_por_chave[chave] != t.valor:
                        chaves_ambiguas.add(chave)
                else:
                    valor_por_chave[chave] = t.valor
            for componente, grandeza, posto in sorted(chaves_ambiguas):
                avisos.append(
                    (
                        "tarifa_ambigua",
                        f"Tarifa ambígua ({componente} {grandeza} {posto}): "
                        "múltiplos valores vigentes simultâneos (P6) — "
                        "parcelas omitidas da fatura. Informe classe/subclasse "
                        "para desambiguar.",
                    )
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
            chave = (t.componente, grandeza, t.posto.strip().casefold())
            if chave in chaves_ambiguas or chave in chaves_processadas:
                # Ambíguo (omitido com aviso — A5) ou repetição do mesmo valor.
                continue
            chaves_processadas.add(chave)
            if m in ("Optante B", "Convencional Monômia"):
                if grandeza == GRANDEZA_DEMANDA:
                    # Monômia (Grupo B) não fatura demanda.
                    continue
                if t.posto.strip().casefold() == "não se aplica":
                    # Tarifa única do B aplicada sobre o consumo total:
                    # uma parcela PONTA e uma FORA PONTA com o mesmo valor.
                    parcelas.append(
                        tarifa_vigente_para_parcela(
                            t, grandeza=grandeza, posto=POSTO_PONTA
                        )
                    )
                    parcelas.append(
                        tarifa_vigente_para_parcela(
                            t, grandeza=grandeza, posto=POSTO_FORA_PONTA
                        )
                    )
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
        demanda_unica = m == "Verde"

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

        # Custo de disponibilidade do Grupo B (REN 1.000/2021, arts. 290 e
        # 291): se o consumo for menor que o mínimo da ligação (30/50/100
        # kWh), o mínimo é faturado proporcionalmente aos postos faturados.
        # Vale também para o Optante B, faturado como Grupo B (art. 292).
        if m in ("Optante B", "Convencional Monômia", "Branca"):
            minimo = _consumo_minimo_kwh(consumidor_efetivo.tipo_ligacao)
            # Postos efetivamente faturados: a monômia (Optante B e
            # Convencional) fatura ponta + fora ponta; a Branca também fatura
            # o intermediário.
            inclui_intermediario = m == "Branca"
            total = (
                consumidor_efetivo.consumo_ponta_kwh
                + consumidor_efetivo.consumo_fora_ponta_kwh
                + (
                    consumidor_efetivo.consumo_intermediario_kwh
                    if inclui_intermediario
                    else 0.0
                )
            )
            if 0 < total < minimo:
                fator = minimo / total
                consumidor_efetivo = replace(
                    consumidor_efetivo,
                    consumo_ponta_kwh=consumidor_efetivo.consumo_ponta_kwh * fator,
                    consumo_fora_ponta_kwh=consumidor_efetivo.consumo_fora_ponta_kwh * fator,
                    consumo_intermediario_kwh=(
                        consumidor_efetivo.consumo_intermediario_kwh * fator
                        if inclui_intermediario
                        else consumidor_efetivo.consumo_intermediario_kwh
                    ),
                )

        # Reativos excedentes. Modo direto (faturas antigas): usa as tarifas
        # informadas (R$/kVArh e R$/kVAr) sem buscar referências. Modo art. 304:
        # busca VRERE/VRDRE no banco; se a referência faltar ou for ambígua, as
        # linhas são omitidas e um aviso é devolvido (premissa A5).
        vrere_r_mwh = None
        vrdre_r_kw = None
        if reativos_direto and _tem_reativos(consumidor_efetivo):
            # Faturas antigas cobram o excedente direto com tarifas de
            # referência do art. 304: energia = VRERE/1000 (R$/kVArh) e
            # demanda = VRDRE (R$/kVAr). Se o chamador informar tarifa
            # manual, ela tem prioridade (override).
            if tarifa_reativo_energia_r_kvarh is None:
                vrere, aviso = self._buscar_vrere(
                    consumidor_efetivo, base_tarifaria
                )
                if vrere is not None:
                    tarifa_reativo_energia_r_kvarh = vrere / 1000.0
                elif aviso:
                    avisos.append(aviso)
            if tarifa_reativo_demanda_r_kvar is None:
                vrdre, aviso = self._buscar_vrdre(
                    consumidor_efetivo, base_tarifaria
                )
                if vrdre is not None:
                    tarifa_reativo_demanda_r_kvar = vrdre
                elif aviso:
                    avisos.append(aviso)
            if (
                tarifa_reativo_energia_r_kvarh is None
                and tarifa_reativo_demanda_r_kvar is None
            ):
                avisos.append(
                    (
                        "reativos_direto_sem_tarifa",
                        "Modo reativos direto sem tarifa (R$/kVArh ou R$/kVAr) "
                        "informada e sem referência no banco — linhas de "
                        "reativos omitidas.",
                    )
                )
        elif _tem_reativos(consumidor_efetivo):
            vrere_r_mwh, aviso_vrere = self._buscar_vrere(
                consumidor_efetivo, base_tarifaria
            )
            if aviso_vrere:
                avisos.append(aviso_vrere)
            vrdre_r_kw, aviso_vrdre = self._buscar_vrdre(
                consumidor_efetivo, base_tarifaria
            )
            if aviso_vrdre:
                avisos.append(aviso_vrdre)

        return (
            calcular_fatura(
                consumidor_efetivo, modalidade, parcelas,
                demanda_unica=demanda_unica,
                aplicar_tributos=aplicar_tributos,
                pis=pis,
                cofins=cofins,
                icms=icms,
                tipo_icms=tipo_icms,
                vrere_r_mwh=vrere_r_mwh,
                vrdre_r_kw=vrdre_r_kw,
                reativos_direto=reativos_direto,
                tarifa_reativo_energia_r_kvarh=tarifa_reativo_energia_r_kvarh,
                tarifa_reativo_demanda_r_kvar=tarifa_reativo_demanda_r_kvar,
                arredondar_centavos=arredondar_centavos,
                demanda_isenta_icms=demanda_isenta_icms,
                demanda_isenta_icms_kw=demanda_isenta_icms_kw,
                tributar_reativos=tributar_reativos,
            ),
            nao_mapeadas,
            avisos,
        )

    # Art. 304, §3º: quando VRDRE for nulo, usar o nível de tensão
    # imediatamente inferior. Ordem decrescente de tensão dos subgrupos.
    _SUBGRUPOS_POR_TENSAO = ("A1", "A2", "A3", "A3a", "A4", "AS")

    def _buscar_vrere(
        self, consumidor: Consumidor, base_tarifaria: str
    ) -> tuple[float | None, tuple[str, str] | None]:
        """VRERE do art. 304: TE do subgrupo B1 (bandeira verde), em R$/MWh.

        Filtra classe/subclasse "Residencial"/"Residencial" (como a planilha)
        para evitar a ambiguidade B1 Baixa Renda × Residencial (P6).
        """
        tarifas = self._repo.buscar_tarifas(
            data=consumidor.data_referencia,
            sig_agente=consumidor.distribuidora,
            subgrupo="B1",
            modalidade="Convencional",
            componente="TE",
            classe="Residencial",
            subclasse="Residencial",
            detalhe=consumidor.detalhe or None,
            base_tarifaria=base_tarifaria,
        )
        if not tarifas:
            return None, (
                "reativos_sem_tarifa_referencia",
                "VRERE (TE B1 bandeira verde) indisponível no banco — "
                "reativos excedentes omitidos da fatura.",
            )
        if len(tarifas) > 1:
            return None, (
                "reativos_tarifa_referencia_ambigua",
                "VRERE (TE B1) com múltiplas tarifas vigentes (P6) — "
                "reativos excedentes omitidos da fatura.",
            )
        return _valor_em_r_mwh(tarifas[0]), None

    def _buscar_vrdre(
        self, consumidor: Consumidor, base_tarifaria: str
    ) -> tuple[float | None, tuple[str, str] | None]:
        """VRDRE do art. 304: TUSD demanda fora ponta da Azul, em R$/kW.

        Se o subgrupo do consumidor não tiver a tarifa publicada, aplica o
        §3º do art. 304: usa o nível de tensão imediatamente inferior.
        """
        sub = consumidor.subgrupo.strip().upper()
        ordem = self._SUBGRUPOS_POR_TENSAO
        try:
            idx = ordem.index(sub)
        except ValueError:
            idx = None
        candidatos = ordem[idx:] if idx is not None else (sub,)
        for sg in candidatos:
            tarifas = self._repo.buscar_tarifas(
                data=consumidor.data_referencia,
                sig_agente=consumidor.distribuidora,
                subgrupo=sg,
                modalidade="Azul",
                componente="TUSD",
                unidade="kW",
                posto="Fora ponta",
                detalhe=consumidor.detalhe or None,
                base_tarifaria=base_tarifaria,
            )
            if len(tarifas) == 1:
                return float(tarifas[0].valor), None
            if len(tarifas) > 1:
                return None, (
                    "reativos_tarifa_referencia_ambigua",
                    f"VRDRE (TUSD demanda fora ponta da Azul, subgrupo {sg}) "
                    "com múltiplas tarifas vigentes (P6) — reativos "
                    "excedentes omitidos da fatura.",
                )
        return None, (
            "reativos_sem_tarifa_referencia",
            "VRDRE (TUSD demanda fora ponta da Azul) indisponível no banco "
            "para o subgrupo e níveis inferiores — reativos excedentes "
            "omitidos da fatura.",
        )


def _filtro_b_ou_none(valor: str | None) -> str | None:
    """Valor de classe/subclasse para o filtro da tarifa B, ou None.

    "Não se aplica" (com ou sem acento) e vazio significam "sem informação":
    nesse caso não se filtra — a guarda de ambiguidade (A5) cuida do restante.
    """
    v = (valor or "").strip()
    if v.casefold() in ("", "não se aplica", "nao se aplica"):
        return None
    return v


def _consumo_minimo_kwh(tipo_ligacao: str) -> float:
    """Consumo mínimo do custo de disponibilidade do Grupo B (kWh).

    Art. 291: 30 kWh (monofásico/bifásico a 2 condutores), 50 kWh (bifásico
    a 3 condutores), 100 kWh (trifásico). Sem o nº de condutores no perfil,
    aproxima bifásico → 50 kWh (pendência registrada em docs/regras_tarifarias.md).
    """
    t = (tipo_ligacao or "").strip().lower()
    if "monof" in t:
        return 30.0
    if "bif" in t:
        return 50.0
    return 100.0  # trifásico (padrão)


def _com_bandeira(consumidor: Consumidor, valor_r_kwh: float) -> Consumidor:
    """Cópia do consumidor com o adicional de bandeira definido."""
    from dataclasses import replace

    return replace(consumidor, bandeira_adicional_r_kwh=valor_r_kwh)


def _tem_reativos(consumidor: Consumidor) -> bool:
    """True quando o perfil informa qualquer grandeza reativa."""
    return (
        consumidor.reativo_energia_ponta_kvArh
        + consumidor.reativo_energia_fora_ponta_kvArh
        + consumidor.reativo_demanda_ponta_kvAr
        + consumidor.reativo_demanda_fora_ponta_kvAr
        + consumidor.reativo_energia_capacitiva_kvArh
        + consumidor.reativo_demanda_capacitiva_kvAr
    ) > 0


def _valor_em_r_mwh(tarifa: TarifaVigente) -> float:
    """Valor em R$/MWh (converte R$/kWh quando necessário)."""
    valor = float(tarifa.valor)
    if tarifa.unidade.strip().upper() == "KWH":
        return valor * 1000.0
    return valor


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
    if p == "intermediário":
        return POSTO_INTERMEDIARIO
    return None  # seca / úmida / Não se aplica: pendente (P5)


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
