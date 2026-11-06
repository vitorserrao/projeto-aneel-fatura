"""Serviço de planejamento anual de modalidades (orquestração repo → core).

Integra o ``core.planejamento`` ao motor de faturamento COMPLETO: a função de
custo injetada no otimizador é a fatura mensal real (motor com tributos), não
apenas a parcela de demanda. As tarifas são buscadas **em cada mês** do
histórico (a data de referência de cada mês seleciona a vigência correta,
tratando reajustes dentro do período).

O cenário "contrato atual" usa as demandas contratadas informadas; o cenário
"demanda otimizada" usa a DC* encontrada pelo otimizador. A elegibilidade do
Optante B é a já existente (``core.motor_calculo.modalidades_elegiveis``).
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from typing import Sequence

from core.motor_calculo import (
    calcular_fatura,
    modalidades_elegiveis,
)
from core.models import Consumidor
from core.planejamento import (
    AVISO_DEMANDA_OTIMA_REFERENCIA,
    DC_MINIMO_GRUPO_A,
    MedicaoMensal,
    CustoDemandaMensal,
    ResultadoContrato,
    ResultadoEquilibrio,
    ResultadoModalidadePlanejamento,
    ResultadoPlanejamento,
    comparar_planejamento,
    custo_demanda_mensal,
    demanda_ponta_equilibrio,
    montar_demanda,
    montar_demandas,
    otimizar_contrato,
)
from services.calculo_service import BASE_PADRAO, CalculoService
from services.epi_service import EPIService


def _consumo_obrigatorio(mes: dict, campo: str) -> float:
    """Lê o consumo do mês sem zero implícito (dado faltante é erro)."""
    valor = mes.get(campo)
    if valor is None:
        ref = mes.get("data_referencia", "?")
        raise ValueError(f"mês {ref}: falta consumo {campo}")
    return float(valor)


class PlanejamentoService:
    """Caso de uso: comparar modalidades em 12 meses (contrato × otimizado)."""

    def __init__(self, calculo_service: CalculoService, epi_service: EPIService):
        self._calculo = calculo_service
        self._epi = epi_service

    def comparar(
        self,
        perfil_base: Consumidor,
        meses: Sequence[dict],
        *,
        pis: float,
        cofins: float,
        icms: float,
        tipo_icms: str = "fora",
        demanda_isenta_icms: bool = True,
        tributar_reativos: bool = False,
        modalidade_atual: str = "Verde",
        dc_atual_verde: float | None = None,
        dc_atual_azul_ponta: float | None = None,
        dc_atual_azul_fora: float | None = None,
        k: float = 0.03,
        encargos: float = 0.0,
        opex_mensal: float = 0.0,
        capex: float = 0.0,
        horizonte_meses: int = 60,
    ) -> tuple[ResultadoPlanejamento, dict[str, float | None]]:
        """Compara Azul × Verde × Optante B no horizonte anual.

        Args:
            perfil_base: perfil ACR (distribuidora, subgrupo, classe, detalhe,
                atividade, reativos...). ``data_referencia`` é o fallback para
                os meses sem data própria.
            meses: 1 a 12 meses; cada item é um dict com
                ``data_referencia`` (AAAA-MM-DD), ``d_med_ponta``,
                ``d_med_fora_ponta``, ``d_med_unica``, ``e_ponta_kwh``,
                ``e_fora_ponta_kwh``.
            pis, cofins, icms, tipo_icms: tributos do motor (fórmula oficial).
            demanda_isenta_icms: demanda contratada e não utilizada sem ICMS
                (Súmula 391/STJ; confirmado nas faturas reais) — padrão True.
            tributar_reativos: tributa linhas de reativos (CEMIG/Equatorial).
            modalidade_atual: "Azul" ou "Verde".
            dc_atual_verde / dc_atual_azul_ponta / dc_atual_azul_fora:
                demandas contratadas atuais (None = usa 30 kW mínimo).
            k, encargos, opex_mensal, capex, horizonte_meses: parâmetros do PI.

        Returns:
            ``(ResultadoPlanejamento, pi_por_modalidade)`` — o PI é calculado
            sobre cada modalidade disponível do cenário otimizado.
        """
        medicoes = [
            MedicaoMensal(
                d_med_ponta=m.get("d_med_ponta"),
                d_med_fora_ponta=m.get("d_med_fora_ponta"),
                d_med_unica=m.get("d_med_unica"),
            )
            for m in meses
        ]
        demandas, avisos = montar_demandas(medicoes)
        avisos.append(AVISO_DEMANDA_OTIMA_REFERENCIA)

        medidas_verde = [d.verde for d in demandas]
        medidas_ponta = [d.azul_ponta for d in demandas]
        medidas_fora = [d.azul_fora_ponta for d in demandas]

        # Parcelas vigentes por mês e modalidade (busca 1× por mês/mod.).
        parcelas_verde = [self._parcelas(perfil_base, m, "Verde") for m in meses]
        parcelas_azul = [self._parcelas(perfil_base, m, "Azul") for m in meses]

        # ------------------------------------------------------------------
        # Funções de custo com o MOTOR COMPLETO (com tributos)
        # ------------------------------------------------------------------
        def custo_verde(dc: float, i: int) -> CustoDemandaMensal:
            fatura = self._motor_mes(
                perfil_base, meses[i], "Verde", parcelas_verde[i],
                dc_unica=dc, demanda_unica=True,
                pis=pis, cofins=cofins, icms=icms, tipo_icms=tipo_icms,
                demanda_isenta_icms=demanda_isenta_icms,
                tributar_reativos=tributar_reativos,
            )
            d_med = medidas_verde[i]
            detalhe = custo_demanda_mensal(d_med, dc, 1.0)
            return CustoDemandaMensal(
                faturavel_kw=detalhe.faturavel_kw,
                ultrapassagem_kw=detalhe.ultrapassagem_kw,
                ociosidade_kw=detalhe.ociosidade_kw,
                custo=fatura.custo_total,
            )

        def custo_azul(dc_ponta: float, dc_fora: float, i: int) -> float:
            fatura = self._motor_mes(
                perfil_base, meses[i], "Azul", parcelas_azul[i],
                dc_unica=None,
                dc_ponta=dc_ponta, dc_fora=dc_fora, demanda_unica=False,
                pis=pis, cofins=cofins, icms=icms, tipo_icms=tipo_icms,
                demanda_isenta_icms=demanda_isenta_icms,
                tributar_reativos=tributar_reativos,
            )
            return fatura.custo_total

        # ------------------------------------------------------------------
        # Otimização (Azul: otimiza cada posto com o outro fixo, e confirma)
        # ------------------------------------------------------------------
        verde_otimo = otimizar_contrato(medidas_verde, custo_verde)

        dc_fora_fixo = dc_atual_azul_fora if dc_atual_azul_fora else DC_MINIMO_GRUPO_A
        ponta_otimo = otimizar_contrato(
            medidas_ponta,
            lambda dc, i: CustoDemandaMensal(
                faturavel_kw=max(dc, medidas_ponta[i]),
                ultrapassagem_kw=(
                    medidas_ponta[i] - dc if medidas_ponta[i] > 1.05 * dc else 0.0
                ),
                ociosidade_kw=max(dc - medidas_ponta[i], 0.0),
                custo=custo_azul(dc, dc_fora_fixo, i),
            ),
        )
        fora_otimo = otimizar_contrato(
            medidas_fora,
            lambda dc, i: CustoDemandaMensal(
                faturavel_kw=max(dc, medidas_fora[i]),
                ultrapassagem_kw=(
                    medidas_fora[i] - dc if medidas_fora[i] > 1.05 * dc else 0.0
                ),
                ociosidade_kw=max(dc - medidas_fora[i], 0.0),
                custo=custo_azul(ponta_otimo.dc, dc, i),
            ),
        )
        custo_azul_otimo = sum(
            custo_azul(ponta_otimo.dc, fora_otimo.dc, i)
            for i in range(len(meses))
        )

        # ------------------------------------------------------------------
        # Cenário contrato atual
        # ------------------------------------------------------------------
        dc_verde_atual = dc_atual_verde if dc_atual_verde else DC_MINIMO_GRUPO_A
        custo_verde_atual = sum(
            custo_verde(dc_verde_atual, i).custo for i in range(len(meses))
        )
        dc_ponta_atual = (
            dc_atual_azul_ponta if dc_atual_azul_ponta else DC_MINIMO_GRUPO_A
        )
        dc_fora_atual = (
            dc_atual_azul_fora if dc_atual_azul_fora else DC_MINIMO_GRUPO_A
        )
        custo_azul_atual = sum(
            custo_azul(dc_ponta_atual, dc_fora_atual, i)
            for i in range(len(meses))
        )

        # ------------------------------------------------------------------
        # Optante B (elegibilidade existente; monômia não otimiza demanda)
        # ------------------------------------------------------------------
        elegiveis = modalidades_elegiveis(perfil_base)
        custo_optante = None
        if "OPTANTE B" in elegiveis:
            parcelas_optante = [
                self._parcelas(perfil_base, m, "Optante B") for m in meses
            ]
            custo_optante = sum(
                self._motor_mes(
                    perfil_base, meses[i], "Optante B", parcelas_optante[i],
                    dc_unica=None, demanda_unica=False,
                    pis=pis, cofins=cofins, icms=icms, tipo_icms=tipo_icms,
                    demanda_isenta_icms=demanda_isenta_icms,
                    tributar_reativos=tributar_reativos,
                ).custo_total
                for i in range(len(meses))
            )

        # ------------------------------------------------------------------
        # Monta resultados por modalidade
        # ------------------------------------------------------------------
        verde_resultado = ResultadoModalidadePlanejamento(
            modalidade="Verde",
            custo_contrato_atual=custo_verde_atual,
            custo_demanda_otimizada=verde_otimo.custo_anual,
            dc_atual=dc_verde_atual,
            dc_otima=verde_otimo.dc,
            detalhe=verde_otimo,
        )
        azul_resultado = ResultadoModalidadePlanejamento(
            modalidade="Azul",
            custo_contrato_atual=custo_azul_atual,
            custo_demanda_otimizada=custo_azul_otimo,
            dc_atual=(dc_ponta_atual, dc_fora_atual),
            dc_otima=(ponta_otimo.dc, fora_otimo.dc),
            detalhe=ponta_otimo,
        )
        modalidades_resultado = [azul_resultado, verde_resultado]
        if custo_optante is not None:
            modalidades_resultado.append(
                ResultadoModalidadePlanejamento(
                    modalidade="Optante B",
                    custo_contrato_atual=custo_optante,
                    custo_demanda_otimizada=custo_optante,
                    dc_atual=None,
                    dc_otima=0.0,
                    detalhe=verde_otimo,  # sem detalhe de demanda
                )
            )

        # ------------------------------------------------------------------
        # Equilíbrio (somente quando a ponta foi estimada)
        # ------------------------------------------------------------------
        equilibrio = None
        if any(m.get("d_med_ponta") is None for m in meses):
            custo_verde_ref = verde_resultado.custo_demanda_otimizada
            d_unica_ref = medidas_verde[0]

            def custo_azul_para_ponta(dp: float) -> float:
                medidas_ponta_estimadas = [dp] * len(meses)
                r = otimizar_contrato(
                    medidas_ponta_estimadas,
                    lambda dc, i: CustoDemandaMensal(
                        faturavel_kw=max(dc, dp),
                        ultrapassagem_kw=dp - dc if dp > 1.05 * dc else 0.0,
                        ociosidade_kw=max(dc - dp, 0.0),
                        custo=custo_azul(dc, fora_otimo.dc, i),
                    ),
                )
                return r.custo_anual

            equilibrio = demanda_ponta_equilibrio(
                custo_azul_para_ponta,
                custo_verde=custo_verde_ref,
                d_med_unica=d_unica_ref,
            )

        planejamento = comparar_planejamento(
            modalidades_resultado,
            modalidade_atual=modalidade_atual,
            avisos=avisos,
            equilibrio=equilibrio,
        )

        # ------------------------------------------------------------------
        # PI do período: soma mês a mês (especificação)
        # PI = (Σ C_E_ACR[m] − n·OPEX − n·CAPEX/N) / Σ BASE_ACL[m]
        # com TE e bandeira de cada mês. O PI mensal fica como informação.
        # ------------------------------------------------------------------
        from core.epi import calcular_pi, calcular_pi_meses

        pi_por_modalidade: dict[str, dict] = {}
        for resultado in modalidades_resultado:
            try:
                meses_pi = []
                for m in meses:
                    perfil_m = replace(
                        perfil_base,
                        data_referencia=(
                            date.fromisoformat(m["data_referencia"])
                            if m.get("data_referencia")
                            else perfil_base.data_referencia
                        ),
                        consumo_ponta_kwh=_consumo_obrigatorio(m, "e_ponta_kwh"),
                        consumo_fora_ponta_kwh=_consumo_obrigatorio(m, "e_fora_ponta_kwh"),
                    )
                    te_ponta, te_fora = self._epi._buscar_te(
                        perfil_m,
                        resultado.modalidade.strip().title(),
                        perfil_m.data_referencia,
                    )
                    bandeira = self._calculo._repo.buscar_bandeira(
                        perfil_m.data_referencia
                    )
                    meses_pi.append(
                        {
                            "e_ponta": perfil_m.consumo_ponta_kwh / 1000.0,
                            "e_fora_ponta": perfil_m.consumo_fora_ponta_kwh / 1000.0,
                            "te_ponta": te_ponta,
                            "te_fora_ponta": te_fora,
                            "bandeira": bandeira[2] if bandeira else 0.0,
                        }
                    )
                anual = calcular_pi_meses(
                    meses_pi,
                    pis=pis,
                    cofins=cofins,
                    icms=icms,
                    encargos=encargos,
                    k=k,
                    opex_mensal=opex_mensal,
                    capex=capex,
                    horizonte_meses=horizonte_meses,
                )
                mensal = [
                    calcular_pi(
                        e_ponta=m["e_ponta"],
                        e_fora_ponta=m["e_fora_ponta"],
                        te_ponta=m["te_ponta"],
                        te_fora_ponta=m["te_fora_ponta"],
                        pis=pis,
                        cofins=cofins,
                        icms=icms,
                        bandeira=m["bandeira"],
                        encargos=encargos,
                        k=k,
                        opex_mensal=opex_mensal,
                        capex=capex,
                        horizonte_meses=horizonte_meses,
                    ).pi
                    for m in meses_pi
                ]
                pi_por_modalidade[resultado.modalidade] = {
                    "anual": anual.pi,
                    "mensal": mensal,
                }
            except ValueError:
                pi_por_modalidade[resultado.modalidade] = {
                    "anual": None,
                    "mensal": [],
                }

        return planejamento, pi_por_modalidade

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _parcelas(
        self, perfil_base: Consumidor, mes: dict, modalidade: str
    ) -> list:
        consumidor = self._consumidor_mes(perfil_base, mes, modalidade)
        parcelas, _nao, _avisos, _du = self._calculo.parcelas_vigentes(
            consumidor, modalidade, BASE_PADRAO
        )
        return parcelas

    def _motor_mes(
        self,
        perfil_base: Consumidor,
        mes: dict,
        modalidade: str,
        parcelas: list,
        *,
        dc_unica: float | None,
        dc_ponta: float | None = None,
        dc_fora: float | None = None,
        demanda_unica: bool,
        pis: float,
        cofins: float,
        icms: float,
        tipo_icms: str,
        demanda_isenta_icms: bool = True,
        tributar_reativos: bool = False,
    ):
        consumidor = self._consumidor_mes(
            perfil_base,
            mes,
            modalidade,
            dc_unica=dc_unica,
            dc_ponta=dc_ponta,
            dc_fora=dc_fora,
        )
        bandeira = self._calculo._repo.buscar_bandeira(consumidor.data_referencia)
        if bandeira is not None:
            consumidor = replace(
                consumidor, bandeira_adicional_r_kwh=bandeira[1]
            )
        return calcular_fatura(
            consumidor,
            modalidade,
            parcelas,
            demanda_unica=demanda_unica,
            aplicar_tributos=True,
            pis=pis,
            cofins=cofins,
            icms=icms,
            tipo_icms=tipo_icms,
            demanda_isenta_icms=demanda_isenta_icms,
            tributar_reativos=tributar_reativos,
        )

    def _consumidor_mes(
        self,
        perfil_base: Consumidor,
        mes: dict,
        modalidade: str,
        *,
        dc_unica: float | None = None,
        dc_ponta: float | None = None,
        dc_fora: float | None = None,
    ) -> Consumidor:
        data_ref = (
            date.fromisoformat(mes["data_referencia"])
            if mes.get("data_referencia")
            else perfil_base.data_referencia
        )
        kwargs: dict = {
            "data_referencia": data_ref,
            "consumo_ponta_kwh": _consumo_obrigatorio(mes, "e_ponta_kwh"),
            "consumo_fora_ponta_kwh": _consumo_obrigatorio(mes, "e_fora_ponta_kwh"),
        }
        # Demanda medida do mês pela MESMA regra do otimizador (item A,
        # core.planejamento.montar_demanda): com histórico HP/HFP a Verde usa
        # max(ponta, fora); só com a demanda única, a Azul usa a única nos
        # dois postos. (Antes a Verde lia só d_med_unica e, com histórico por
        # posto, faturava medida = 0 → DC ótima caía no mínimo de 30 kW.)
        demanda, _ = montar_demanda(
            MedicaoMensal(
                d_med_ponta=mes.get("d_med_ponta"),
                d_med_fora_ponta=mes.get("d_med_fora_ponta"),
                d_med_unica=mes.get("d_med_unica"),
            )
        )
        if modalidade.strip().title() == "Verde":
            kwargs["demanda_medida_unica_kw"] = float(demanda.verde)
            if dc_unica is not None:
                kwargs["demanda_contratada_unica_kw"] = dc_unica
        else:
            kwargs["demanda_ponta_kw"] = float(demanda.azul_ponta)
            kwargs["demanda_fora_ponta_kw"] = float(demanda.azul_fora_ponta)
            if dc_ponta is not None:
                kwargs["demanda_contratada_ponta_kw"] = dc_ponta
            if dc_fora is not None:
                kwargs["demanda_contratada_fora_ponta_kw"] = dc_fora
        return replace(perfil_base, **kwargs)
