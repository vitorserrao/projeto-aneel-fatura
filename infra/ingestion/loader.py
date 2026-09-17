"""Carregador do dataset de Tarifas de Aplicação da ANEEL.

Lê o CSV bruto preservando o conteúdo original (BOM, aspas, vírgulas internas,
decimal brasileiro) e devolve registros ``dict`` raw com os nomes REAIS das
colunas. Este módulo NÃO normaliza nada — apenas leitura fiel ao arquivo.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

COLUNAS_REAIS = [
    "_id",
    "DatGeracaoConjuntoDados",
    "DscREH",
    "SigAgente",
    "NumCNPJDistribuidora",
    "DatInicioVigencia",
    "DatFimVigencia",
    "DscBaseTarifaria",
    "DscSubGrupo",
    "DscModalidadeTarifaria",
    "DscClasse",
    "DscSubClasse",
    "DscDetalhe",
    "NomPostoTarifario",
    "DscUnidadeTerciaria",
    "SigAgenteAcessante",
    "VlrTUSD",
    "VlrTE",
]

N_COLUNAS_ESPERADO = 18


class CsvAneelNaoEncontrado(FileNotFoundError):
    """O arquivo CSV não foi encontrado."""


class CsvAneelMalformado(ValueError):
    """O cabeçalho ou a estrutura do CSV não corresponde ao esperado."""


def carregar_dataset(caminho) -> Iterator[dict[str, str]]:
    """Itera sobre as linhas do CSV bruto como dicts de strings.

    Valida o cabeçalho (deve conter as 18 colunas reais, em qualquer ordem).
    Cada linha de dados é devolvida como um dict coluna -> valor (string),
    sem normalização. O arquivo é aberto em modo leitura (nunca reescrito).

    Raises:
        CsvAneelNaoEncontrado: arquivo inexistente.
        CsvAneelMalformado: cabeçalho não casa com as colunas esperadas, ou
            uma linha de dados tem número diferente de colunas do cabeçalho.
    """
    path = Path(caminho)
    if not path.is_file():
        raise CsvAneelNaoEncontrado(f"CSV não encontrado: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise CsvAneelMalformado("CSV sem cabeçalho")
        if len(reader.fieldnames) != N_COLUNAS_ESPERADO:
            raise CsvAneelMalformado(
                f"esperado {N_COLUNAS_ESPERADO} colunas, "
                f"encontrado {len(reader.fieldnames)}: {reader.fieldnames}"
            )
        incompletos = set(reader.fieldnames) - set(COLUNAS_REAIS)
        if incompletos:
            raise CsvAneelMalformado(
                f"colunas não reconhecidas: {sorted(incompletos)}"
            )
        for linha in reader:
            yield linha
