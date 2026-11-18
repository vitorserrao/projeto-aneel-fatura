"""Contraprova do motor contra faturas reais (Verde).

Para cada fatura em ``tests/fixtures/faturas/*.json``:
1. busca no ``TarifaRepository`` as tarifas vigentes na data de referência
   (datas de leitura no meio do ciclo — mesma vigência);
2. simula a fatura com ``fatura_verde(...)`` usando a modalidade e a
   contratada REAIS (sem otimizar);
3. compara componente a componente e o total.

Tolerância do total: ``config.TOLERANCIA_VALIDACAO`` (padrão 1%).

Os dois casos conhecidos falham o total por uma regra ainda não implementada
em ``fatura_verde``: a parcela da demanda CONTRATADA NÃO UTILIZADA é isenta
de ICMS nas faturas reais (Copel e CEMIG). A falha é esperada e está
documentada em ``docs/validacao_faturas.md`` — o motor NÃO é ajustado para
forçar o resultado.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

import config
from core.motor_calculo import fatura_verde
from core.models import (
    GRANDEZA_DEMANDA,
    GRANDEZA_ENERGIA,
    POSTO_FORA_PONTA,
    POSTO_PONTA,
    Consumidor,
)
from services.calculo_service import BASE_PADRAO, CalculoService

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "faturas"
REPORT = Path(__file__).resolve().parents[2] / "docs" / "validacao_faturas.md"

CASES = [
    json.loads(p.read_text(encoding="utf-8"))
    for p in sorted(FIXTURES.glob("*.json"))
]


@pytest.fixture(scope="module")
def repo():
    from infra.database import create_db_engine, get_session_factory, ping_db
    from infra.repositories.tarifa_repository import TarifaRepository

    try:
        ping_db(create_db_engine())
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"PostgreSQL indisponível: {exc}")
    return TarifaRepository(get_session_factory())


def _tarifas_verde(repo, caso) -> dict[str, float | None]:
    """Tarifas líquidas da Verde vigentes na data de referência da fatura."""
    meta = caso["meta"]
    consumidor = Consumidor(
        distribuidora=meta["distribuidora"],
        subgrupo=meta["subgrupo"],
        classe="Não se aplica",
        detalhe="Não se aplica",
        data_referencia=date.fromisoformat(meta["data_referencia"]),
    )
    parcelas, _nao, _avisos, _du = CalculoService(repo).parcelas_vigentes(
        consumidor, "Verde", BASE_PADRAO
    )

    def unica(componente: str, grandeza: str, posto: str) -> float | None:
        vals = [
            float(p.valor)
            for p in parcelas
            if p.componente == componente
            and p.grandeza == grandeza
            and p.posto == posto
        ]
        return vals[0] if len(vals) == 1 else None

    def energia_mwh(componente: str, posto: str) -> float | None:
        vals = [
            p for p in parcelas
            if p.componente == componente
            and p.grandeza == GRANDEZA_ENERGIA
            and p.posto == posto
        ]
        if len(vals) != 1:
            return None
        valor = float(vals[0].valor)
        return valor * 1000.0 if vals[0].unidade == "R$/kWh" else valor

    return {
        "tusd_demanda": unica("TUSD", GRANDEZA_DEMANDA, POSTO_PONTA),
        "tusd_energia_ponta": energia_mwh("TUSD", POSTO_PONTA),
        "tusd_energia_fora_ponta": energia_mwh("TUSD", POSTO_FORA_PONTA),
        "te_energia_ponta": energia_mwh("TE", POSTO_PONTA),
        "te_energia_fora_ponta": energia_mwh("TE", POSTO_FORA_PONTA),
    }


def _simular(caso, tarifas):
    entrada = caso["entrada"]
    trib = caso["tributos"]
    fatura = fatura_verde(
        demanda_medida_unica_kw=entrada["demanda_medida_unica_kw"],
        demanda_contratada_unica_kw=entrada["demanda_contratada_unica_kw"],
        consumo_ponta_kwh=entrada["consumo_ponta_kwh"],
        consumo_fora_ponta_kwh=entrada["consumo_fora_ponta_kwh"],
        tarifa_tusd_demanda_r_kw=tarifas["tusd_demanda"],
        tarifa_tusd_energia_ponta_r_mwh=tarifas["tusd_energia_ponta"],
        tarifa_tusd_energia_fora_ponta_r_mwh=tarifas["tusd_energia_fora_ponta"],
        tarifa_te_energia_ponta_r_mwh=tarifas["te_energia_ponta"],
        tarifa_te_energia_fora_ponta_r_mwh=tarifas["te_energia_fora_ponta"],
        tolerancia=config.TOLERANCIA_ULTRAPASSAGEM,
        fator_ultrapassagem=config.FATOR_ULTRAPASSAGEM,
        pis=trib["pis"],
        cofins=trib["cofins"],
        icms=trib["icms"],
        tipo_icms=trib.get("tipo_icms", "fora"),
        reativos_rs=entrada["reativos_rs"],
        bandeira_rs=entrada["bandeira_rs"],
    )
    return fatura, {
        "tusd_demanda": fatura.tusd_demanda,
        "tusd_energia_ponta": fatura.tusd_energia_ponta,
        "tusd_energia_fora_ponta": fatura.tusd_energia_fora_ponta,
        "te_energia_ponta": fatura.te_energia_ponta,
        "te_energia_fora_ponta": fatura.te_energia_fora_ponta,
        "ultrapassagem": fatura.ultrapassagem,
        "reativos": fatura.reativos,
        "bandeira": fatura.bandeira,
    }


def _tabela(caso, linhas, total_real, total_sim) -> str:
    texto = [
        f"\n{caso['meta']['distribuidora']} · {caso['meta']['competencia']} "
        f"(total técnico fatura R$ {total_real:,.2f}, simulado R$ {total_sim:,.2f})\n",
        "| Componente | Fatura real | Simulado | Diferença (R$) | Diferença (%) |",
        "|---|---:|---:|---:|---:|",
    ]
    for nome, real, sim, delta, pct in linhas:
        sim_s = "—" if sim is None else f"{sim:,.2f}"
        pct_s = "—" if pct is None else f"{pct:+.2f}%"
        texto.append(
            f"| {nome} | {real:,.2f} | {sim_s} | "
            f"{'—' if delta is None else f'{delta:+,.2f}'} | {pct_s} |"
        )
    return "\n".join(texto)


def _executar(caso, repo):
    tarifas = _tarifas_verde(repo, caso)
    if any(v is None for v in tarifas.values()):
        pytest.skip(
            f"tarifa líquida ausente/ambígua no banco para "
            f"{caso['meta']['distribuidora']} {caso['meta']['competencia']}"
        )
    fatura, sim = _simular(caso, tarifas)

    linhas = []
    for c in caso["comparar"]:
        real = float(c["real"])
        valor_sim = sum(sim[n] for n in c["sim"])
        delta = valor_sim - real
        pct = delta / real * 100.0 if real else None
        linhas.append((c["componente"], real, valor_sim, delta, pct))

    total_real = float(caso["total_tecnico"])
    total_sim = fatura.custo_total
    delta_total = total_sim - total_real
    pct_total = delta_total / total_real * 100.0

    return {
        "linhas": linhas,
        "total_real": total_real,
        "total_sim": total_sim,
        "delta_total": delta_total,
        "pct_total": pct_total,
        "tabela": _tabela(caso, linhas, total_real, total_sim),
    }


@pytest.mark.xfail(
    strict=False,
    reason=(
        "demanda contratada não utilizada é isenta de ICMS nas faturas reais; "
        "fatura_verde ainda não implementa a parcela isenta (docs/validacao_faturas.md)"
    ),
)
@pytest.mark.parametrize("caso", CASES, ids=lambda c: c["id"])
def test_fatura_real_dentro_da_tolerancia(caso, repo):
    resultado = _executar(caso, repo)
    tolerancia_abs = config.TOLERANCIA_VALIDACAO * resultado["total_real"]
    assert abs(resultado["delta_total"]) <= tolerancia_abs, (
        f"diferença no total acima da tolerância de "
        f"{config.TOLERANCIA_VALIDACAO:.1%} "
        f"(R$ {resultado['delta_total']:+,.2f} = {resultado['pct_total']:+.2f}%)"
        f"{resultado['tabela']}"
    )


def test_gerar_relatorio_validacao(repo):
    """Regenera docs/validacao_faturas.md com as tabelas comparativas."""
    secoes = [
        "# Validação contra faturas reais (sprint feriados móveis)\n",
        "Contraprova do `fatura_verde(...)` com tarifas do `TarifaRepository` "
        "vigentes na data de referência de cada fatura. Tolerância do total: "
        f"`config.TOLERANCIA_VALIDACAO` = {config.TOLERANCIA_VALIDACAO:.1%}.\n",
        "## Casos\n",
    ]
    for caso in CASES:
        resultado = _executar(caso, repo)
        secoes.append(
            f"### {caso['meta']['distribuidora']} · {caso['meta']['modalidade']} · "
            f"{caso['meta']['competencia']} ({caso['id']})\n"
        )
        secoes.append(resultado["tabela"])
        secoes.append(
            f"\nTotal técnico: fatura R$ {resultado['total_real']:,.2f} × "
            f"simulado R$ {resultado['total_sim']:,.2f} → "
            f"Δ R$ {resultado['delta_total']:+,.2f} "
            f"({resultado['pct_total']:+.2f}%)\n"
        )
        secoes.append("\nNotas da fatura:\n")
        for nota in caso["meta"].get("notas", []):
            secoes.append(f"- {nota}")
        secoes.append("\n")
    secoes.append(
        "## Diferenças acima de 0,5% — causas\n\n"
        "1. **Demanda contratada não utilizada isenta de ICMS** (Copel e CEMIG): "
        "a fatura divide a demanda em parcela com ICMS e parcela isenta "
        "(só PIS/COFINS). O `fatura_verde` aplica o fator cheio em toda a "
        "demanda faturável — regra ainda não implementada nesta função "
        "(o `calcular_fatura` já tem `demanda_isenta_icms`).\n"
        "2. **Arredondamento por linha** (Copel, centavos): a fatura arredonda "
        "cada linha; o `fatura_verde` devolve valores sem arredondar.\n"
        "3. **CIP/COSIP**: não é componente do `fatura_verde`; fica fora da "
        "comparação técnica.\n"
    )
    REPORT.write_text("".join(secoes), encoding="utf-8")
