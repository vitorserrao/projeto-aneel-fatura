"""Carrega a tabela bandeira_valor com o histórico de valores das bandeiras.

Fonte: aba 'valores Bandeira Tarifária' da planilha do Simulador (colunas
L/M/N: vigência a partir de, bandeira e valor R$/MWh).
Idempotente (ON CONFLICT por bandeira+vigência).
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from infra.database import create_session_factory

FONTE = (
    "Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm (Kevin Wu) / "
    "aba 'valores Bandeira Tarifária' (histórico L/M/N)"
)

# (bandeira, vigencia_inicio, valor_mwh)
HISTORICO = [
    ("Amarela", "2015-01-01", 15.0),
    ("Vermelha P1", "2015-01-01", 30.0),
    ("Amarela", "2015-03-02", 25.0),
    ("Vermelha P1", "2015-03-02", 55.0),
    ("Amarela", "2015-09-01", 25.0),
    ("Vermelha P1", "2015-09-01", 45.0),
    ("Amarela", "2016-02-01", 15.0),
    ("Vermelha P1", "2016-02-01", 30.0),
    ("Vermelha P2", "2016-02-01", 45.0),
    ("Amarela", "2017-02-01", 20.0),
    ("Vermelha P1", "2017-02-01", 30.0),
    ("Vermelha P2", "2017-02-01", 35.0),
    ("Amarela", "2018-05-01", 10.0),
    ("Vermelha P1", "2018-05-01", 30.0),
    ("Vermelha P2", "2018-05-01", 50.0),
    ("Amarela", "2019-06-01", 15.0),
    ("Vermelha P1", "2019-06-01", 40.0),
    ("Vermelha P2", "2019-06-01", 60.0),
    ("Amarela", "2019-11-01", 13.43),
    ("Vermelha P1", "2019-11-01", 41.69),
    ("Vermelha P2", "2019-11-01", 62.43),
    ("Amarela", "2021-07-01", 18.74),
    ("Vermelha P1", "2021-07-01", 39.71),
    ("Vermelha P2", "2021-07-01", 94.92),
    ("Amarela", "2022-07-01", 29.89),
    ("Vermelha P1", "2022-07-01", 65.0),
    ("Vermelha P2", "2022-07-01", 97.95),
    ("Amarela", "2024-04-01", 18.85),
    ("Vermelha P1", "2024-04-01", 44.63),
    ("Vermelha P2", "2024-04-01", 78.77),
]


def carregar() -> int:
    count = 0
    with create_session_factory()() as sess:
        for bandeira, vig, mwh in HISTORICO:
            sess.execute(
                text("""
                    INSERT INTO bandeira_valor (
                        bandeira, vigencia_inicio, valor_mwh, valor_kwh, fonte
                    ) VALUES (:b, :v, :mwh, :kwh, :fonte)
                    ON CONFLICT (bandeira, vigencia_inicio) DO UPDATE SET
                        valor_mwh = EXCLUDED.valor_mwh,
                        valor_kwh = EXCLUDED.valor_kwh,
                        fonte = EXCLUDED.fonte
                """),
                {
                    "b": bandeira,
                    "v": date.fromisoformat(vig),
                    "mwh": mwh,
                    "kwh": mwh / 1000.0,
                    "fonte": FONTE,
                },
            )
            count += 1
        sess.commit()
    return count


if __name__ == "__main__":
    n = carregar()
    print(f"bandeira_valor: {n} registros carregados")
