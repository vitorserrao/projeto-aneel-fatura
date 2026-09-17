"""Script de ingestão do dataset de Tarifas de Aplicação da ANEEL.

Uso:
    python -m scripts.ingest_aneel [caminho_do_csv]

Executa o pipeline completo (loader → cleaner → validator → carga transactional)
e imprime um resumo. O CSV em data/raw/ permanece intacto (somente leitura).
"""

from __future__ import annotations

import sys

from infra.database import create_session_factory
from infra.ingestion.load import PipelineIngestao, CargaAneelError

DEFAULT_CSV = "data/raw/fcf2906c-7c32-4b9b-a637-054e7a5234f4.csv"


def main(caminho_csv: str | None = None) -> int:
    target = caminho_csv or DEFAULT_CSV
    try:
        resumo = PipelineIngestao(create_session_factory()).executar(target)
    except CargaAneelError as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    print("Carga concluída:")
    for k, v in resumo.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else None))
