"""Comparação Verde × Azul a partir da fatura Verde (sprint Verde × Azul).

Nível 1 — com histórico de ponta (``dp`` e ``dfp`` medidos em todos os meses):
otimiza as contratadas da ponta, da fora ponta e da Verde, calcula as faturas
e devolve o resultado exato.

Nível 2 — sem histórico de ponta (só a demanda única da Verde): assume
``Dfp = D_verde`` (limite superior, conservador para a Azul), monta a faixa
possível de ``Dp`` por mês e simula a Azul nos extremos. Nunca decide pelo
meio da faixa; quando o resultado é inconclusivo, calcula ``dp_equilibrio``
por bisseção (o custo da Azul é monotônico em ``Dp``).

As tarifas vêm SEMPRE do ``TarifaRepository`` (via ``CalculoService``), nunca
são inventadas aqui. Os parâmetros regulatórios vêm de ``config`` e são
repassados explicitamente às funções puras do core.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, replace
from datetime import date
from typing import Sequence

import config
from core.motor_calculo import fatura_azul, fatura_verde
from core.models import (
    GRANDEZA_DEMANDA,
    GRANDEZA_ENERGIA,
    POSTO_FORA_PONTA,
    POSTO_PONTA,
    Consumidor,
)
from core.otimizador import (
    demanda_verde_mensal,
    faixa_demanda_ponta,
    horas_ponta,
    otimizar_contratada,
)
from services.calculo_service import BASE_PADRAO, CalculoService

_VERDE = "VERDE"
_AZUL = "AZUL"
_INCONCLUSIVO = "INCONCLUSIVO"

_CAMPOS_REATIVOS = (
    "reativo_energia_ponta_kvArh",
    "reativo_energia_fora_ponta_kvArh",
    "reativo_energia_capacitiva_kvArh",
    "reativo_demanda_ponta_kvAr",
    "reativo_demanda_fora_ponta_kvAr",
)


@dataclass(frozen=True)
class ResultadoComparacaoVerdeAzul:
    """Saída da comparação Verde × Azul (dataclass).

    ``azul`` é um valor (nível 1) ou ``{"min": ..., "max": ...}`` (nível 2).
    ``dc_otimas`` tem as chaves ``p``, ``fp`` e ``verde``; no nível 2, ``p``
    guarda ``{"min": ..., "max": ...}`` (reotimizada em cada extremo).
    """

    nivel: int
    veredito: str
    verde_atual: float
    verde_otimizada: float
    azul: float | dict[str, float]
    dc_otimas: dict[str, object]
    dp_equilibrio: float | None = None
    meses_analisados: int = 0
    avisos: tuple[str, ...] = ()


class ComparacaoVerdeAzulService:
    """Caso de uso: simular a Azul a partir de faturas Verde."""

    def __init__(self, calculo_service: CalculoService):
        self._calculo = calculo_service

    # ------------------------------------------------------------------ #
    # API pública
    # ------------------------------------------------------------------ #
    def comparar(
        self,
        perfil_base: Consumidor,
        meses: Sequence[dict],
        *,
        pis: float,
        cofins: float,
        icms: float,
        tipo_icms: str = "fora",
        contratada_atual: float | None = None,
    ) -> ResultadoComparacaoVerdeAzul:
        """Compara Verde × Azul para o histórico informado.

        ``meses``: lista de dicts mensais. Chaves aceitas (``None`` = dado
        ausente, nunca vira zero):
        ``data_referencia`` (AAAA-MM-DD), ``data_leitura_anterior``,
        ``data_leitura_atual``, ``dp``, ``dfp``, ``d_verde``, ``ep_kwh``,
        ``efp_kwh`` e os campos ``reativo_*`` (opcionais).
        """
        avisos: list[str] = []
        nivel1 = [
            m for m in meses
            if m.get("dp") is not None
            and m.get("dfp") is not None
            and m.get("ep_kwh") is not None
            and m.get("efp_kwh") is not None
        ]
        excluidos_n1 = [m for m in meses if m not in nivel1]
        for m in excluidos_n1:
            avisos.append(
                f"mês {m.get('data_referencia', '?')} excluído do nível 1: "
                "dp/dfp ou energia ausentes (dado ausente não vira zero)"
            )

        if nivel1:
            return self._comparar_nivel1(
                perfil_base, nivel1, pis, cofins, icms, tipo_icms,
                contratada_atual, avisos,
            )

        nivel2 = [
            m for m in meses
            if m.get("d_verde") is not None
            and m.get("ep_kwh") is not None
            and m.get("efp_kwh") is not None
        ]
        for m in meses:
            if m not in nivel2:
                avisos.append(
                    f"mês {m.get('data_referencia', '?')} excluído do nível 2: "
                    "d_verde ou energia ausentes (dado ausente não vira zero)"
                )
        if not nivel2:
            raise ValueError(
                "nenhum mês analisável: informe dp/dfp (nível 1) ou "
                "d_verde/ep_kwh/efp_kwh (nível 2)"
            )
        return self._comparar_nivel2(
            perfil_base, nivel2, pis, cofins, icms, tipo_icms,
            contratada_atual, avisos,
        )

    # ------------------------------------------------------------------ #
    # Nível 1 — com histórico de ponta
    # ------------------------------------------------------------------ #
    def _comparar_nivel1(
        self, perfil_base, meses, pis, cofins, icms, tipo_icms,
        contratada_atual, avisos,
    ) -> ResultadoComparacaoVerdeAzul:
        contratada = self._contratada_atual(contratada_atual, avisos)
        dps = [float(m["dp"]) for m in meses]
        dfps = [float(m["dfp"]) for m in meses]
        dverdes = [demanda_verde_mensal(dp, dfp) for dp, dfp in zip(dps, dfps)]

        dc_p, _ = otimizar_contratada(
            dps, config.DEMANDA_MINIMA_KW,
            config.TOLERANCIA_ULTRAPASSAGEM, config.FATOR_ULTRAPASSAGEM,
        )
        dc_fp, _ = otimizar_contratada(
            dfps, config.DEMANDA_MINIMA_KW,
            config.TOLERANCIA_ULTRAPASSAGEM, config.FATOR_ULTRAPASSAGEM,
        )
        dc_verde, _ = otimizar_contratada(
            dverdes, config.DEMANDA_MINIMA_KW,
            config.TOLERANCIA_ULTRAPASSAGEM, config.FATOR_ULTRAPASSAGEM,
        )

        dados = self._dados_mes(perfil_base, meses)
        verde_atual = self._verde_total(
            dados, dverdes, contratada, pis, cofins, icms, tipo_icms
        )
        verde_otimizada = self._verde_total(
            dados, dverdes, dc_verde, pis, cofins, icms, tipo_icms
        )
        azul = self._azul_total(
            dados, dps, dfps, dc_p, dc_fp, pis, cofins, icms, tipo_icms
        )

        delta = verde_atual - azul
        if delta > 0:
            veredito = _AZUL
        elif delta < 0:
            veredito = _VERDE
        else:
            veredito = _INCONCLUSIVO

        if len(meses) == 1:
            avisos.append("1 mês só: sazonalidade não captada")

        return ResultadoComparacaoVerdeAzul(
            nivel=1,
            veredito=veredito,
            verde_atual=verde_atual,
            verde_otimizada=verde_otimizada,
            azul=azul,
            dc_otimas={"p": dc_p, "fp": dc_fp, "verde": dc_verde},
            meses_analisados=len(meses),
            avisos=tuple(avisos),
        )

    # ------------------------------------------------------------------ #
    # Nível 2 — sem histórico de ponta
    # ------------------------------------------------------------------ #
    def _comparar_nivel2(
        self, perfil_base, meses, pis, cofins, icms, tipo_icms,
        contratada_atual, avisos,
    ) -> ResultadoComparacaoVerdeAzul:
        contratada = self._contratada_atual(contratada_atual, avisos)
        dverdes = [float(m["d_verde"]) for m in meses]
        dc_fp, _ = otimizar_contratada(
            dverdes, config.DEMANDA_MINIMA_KW,
            config.TOLERANCIA_ULTRAPASSAGEM, config.FATOR_ULTRAPASSAGEM,
        )
        dc_verde, _ = otimizar_contratada(
            dverdes, config.DEMANDA_MINIMA_KW,
            config.TOLERANCIA_ULTRAPASSAGEM, config.FATOR_ULTRAPASSAGEM,
        )

        faixas = []
        for mes, d_verde in zip(meses, dverdes):
            ep = float(mes["ep_kwh"])
            hp = self._horas_ponta_mes(mes, perfil_base, avisos)
            faixas.append(
                faixa_demanda_ponta(ep, hp, d_verde, config.DEMANDA_MINIMA_KW)
            )

        dps_min = [f[0] for f in faixas]
        dps_max = [f[1] for f in faixas]
        dc_p_min, _ = otimizar_contratada(
            dps_min, config.DEMANDA_MINIMA_KW,
            config.TOLERANCIA_ULTRAPASSAGEM, config.FATOR_ULTRAPASSAGEM,
        )
        dc_p_max, _ = otimizar_contratada(
            dps_max, config.DEMANDA_MINIMA_KW,
            config.TOLERANCIA_ULTRAPASSAGEM, config.FATOR_ULTRAPASSAGEM,
        )

        dados = self._dados_mes(perfil_base, meses)
        verde_atual = self._verde_total(
            dados, dverdes, contratada, pis, cofins, icms, tipo_icms
        )
        verde_otimizada = self._verde_total(
            dados, dverdes, dc_verde, pis, cofins, icms, tipo_icms
        )
        azul_min = self._azul_total(
            dados, dps_min, dverdes, dc_p_min, dc_fp,
            pis, cofins, icms, tipo_icms,
        )
        azul_max = self._azul_total(
            dados, dps_max, dverdes, dc_p_max, dc_fp,
            pis, cofins, icms, tipo_icms,
        )

        dp_eq: float | None = None
        if verde_atual < azul_min:
            veredito = _VERDE
        elif verde_atual > azul_max:
            veredito = _AZUL
        else:
            veredito = _INCONCLUSIVO
            dp_eq = self._dp_equilibrio(
                dados, dverdes, dc_fp, verde_atual,
                pis, cofins, icms, tipo_icms,
                lo=min(dps_min), hi=max(dps_max),
            )

        if len(meses) == 1:
            avisos.append("1 mês só: sazonalidade não captada")

        return ResultadoComparacaoVerdeAzul(
            nivel=2,
            veredito=veredito,
            verde_atual=verde_atual,
            verde_otimizada=verde_otimizada,
            azul={"min": azul_min, "max": azul_max},
            dc_otimas={
                "p": {"min": dc_p_min, "max": dc_p_max},
                "fp": dc_fp,
                "verde": dc_verde,
            },
            dp_equilibrio=dp_eq,
            meses_analisados=len(meses),
            avisos=tuple(avisos),
        )

    # ------------------------------------------------------------------ #
    # Totais mensais
    # ------------------------------------------------------------------ #
    def _dados_mes(self, perfil_base, meses):
        """Busca, para cada mês, o Consumidor e as tarifas Verde/Azul."""
        dados = []
        for mes in meses:
            consumidor = self._consumidor_mes(perfil_base, mes)
            tarifas_verde = self._tarifas_mes(consumidor, "Verde")
            tarifas_azul = self._tarifas_mes(consumidor, "Azul")
            adicionais = self._adicionais_mes(consumidor, mes)
            dados.append((consumidor, tarifas_verde, tarifas_azul, adicionais))
        return dados

    def _verde_total(
        self, dados, dverdes, contratada, pis, cofins, icms, tipo_icms
    ) -> float:
        total = 0.0
        for (consumidor, tv, _ta, adicionais), d_verde in zip(dados, dverdes):
            reativos_rs, bandeira_rs = adicionais
            fatura = fatura_verde(
                demanda_medida_unica_kw=d_verde,
                demanda_contratada_unica_kw=contratada,
                consumo_ponta_kwh=consumidor.consumo_ponta_kwh,
                consumo_fora_ponta_kwh=consumidor.consumo_fora_ponta_kwh,
                tarifa_tusd_demanda_r_kw=tv["tusd_demanda"],
                tarifa_tusd_energia_ponta_r_mwh=tv["tusd_energia_ponta"],
                tarifa_tusd_energia_fora_ponta_r_mwh=tv["tusd_energia_fora_ponta"],
                tarifa_te_energia_ponta_r_mwh=tv["te_energia_ponta"],
                tarifa_te_energia_fora_ponta_r_mwh=tv["te_energia_fora_ponta"],
                tolerancia=config.TOLERANCIA_ULTRAPASSAGEM,
                fator_ultrapassagem=config.FATOR_ULTRAPASSAGEM,
                pis=pis,
                cofins=cofins,
                icms=icms,
                tipo_icms=tipo_icms,
                reativos_rs=reativos_rs,
                bandeira_rs=bandeira_rs,
            )
            total += fatura.custo_total
        return total

    def _azul_total(
        self, dados, dps, dfps, dc_p, dc_fp, pis, cofins, icms, tipo_icms
    ) -> float:
        total = 0.0
        for (consumidor, _tv, ta, adicionais), dp, dfp in zip(dados, dps, dfps):
            reativos_rs, bandeira_rs = adicionais
            fatura = fatura_azul(
                demanda_ponta_kw=dp,
                demanda_fora_ponta_kw=dfp,
                demanda_contratada_ponta_kw=dc_p,
                demanda_contratada_fora_ponta_kw=dc_fp,
                consumo_ponta_kwh=consumidor.consumo_ponta_kwh,
                consumo_fora_ponta_kwh=consumidor.consumo_fora_ponta_kwh,
                tarifa_tusd_demanda_ponta_r_kw=ta["tusd_demanda_ponta"],
                tarifa_tusd_demanda_fora_ponta_r_kw=ta["tusd_demanda_fora_ponta"],
                tarifa_tusd_energia_ponta_r_mwh=ta["tusd_energia_ponta"],
                tarifa_tusd_energia_fora_ponta_r_mwh=ta["tusd_energia_fora_ponta"],
                tarifa_te_energia_ponta_r_mwh=ta["te_energia_ponta"],
                tarifa_te_energia_fora_ponta_r_mwh=ta["te_energia_fora_ponta"],
                tolerancia=config.TOLERANCIA_ULTRAPASSAGEM,
                fator_ultrapassagem=config.FATOR_ULTRAPASSAGEM,
                pis=pis,
                cofins=cofins,
                icms=icms,
                tipo_icms=tipo_icms,
                reativos_rs=reativos_rs,
                bandeira_rs=bandeira_rs,
            )
            total += fatura.custo_total
        return total

    def _dp_equilibrio(
        self, dados, dverdes, dc_fp, verde_atual,
        pis, cofins, icms, tipo_icms, lo, hi,
    ) -> float:
        """Bisseção em ``Dp`` (uniforme em todos os meses, reotimizando Dc_p).

        O custo da Azul é monotônico não decrescente em ``Dp``.
        """
        def custo_azul(dp: float) -> float:
            dps = [dp] * len(dverdes)
            dc_p, _ = otimizar_contratada(
                dps, config.DEMANDA_MINIMA_KW,
                config.TOLERANCIA_ULTRAPASSAGEM, config.FATOR_ULTRAPASSAGEM,
            )
            return self._azul_total(
                dados, dps, dverdes, dc_p, dc_fp,
                pis, cofins, icms, tipo_icms,
            )

        if custo_azul(hi) <= verde_atual:
            return hi
        if custo_azul(lo) >= verde_atual:
            return lo
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if custo_azul(mid) < verde_atual:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2.0

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _contratada_atual(self, contratada_atual, avisos) -> float:
        if contratada_atual is not None:
            return float(contratada_atual)
        avisos.append(
            "contratada atual não informada; usada a demanda mínima de "
            f"{config.DEMANDA_MINIMA_KW:g} kW como referência"
        )
        return float(config.DEMANDA_MINIMA_KW)

    def _consumidor_mes(self, perfil_base: Consumidor, mes: dict) -> Consumidor:
        data_ref = self._data_referencia(mes, perfil_base)
        return replace(
            perfil_base,
            data_referencia=data_ref,
            consumo_ponta_kwh=float(mes["ep_kwh"]),
            consumo_fora_ponta_kwh=float(mes["efp_kwh"]),
        )

    def _data_referencia(self, mes: dict, perfil_base: Consumidor) -> date:
        if mes.get("data_referencia"):
            return date.fromisoformat(str(mes["data_referencia"]))
        if perfil_base.data_referencia is not None:
            return perfil_base.data_referencia
        raise ValueError(
            "data_referencia é obrigatória no perfil ou em cada mês"
        )

    def _tarifas_mes(self, consumidor: Consumidor, modalidade: str) -> dict[str, float]:
        parcelas, _nao, _avisos, _du = self._calculo.parcelas_vigentes(
            consumidor, modalidade, BASE_PADRAO
        )
        if modalidade.strip().title() == "Verde":
            return {
                "tusd_demanda": self._unica(
                    parcelas, "TUSD", GRANDEZA_DEMANDA, POSTO_PONTA, modalidade
                ),
                "tusd_energia_ponta": self._energia_mwh(parcelas, "TUSD", POSTO_PONTA),
                "tusd_energia_fora_ponta": self._energia_mwh(
                    parcelas, "TUSD", POSTO_FORA_PONTA
                ),
                "te_energia_ponta": self._energia_mwh(parcelas, "TE", POSTO_PONTA),
                "te_energia_fora_ponta": self._energia_mwh(
                    parcelas, "TE", POSTO_FORA_PONTA
                ),
            }
        return {
            "tusd_demanda_ponta": self._unica(
                parcelas, "TUSD", GRANDEZA_DEMANDA, POSTO_PONTA, modalidade
            ),
            "tusd_demanda_fora_ponta": self._unica(
                parcelas, "TUSD", GRANDEZA_DEMANDA, POSTO_FORA_PONTA, modalidade
            ),
            "tusd_energia_ponta": self._energia_mwh(parcelas, "TUSD", POSTO_PONTA),
            "tusd_energia_fora_ponta": self._energia_mwh(
                parcelas, "TUSD", POSTO_FORA_PONTA
            ),
            "te_energia_ponta": self._energia_mwh(parcelas, "TE", POSTO_PONTA),
            "te_energia_fora_ponta": self._energia_mwh(
                parcelas, "TE", POSTO_FORA_PONTA
            ),
        }

    def _unica(self, parcelas, componente, grandeza, posto, modalidade) -> float:
        vals = [
            float(p.valor)
            for p in parcelas
            if p.componente == componente
            and p.grandeza == grandeza
            and p.posto == posto
        ]
        if len(vals) != 1:
            raise ValueError(
                f"tarifa {componente} {grandeza} {posto} da {modalidade} "
                f"ausente ou ambígua ({len(vals)} parcela(s))"
            )
        return vals[0]

    def _energia_mwh(self, parcelas, componente, posto) -> float:
        vals = [
            p for p in parcelas
            if p.componente == componente
            and p.grandeza == GRANDEZA_ENERGIA
            and p.posto == posto
        ]
        if len(vals) != 1:
            raise ValueError(
                f"tarifa {componente} ENERGIA {posto} ausente ou ambígua "
                f"({len(vals)} parcela(s))"
            )
        p = vals[0]
        valor = float(p.valor)
        if p.unidade == "R$/kWh":
            return valor * 1000.0
        return valor

    def _adicionais_mes(
        self, consumidor: Consumidor, mes: dict
    ) -> tuple[float, float]:
        """Devolve ``(reativos_rs, bandeira_rs)`` — iguais nas duas modalidades."""
        bandeira = self._calculo._repo.buscar_bandeira(consumidor.data_referencia)
        consumo_kwh = float(mes["ep_kwh"]) + float(mes["efp_kwh"])
        bandeira_rs = consumo_kwh * bandeira[1] if bandeira else 0.0
        reativos_rs = self._reativos_mes(consumidor, mes)
        return reativos_rs, bandeira_rs

    def _reativos_mes(self, consumidor: Consumidor, mes: dict) -> float:
        campos = {k: mes.get(k) for k in _CAMPOS_REATIVOS}
        if not any(campos.get(k) is not None and float(campos[k]) > 0 for k in campos):
            return 0.0
        from core.motor_calculo import _linhas_reativos_excedentes

        vrere, _av1 = self._calculo._buscar_vrere(consumidor, BASE_PADRAO)
        vrdre, _av2 = self._calculo._buscar_vrdre(consumidor, BASE_PADRAO)
        d_verde = float(mes["d_verde"]) if mes.get("d_verde") is not None else (
            demanda_verde_mensal(mes.get("dp"), mes.get("dfp"))
        )
        consumidor_reativos = replace(
            consumidor,
            demanda_medida_unica_kw=d_verde,
            demanda_contratada_unica_kw=d_verde,
            reativo_energia_ponta_kvArh=float(campos["reativo_energia_ponta_kvArh"] or 0.0),
            reativo_energia_fora_ponta_kvArh=float(campos["reativo_energia_fora_ponta_kvArh"] or 0.0),
            reativo_energia_capacitiva_kvArh=float(campos["reativo_energia_capacitiva_kvArh"] or 0.0),
            reativo_demanda_ponta_kvAr=float(campos["reativo_demanda_ponta_kvAr"] or 0.0),
            reativo_demanda_fora_ponta_kvAr=float(campos["reativo_demanda_fora_ponta_kvAr"] or 0.0),
        )
        linhas = _linhas_reativos_excedentes(
            consumidor_reativos,
            vrere_r_mwh=vrere,
            vrdre_r_kw=vrdre,
            demanda_unica=True,
        )
        return sum(l.custo for l in linhas)

    def _horas_ponta_mes(self, mes: dict, perfil_base, avisos) -> float:
        anterior = mes.get("data_leitura_anterior")
        atual = mes.get("data_leitura_atual")
        if anterior and atual:
            ant = date.fromisoformat(str(anterior))
            at = date.fromisoformat(str(atual))
            return horas_ponta(
                ant,
                at,
                self._feriados(ant.year, at.year),
                config.HORAS_PONTA_POR_DIA,
            )
        # Fallback: mês-calendário da data de referência (com aviso).
        data_ref = self._data_referencia(mes, perfil_base)
        avisos.append(
            f"mês {data_ref.isoformat()}: data de leitura ausente; usadas "
            "as horas de ponta do mês-calendário"
        )
        feriados = self._feriados(data_ref.year, data_ref.year)
        _, ultimo_dia = calendar.monthrange(data_ref.year, data_ref.month)
        dias_uteis = sum(
            1
            for dia in range(1, ultimo_dia + 1)
            if (d := date(data_ref.year, data_ref.month, dia)).weekday() < 5
            and d not in feriados
        )
        return dias_uteis * float(config.HORAS_PONTA_POR_DIA)

    def _feriados(self, ano_inicio: int, ano_fim: int) -> set[date]:
        return {
            date(ano, mes, dia)
            for ano in range(ano_inicio, ano_fim + 1)
            for mes, dia in config.FERIADOS_NACIONAIS
        }
