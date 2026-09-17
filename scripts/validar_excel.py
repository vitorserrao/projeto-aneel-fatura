"""Validação dos resultados Python contra a ferramenta Excel `Recriar Faturas.xlsm`.

A comparação é um experimento de validação; o sistema NÃO depende do Excel.
ESQUELETO — a estrutura de comparação (entradas, TE, TUSD, demanda, energia,
total, diferenças absoluta/percentual) será preenchida quando houver resultados
reais e casos selecionados.
"""

from __future__ import annotations


def main() -> None:
    """Executa a validação contra o Excel.

    Raises:
        NotImplementedError: validação ainda não implementada.
    """
    raise NotImplementedError(
        "Validação contra o Excel ainda não implementada (docs/validacao_excel.md)."
    )


if __name__ == "__main__":
    main()
