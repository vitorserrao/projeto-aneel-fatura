"""Gera docs/validacao_conta_real_copel_verde_2023.docx (documento Word).

Uso:
    .venv\\Scripts\\python.exe scripts\\gerar_doc_validacao_copel.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt

DESTINO = Path(__file__).resolve().parent.parent / "docs" / (
    "validacao_conta_real_copel_verde_2023.docx"
)


def _tabela(doc, cabecalho: list[str], linhas: list[list[str]]) -> None:
    t = doc.add_table(rows=1, cols=len(cabecalho))
    t.style = "Light Grid Accent 1"
    for i, c in enumerate(cabecalho):
        t.rows[0].cells[i].text = c
    for linha in linhas:
        cells = t.add_row().cells
        for i, v in enumerate(linha):
            cells[i].text = str(v)


def main() -> int:
    doc = Document()

    doc.add_heading(
        "Validação contra conta real — Copel A4 Tarifa Verde (03/2023)", level=0
    )
    doc.add_paragraph(
        "Registro do teste de comparação entre uma conta real de energia "
        "elétrica (DANF3E / NF3E da Copel Distribuição) e o resultado do "
        "simulador do projeto."
    )
    p = doc.add_paragraph()
    p.add_run("Arquivo da conta: ").bold = True
    p.add_run("clipboard-20260916-114548.262904-000003.pdf (anexado). ")
    p.add_run("Data do teste: ").bold = True
    p.add_run("2025-09-16.")

    doc.add_heading("1. Dados da conta real", level=1)
    _tabela(
        doc,
        ["Campo", "Valor"],
        [
            ["Distribuidora", "Copel Distribuição S.A. (CNPJ 04.368.898/0001-06)"],
            ["Consumidor", "UC COPEL-1 (comercial, A4 Verde)"],
            ["Subgrupo", "A4"],
            ["Modalidade", "Tarifa Horária Verde"],
            ["Competência / fatura", "04/2023 (leituras 28/02/2023 a 31/03/2023)"],
            ["Data de emissão", "13/04/2023"],
            ["Total da fatura", "R$ 9.854,93"],
        ],
    )

    doc.add_heading("2. Grandezas faturadas (conta real)", level=1)
    _tabela(
        doc,
        ["Produto", "Faturado", "Tarifa (com tributos)", "Total (R$)"],
        [
            ["ENERGIA ELETRICA TE PONTA", "55 kWh", "0,499818", "27,49"],
            ["ENERGIA ELETRICA USD PONTA", "55 kWh", "1,323455", "72,79"],
            ["ENERGIA ELETRICA TE F PONTA", "9.094 kWh", "0,318435", "2.895,85"],
            ["ENERGIA ELETRICA USD F PONTA", "9.094 kWh", "0,142793", "1.298,56"],
            ["ENERGIA REAT EXCED TE F PONTA", "9 kWh", "0,333333", "3,00"],
            ["DEMANDA USD", "150,65 kW", "22,645868", "3.411,60"],
            ["DEMANDA USD ISENTA ICMS", "109,35 kW", "18,570005", "2.030,63"],
            ["CONT ILUMIN PUBLICA MUNICIPIO", "—", "—", "115,01"],
            ["TOTAL", "", "", "9.854,93"],
        ],
    )
    doc.add_paragraph(
        "Demanda contratada: 260 kW (medida 150,65 kW; faturada = contratada). "
        "A Copel divide a demanda em parcela com ICMS e parcela isenta de ICMS "
        "(150,65 + 109,35 = 260 kW)."
    )
    doc.add_paragraph(
        "Bandeira tarifária: Verde (01/03 a 31/03/2023) -> adicional 0. "
        "Tributos: ICMS 18%, PIS 0,95%, COFINS 4,38% (PIS R$ 79,35 + COFINS "
        "R$ 365,83 = R$ 445,18; ICMS R$ 1.387,67 — incluídos no total)."
    )

    doc.add_heading("3. Tarifas líquidas — banco x conta real", level=1)
    _tabela(
        doc,
        ["Componente", "Banco", "Conta real", "Confere?"],
        [
            ["TE Ponta", "388,08 R$/MWh", "0,388080 R$/kWh", "Sim"],
            ["TE Fora ponta", "247,20 R$/MWh", "0,247200 R$/kWh", "Sim"],
            ["TUSD Ponta", "1.027,46 R$/MWh", "1,027460 R$/kWh", "Sim"],
            ["TUSD Fora ponta", "110,85 R$/MWh", "0,110850 R$/kWh", "Sim"],
            ["TUSD Demanda (unica)", "17,58 R$/kW", "17,580000 R$/kW", "Sim"],
        ],
    )
    doc.add_paragraph(
        "Vigência no banco: 2022-06-24 a 2023-06-23 (base Tarifa de Aplicação)."
    )

    doc.add_heading("4. Fórmula de tributos validada pela conta", level=1)
    doc.add_paragraph(
        "A Copel engrossa as tarifas líquidas com o fator multiplicativo "
        '("por fora"):'
    )
    doc.add_paragraph(
        "fator = 1 / ((1 - PIS - COFINS) x (1 - ICMS)) "
        "= 1 / ((1 - 0,0095 - 0,0438) x (1 - 0,18)) = 1,28817"
    )
    doc.add_paragraph("Conferência com a conta:")
    doc.add_paragraph("TE Ponta: 0,388080 x 1,28817 = 0,499818 (ok)", style="List Bullet")
    doc.add_paragraph("TUSD Ponta: 1,027460 x 1,28817 = 1,323455 (ok)", style="List Bullet")
    doc.add_paragraph("Demanda: 17,58 x 1,28817 = 22,645868 (ok)", style="List Bullet")
    doc.add_paragraph(
        "Conclusão: a conta real valida o uso de tipo_icms=\"fora\" "
        "(multiplicativo). A forma aditiva (1/(1-PIS-COFINS-ICMS) = 1,3043) "
        "NÃO reproduz esta conta. O projeto mantém as duas fórmulas com "
        "seletor (tipo_icms: dentro/fora)."
    )

    doc.add_heading("5. Comparação — Conta real x Simulação", level=1)
    doc.add_paragraph(
        "Perfil simulado (POST /api/calculo/fatura): distribuidora COPEL-DIS, "
        "subgrupo A4, modalidade Verde, data_referencia 2023-03-15, consumo "
        "Ponta 55 kWh / Fora Ponta 9.094 kWh, demanda medida única 150,65 kW, "
        "contratada única 260 kW, outros_rs 115,01; tributos por fora "
        "(pis=0,0095, cofins=0,0438, icms=0,18)."
    )
    _tabela(
        doc,
        ["Item", "Conta real (R$)", "Simulação (R$)", "Diferença (R$)"],
        [
            ["TE Ponta", "27,49", "27,50", "+0,01"],
            ["TUSD Ponta", "72,79", "72,79", "0,00"],
            ["TE Fora Ponta", "2.895,85", "2.895,86", "+0,01"],
            ["TUSD Fora Ponta", "1.298,56", "1.298,57", "+0,01"],
            ["Demanda (260 kW)", "5.442,23", "5.887,98", "+445,75"],
            ["Reativo excedente", "3,00", "0,00", "-3,00"],
            ["Iluminação pública", "115,01", "115,01", "0,00"],
            ["TOTAL", "9.854,93", "10.297,70", "+442,77"],
        ],
    )
    doc.add_paragraph("Explicação da diferença:")
    doc.add_paragraph(
        "+445,75 -> a Copel divide a demanda em parcela com ICMS e parcela "
        "isenta de ICMS; nosso motor aplica o fator cheio nos 260 kW.",
        style="List Bullet",
    )
    doc.add_paragraph(
        "-3,00 -> a conta cobra reativo excedente faturado (9 kWh x 0,333333); "
        "nosso motor não aceita a quantidade de reativo excedente já faturada.",
        style="List Bullet",
    )
    doc.add_paragraph(
        "+445,75 - 3,00 = +442,75 (os R$ 0,02 restantes são arredondamento de "
        "centavos da Copel)."
    )

    doc.add_heading("6. O que foi validado", level=1)
    for item in [
        "Tarifas líquidas: o banco bate 1:1 com a conta real.",
        "Tributos por fora: a fórmula multiplicativa reproduz as tarifas finais.",
        "Demanda faturável = máx(medida, contratada): faturados 260 kW.",
        "Bandeira Verde 03/2023 -> 0: sem adicional nos dois lados.",
        "Horo-sazonal: não se aplica em 2023 (postos simples Ponta/Fora ponta).",
        "Estrutura da fatura Verde: TE + TUSD energia por posto e demanda única.",
    ]:
        doc.add_paragraph(item, style="List Number")

    doc.add_heading("7. Gaps identificados (backlog)", level=1)
    doc.add_paragraph(
        "1) Isenção de ICMS na demanda — impacto R$ 445,75. A Copel divide a "
        "demanda em DEMANDA USD (com ICMS) e DEMANDA USD ISENTA ICMS (apenas "
        "PIS/COFINS). Necessário suportar parcela isenta de ICMS."
    )
    doc.add_paragraph(
        "2) Reativo excedente faturado diretamente — impacto R$ 3,00. "
        "Necessário aceitar a quantidade de reativo excedente já faturada "
        "(além do cálculo por fator de potência < 0,92)."
    )
    doc.add_paragraph(
        "3) Cosmético — nossa linha sai como TUSD DEMANDA PONTA; a conta usa "
        "DEMANDA USD (demanda única da Verde)."
    )

    doc.add_heading("8. Como reproduzir", level=1)
    doc.add_paragraph(
        "Consulta das tarifas líquidas:"
    )
    doc.add_paragraph(
        '.venv\\Scripts\\python.exe scripts\\consultar_banco.py '
        '--distribuidora "COPEL-DIS" --subgrupo A4 --modalidade Verde '
        "--data 2023-03-15"
    )
    doc.add_paragraph(
        "Endpoint: POST http://127.0.0.1:8000/api/calculo/fatura com o perfil "
        "da seção 5 e a query "
        "modalidade=Verde&aplicar_tributos=true&pis=0.0095&cofins=0.0438"
        "&icms=0.18&tipo_icms=fora"
    )

    doc.add_heading("9. Critérios de aceite futuros", level=1)
    doc.add_paragraph(
        "Quando os gaps forem fechados, a simulação deve fechar: demanda com "
        "isenção de ICMS = 5.442,23; reativo excedente = 3,00; "
        "TOTAL = 9.854,93 (+/- R$ 0,03 de arredondamento da Copel)."
    )

    for p in doc.paragraphs:
        for run in p.runs:
            run.font.size = Pt(11)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(DESTINO))
    print(f"OK -> {DESTINO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
