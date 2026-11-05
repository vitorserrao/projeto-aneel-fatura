"""Anonimiza os extratos e documentos de validação com faturas reais (LGPD).

Remove do repositório os dados que identificam os consumidores — nome,
endereço, CNPJ/CPF, inscrição estadual, números de cliente/instalação/conta
contrato, nota fiscal, chave de acesso, protocolo, medidor e código de barras —
e mantém todos os dados técnicos usados na validação (grandezas, tarifas,
tributos, leituras e históricos).

As distribuidoras (pessoas jurídicas concessionárias) continuam identificadas.

Uso:
    python scripts/anonimizar_faturas.py            # aplica
    python scripts/anonimizar_faturas.py --checar   # só verifica se sobrou algo
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EXTRATOS = RAIZ / "docs/validacao_faturas_reais/extratos"
DOCS_TEXTO = [
    RAIZ / "docs/validacao_faturas_reais/relatorio_final.md",
    RAIZ / "docs/validacao_faturas_reais/inventario_e_selecao.md",
    RAIZ / "docs/validacao_faturas_reais/divergencias.md",
    RAIZ / "docs/validacao_conta_real_copel_verde_2023.md",
    RAIZ / "scripts/gerar_doc_validacao_copel.py",
]

# Códigos usados no lugar dos nomes (documentos de texto).
PSEUDONIMOS = {
    "ON PETRO DISTRIBUIDORA DE COMBUSTIVEIS LTDA": "UC COPEL-1 (comercial, A4 Verde)",
    "Copel ON PETRO": "Copel UC COPEL-1",
    "COPEL ON PETRO": "COPEL UC COPEL-1",
    "ON PETRO": "UC COPEL-1",
    "CEMIG CEFET BH": "CEMIG UC CEMIG-1",
    "CEFET BH": "UC CEMIG-1",
    "ENEL CRBio": "ENEL UC ENEL-1",
    "CRBio": "UC ENEL-1",
    "Equatorial IFPA Abaetetuba": "Equatorial UC EQT-ABAETETUBA",
    "IFPA": "UC pública federal",
}

# Linhas inteiras removidas nos extratos (identificam cliente/endereço/pessoa).
LINHAS_PII = [
    r"CEFET", r"AV AMAZONAS", r"NOVA SUI", r"30421-169", r"^\s*Cliente:",
    r"N[ºo°] DO CLIENTE",
    r"ON PETRO", r"COMBUSTIVEIS LTDA", r"Endere[cç]o:", r"ALEXANDRE ZANCHETTA",
    r"Alexandre Zanchetta", r"ITALIA", r"Italia", r"Cidade: Sao Jose dos Pinhais",
    r"I\.E\.:", r"GERENTE DA AGENCIA", r"01543 2021",
    r"CONSELHO REGIONAL", r"CLIMACO BARBOSA", r"INSC\. EST",
    r"INSTITUTO FEDERAL", r"AV ESPIRITO SANTO", r"ABAETE", r"FRANCILANDIA",
    r"RD BR 316", r"^\s*CASTANHAL - PA", r"RD ERNESTO ACIOLY", r"ESCOLA AGRICOLA",
    r"Campus Tucuru", r"AV BRASILIA", r"Conta contrato geradora",
    r"Distribui[cç][aã]o Percentual das seguintes CC", r"IFPA",
]

# CNPJs das distribuidoras (públicos) — preservados.
CNPJ_DISTRIBUIDORAS = {
    "04.368.898/0001-06",  # Copel
    "06.981.180/0001-16",  # CEMIG-D
    "04.895.728/0001-80",  # Equatorial Pará
    "61.695.227/0001-93",  # ENEL SP
}
LINHA_DISTRIBUIDORA = re.compile(
    r"Rodovia Augusto Montenegro|Coqueiro - Bel[eé]m|BARBACENA|Jose Izidoro|"
    r"Mossungue|CEP: 81200-240|CEP: 30190-131|Copel Distribui|CEMIG DISTRIBUI|"
    r"Equatorial Par[aá] Distribuidora",
    re.IGNORECASE,
)

RE_CNPJ = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{8}/\d{4}-\d{2}")
RE_CEP = re.compile(r"\b\d{2}\.?\d{3}-\d{3}\b")
RE_CHAVE_AGRUPADA = re.compile(r"\b(?:\d{4}\s){10}\d{4}\b")
RE_HEX_FISCAL = re.compile(r"\b(?:[0-9A-F]{4}\.){7}[0-9A-F]{4}\b")
RE_ID_LONGO = re.compile(r"(?<![\d.,])\d{8,}(?![\d.,])")


def _anonimizar_linha(linha: str) -> str:
    if any(re.search(p, linha) for p in LINHAS_PII):
        return "[dados do cliente removidos]"
    eh_distribuidora = bool(LINHA_DISTRIBUIDORA.search(linha))
    linha = RE_CHAVE_AGRUPADA.sub("[ID]", linha)
    linha = RE_HEX_FISCAL.sub("[ID]", linha)
    linha = RE_CNPJ.sub(
        lambda m: m.group(0) if m.group(0) in CNPJ_DISTRIBUIDORAS else "[CNPJ]", linha
    )
    if not eh_distribuidora:
        linha = RE_CEP.sub("[CEP]", linha)
    linha = RE_ID_LONGO.sub("[ID]", linha)
    return linha


def anonimizar_extrato(texto: str) -> str:
    return "\n".join(_anonimizar_linha(l) for l in texto.splitlines()) + "\n"


def pseudonimizar(texto: str) -> str:
    for nome, codigo in sorted(PSEUDONIMOS.items(), key=lambda kv: -len(kv[0])):
        texto = texto.replace(nome, codigo)
    return texto


RESTOS = re.compile(
    r"ON PETRO|CEFET|CRBio|CONSELHO REGIONAL|INSTITUTO FEDERAL|IFPA|ZANCHETTA|"
    r"AV AMAZONAS|7000081824|3009014934|3009000112|09250921|62\.021\.837",
    re.IGNORECASE,
)


def checar() -> int:
    problemas = 0
    for arq in list(EXTRATOS.glob("*.txt")) + DOCS_TEXTO:
        if not arq.exists():
            continue
        for n, linha in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
            if RESTOS.search(linha):
                problemas += 1
                print(f"{arq.relative_to(RAIZ)}:{n}: {linha.strip()[:100]}")
    print(f"{problemas} ocorrência(s) identificável(is) restante(s)")
    return problemas


def main() -> None:
    if "--checar" in sys.argv:
        sys.exit(1 if checar() else 0)
    for arq in sorted(EXTRATOS.glob("*.txt")):
        arq.write_text(anonimizar_extrato(arq.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"anonimizado: {arq.relative_to(RAIZ)}")
    for arq in DOCS_TEXTO:
        if arq.exists():
            arq.write_text(pseudonimizar(arq.read_text(encoding="utf-8")), encoding="utf-8")
            print(f"pseudonimizado: {arq.relative_to(RAIZ)}")
    checar()


if __name__ == "__main__":
    main()
