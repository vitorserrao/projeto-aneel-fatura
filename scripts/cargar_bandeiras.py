"""Carrega a tabela bandeira_tarifaria a partir da planilha do Simulador.

Fonte: Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm
       aba 'valores Bandeira Tarifária' (Tabela11: competência/categoria/R$/MWh).
Idempotente (ON CONFLICT por competência).
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from infra.database import create_session_factory

CAMINHO_JSON = (
    r"C:\Users\vitor\AppData\Local\Temp\aneel_xlsm\bandeiras_dados.json"
)
FONTE = (
    "Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm (Kevin Wu) / "
    "aba 'valores Bandeira Tarifária' — fonte ANEEL dadosabertos"
)


def carregar() -> int:
    dados = json.load(open(CAMINHO_JSON, encoding="utf-8"))
    count = 0
    with create_session_factory()() as sess:
        for d in dados:
            dia = date.fromisoformat(d["competencia"])
            valor_kwh = d["r_mwh"] / 1000.0
            # vigência = mês civil da competência
            inicio = dia.replace(day=1)
            if dia.month == 12:
                fim = date(dia.year, 12, 31)
            else:
                nxt = date(dia.year, dia.month + 1, 1)
                from datetime import timedelta
                fim = nxt - timedelta(days=1)
            sess.execute(
                text("""
                    INSERT INTO bandeira_tarifaria (
                        competencia, bandeira, valor_mwh, valor_kwh,
                        vigencia_inicio, vigencia_fim, fonte
                    ) VALUES (
                        :comp, :band, :mwh, :kwh, :ini, :fim, :fonte
                    )
                    ON CONFLICT (competencia) DO UPDATE SET
                        bandeira = EXCLUDED.bandeira,
                        valor_mwh = EXCLUDED.valor_mwh,
                        valor_kwh = EXCLUDED.valor_kwh,
                        vigencia_inicio = EXCLUDED.vigencia_inicio,
                        vigencia_fim = EXCLUDED.vigencia_fim,
                        fonte = EXCLUDED.fonte
                """),
                {
                    "comp": dia,
                    "band": d["bandeira"],
                    "mwh": d["r_mwh"],
                    "kwh": valor_kwh,
                    "ini": inicio,
                    "fim": fim,
                    "fonte": FONTE,
                },
            )
            count += 1
        sess.commit()
    return count


if __name__ == "__main__":
    n = carregar()
    print(f"bandeira_tarifaria: {n} competências carregadas")
