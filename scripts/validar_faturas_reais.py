"""Validação camada 1 de TODOS os casos de faturas reais (sem banco).

Usa a mesma rotina dos resultados do artigo (scripts/resultados_artigo.py):
tarifas líquidas impressas na fatura, flags validadas (demanda isenta de ICMS,
reativo tributado exceto Copel) e agrupamento linha a linha da fatura.
Critério: ≤ R$ 0,05 por item e ≤ R$ 1,00 no total técnico.

Uso: python scripts/validar_faturas_reais.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_RAIZ = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location("resultados_artigo", _RAIZ / "resultados_artigo.py")
ra = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ra)


def main() -> None:
    for arq in sorted(ra.CASOS.glob("*.json")):
        r = ra.validar_arquivo(arq.name)
        status = "OK" if r["aprovado"] else "DIVERGE"
        print("=" * 90)
        print(f"{r['caso']}  [{arq.name}]  → {status}  (Δ total {r['delta_total']:+.2f}, máx/linha {r['max_delta_linha']:.2f})")
        for l in r["linhas"]:
            motor = "sem mapeamento" if l["motor"] is None else f"{l['motor']:>12,.2f}"
            delta = "" if l["delta"] is None else f"{l['delta']:+.2f}"
            print(f"  {l['item'][:38]:40s} fatura={l['fatura']:>12,.2f} motor={motor}  Δ {delta}")
        if not r["aprovado"]:
            for n in r["notas"]:
                print(f"  NOTA: {n}")


if __name__ == "__main__":
    main()
