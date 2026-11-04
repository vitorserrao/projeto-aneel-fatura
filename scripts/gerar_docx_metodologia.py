# -*- coding: utf-8 -*-
"""Gera docs/eficiencia/metodologia_eficiencia_energetica.docx a partir da
metodologia de análise de eficiência energética (PGEN 2025).

Uso: .venv/Scripts/python.exe scripts/gerar_docx_metodologia.py
"""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "eficiencia" / "metodologia_eficiencia_energetica.docx"

# ---------------------------------------------------------------------------
# Dados dos campi
# ---------------------------------------------------------------------------
CAMPUSES = [
    dict(
        n="1", ifs="IFAM", campus="Presidente Figueiredo", cidade="Presidente Figueiredo/AM",
        regiao="Equatorial", geracao="Sim — problema no inversor", obs="(preencher)",
        quente="Set–Out", dia_quente="16/10/2025 (qui)", criterio_quente="Mês mais quente da normal",
        frio="Abr–Jun", dia_frio="21/05/2025 (qua)", criterio_frio="Menores médias/mínimas",
    ),
    dict(
        n="2", ifs="IFAP", campus="Macapá", cidade="Macapá/AP",
        regiao="Equatorial", geracao="Sim — usina fotovoltaica", obs="(preencher)",
        quente="Set–Nov", dia_quente="23/10/2025 (qui)", criterio_quente="Mês mais quente da normal",
        frio="Fev–Mar", dia_frio="20/02/2025 (qui)", criterio_frio="Menores médias; mínimas em jul",
    ),
    dict(
        n="3", ifs="IFRO", campus="Guajará-Mirim", cidade="Guajará-Mirim/RO",
        regiao="Tropical", geracao="(verificar no PGEN)", obs="(preencher)",
        quente="Ago–Out", dia_quente="18/09/2025 (qui)", criterio_quente="Mês mais quente da normal",
        frio="Jun–Jul", dia_frio="10/07/2025 (qui)", criterio_frio="Menores médias; friagem",
    ),
    dict(
        n="4", ifs="IFMG", campus="Bambuí", cidade="Bambuí/MG",
        regiao="Tropical de altitude", geracao="(verificar no PGEN)", obs="Poucos detalhes disponíveis",
        quente="Jan–Fev", dia_quente="23/01/2025 (qui)", criterio_quente="Mês mais quente da normal",
        frio="Jun–Jul", dia_frio="24/07/2025 (qui)", criterio_frio="Mês mais frio da normal",
    ),
    dict(
        n="5", ifs="IFSC", campus="Canoinhas", cidade="Canoinhas/SC",
        regiao="Subtropical", geracao="(verificar no PGEN)", obs="(preencher)",
        quente="Jan–Fev", dia_quente="23/01/2025 (qui)", criterio_quente="Mês mais quente da normal",
        frio="Jun–Jul", dia_frio="24/07/2025 (qui)", criterio_frio="Mês mais frio da normal",
    ),
    dict(
        n="6", ifs="IFSul", campus="Santana do Livramento", cidade="Santana do Livramento/RS",
        regiao="Subtropical", geracao="(verificar no PGEN)", obs="(preencher)",
        quente="Jan–Fev", dia_quente="23/01/2025 (qui)", criterio_quente="Mês mais quente da normal",
        frio="Jun–Jul", dia_frio="24/07/2025 (qui)", criterio_frio="Mês mais frio da normal",
    ),
    dict(
        n="7", ifs="IFC", campus="Concórdia", cidade="Concórdia/SC",
        regiao="Subtropical", geracao="(verificar no PGEN)", obs="(preencher)",
        quente="Jan–Fev", dia_quente="23/01/2025 (qui)", criterio_quente="Mês mais quente da normal",
        frio="Jun–Jul", dia_frio="24/07/2025 (qui)", criterio_frio="Mês mais frio da normal",
    ),
]


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        run = p.add_run(h)
        run.bold = True
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)
    return table


def bullets(doc, items):
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def numbered(doc, items):
    for item in items:
        doc.add_paragraph(item, style="List Number")


def build():
    doc = Document()

    # Metadados e estilos básicos
    doc.core_properties.title = "Metodologia — Análise de Eficiência Energética em Campi da Rede Federal (PGEN 2025)"
    doc.core_properties.author = "Gestão e Eficiência Energética"
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)

    # Título
    title = doc.add_heading("Metodologia — Análise de Eficiência Energética em Campi da Rede Federal (PGEN 2025)", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sub.add_run(
        "Trabalho da disciplina de Gestão e Eficiência Energética — documento de estrutura e roteiro de análise. "
        "Os dados serão extraídos do PGEN em etapa posterior; este template deixa os campos prontos para preenchimento."
    )
    run.italic = True

    # 1. Objetivo
    doc.add_heading("1. Objetivo", level=1)
    doc.add_paragraph(
        "Analisar o perfil de consumo de energia e as características de cada campus, com base nos dados "
        "disponíveis no PGEN (pgen.app), e produzir:"
    )
    bullets(doc, [
        "um diagnóstico do perfil de consumo e dos dados;",
        "um comparativo verão × inverno (com dias de referência);",
        "propostas de melhoria na ótica de gestão de energia (ex.: excesso de reativos, picos, consumo fora de horário, geração fotovoltaica ociosa).",
    ])
    doc.add_paragraph(
        "Premissa central: não é necessário calcular nada manualmente — o PGEN já fornece visão anual, mensal e "
        "diária, potência média, demanda de pico, consumo por período do dia, reativos/fator de potência e geração "
        "fotovoltaica. O trabalho é de leitura, organização e interpretação desses dados."
    )

    # 2. Escopo
    doc.add_heading("2. Escopo", level=1)
    bullets(doc, [
        "Período de análise: ano de 2025 (visão anual + visão mensal + dias de referência).",
        "Fonte de dados: PGEN — Portal de Gerenciamento de Energia (https://pgen.app).",
    ])
    doc.add_paragraph("Campi analisados (7):")
    add_table(
        doc,
        ["#", "Instituição", "Campus", "Cidade/UF", "Observação inicial"],
        [
            [c["n"], c["ifs"], c["campus"], c["cidade"], c["obs"]]
            for c in CAMPUSES
        ],
    )
    doc.add_paragraph(
        "O que NÃO faz parte desta etapa: cálculos manuais de potência/energia e a extração automatizada dos dados "
        "(será feita depois). Os valores serão lidos diretamente do PGEN."
    )

    # 3. Seções do trabalho
    doc.add_heading("3. Seções do trabalho (estrutura da análise)", level=1)
    doc.add_paragraph(
        "O trabalho/apresentação será organizado em 6 seções. Para cada uma, o template por campus (seção 6 deste "
        "documento) traz as tabelas prontas."
    )

    doc.add_heading("3.1 Caracterização do campus", level=2)
    bullets(doc, [
        "Localização (cidade, UF) e região climática (equatorial, tropical, subtropical).",
        "Número de alunos e servidores.",
        "Metragem/área construída do campus (m²).",
        "Horários de aula e turnos de funcionamento (manhã, tarde, noite; dias da semana).",
        "Presença de geração fotovoltaica e sua condição (ex.: IFAM com problema no inversor; IFAP com usina ativa).",
        "Outras cargas relevantes: laboratórios, refeitório, biblioteca, ar-condicionado, iluminação externa, bombas.",
    ])

    doc.add_heading("3.2 Análise do perfil de consumo (dados PGEN)", level=2)
    bullets(doc, [
        "Visão anual 2025: consumo total (kWh), potência média anual (kW), tendência ao longo do ano.",
        "Visão mensal 2025: meses de maior e menor consumo; relação com calendário acadêmico (férias, recesso) e clima.",
        "Curvas diárias: formato da curva, potência média do dia, demanda de pico e horário em que ocorre, consumo por período do dia (madrugada, manhã, tarde, noite).",
        "Reativos / fator de potência: nível de energia reativa excedente mostrado no PGEN; presença de cobrança/multa potencial.",
        "Geração fotovoltaica: quando houver, geração diária/mensal, excedente e percentual da carga atendida.",
    ])

    doc.add_heading("3.3 Análise verão × inverno (dias de referência)", level=2)
    numbered(doc, [
        "Para cada campus, identificar o período mais quente e o período mais frio de 2025, usando dados climáticos da cidade (INMET/normais climatológicas).",
        "Escolher 1 dia útil de referência dentro de cada período (preferência: terça a quinta, sem feriado ou evento atípico).",
        "Validar o dia escolhido na curva do PGEN (dia com dados completos e representativo do período).",
        "Comparar os dois dias e os dois períodos.",
    ])
    bullets(doc, [
        "Potência média (kW) e consumo do dia (kWh).",
        "Demanda de pico e horário do pico.",
        "Consumo por período do dia (madrugada/manhã/tarde/noite).",
        "Reativos e fator de potência.",
        "Influência do ar-condicionado (verão) e da iluminação/calefação conforme a região.",
    ])

    doc.add_heading("3.3.1 Pré-seleção por clima (períodos e dias de referência)", level=3)
    doc.add_paragraph(
        "Pré-seleção feita com base nas normais climatológicas das cidades (INMET/climate-data/WeatherSpark). "
        "Os dias devem ser validados na curva do PGEN antes da análise final."
    )
    add_table(
        doc,
        ["Campus", "Período mais quente (clima)", "Dia quente pré-selecionado", "Período mais frio (clima)", "Dia frio pré-selecionado"],
        [
            [f"{c['ifs']} {c['campus']}", c["quente"], c["dia_quente"], c["frio"], c["dia_frio"]]
            for c in CAMPUSES
        ],
    )
    bullets(doc, [
        "Para os campi da Amazônia (IFAM, IFAP, IFRO), o “período mais frio” é o de menores temperaturas médias/mínimas — a amplitude é pequena; a comparação deve focar na diferença das mínimas e no efeito da chuva/nebulosidade.",
        "Em 2025 o período pode deslocar-se em relação à normal; a confirmação final é feita pela curva do PGEN (dias de maior/menor consumo e temperatura local).",
        "Dias escolhidos entre terça e quinta, sem feriados nacionais.",
    ])

    doc.add_heading("3.4 Diagnóstico do perfil e dos dados", level=2)
    doc.add_paragraph("Checklist de diagnóstico a aplicar em cada campus:")
    bullets(doc, [
        "Picos elevados em horário específico? (tarifação e demanda)",
        "Consumo relevante na madrugada? (iluminação externa, standby, equipamentos ligados)",
        "Reativos altos / fator de potência baixo? (multa e perdas)",
        "Consumo alto em dias não letivos? (falta de desligamento programado)",
        "Consumo acima do teto do PGEN? (alerta do próprio portal)",
        "Geração fotovoltaica ausente/ociosa? (inversor, sujeira, sombreamento)",
        "Diferença verão × inverno coerente com o clima e com a carga de ar-condicionado?",
    ])
    doc.add_paragraph(
        "Possíveis motivos (hipóteses a confirmar com os dados): ar-condicionado no verão; iluminação externa ligada "
        "a noite toda; equipamentos em standby; baixo fator de potência (excesso de reativos); retorno às aulas "
        "(comparar com recesso); falha em inversor (IFAM); usina fotovoltaica gerando abaixo do esperado."
    )

    doc.add_heading("3.5 Melhorias na ótica de gestão de energia", level=2)
    doc.add_paragraph("Vincular cada problema identificado a uma ação concreta:")
    add_table(
        doc,
        ["Problema identificado", "Melhoria proposta", "Impacto esperado"],
        [
            ["Muitos reativos / FP baixo", "Correção de fator de potência (banco de capacitores)", "Elimina multa por reativo excedente e reduz perdas"],
            ["Pico elevado em horário de ponta", "Deslocamento de cargas, gerenciamento de demanda, escala de horários", "Reduz demanda faturada e custo"],
            ["Consumo alto na madrugada", "Automação/desligamento de iluminação externa e standby", "Reduz consumo fora de uso"],
            ["Consumo alto no verão", "Ar-condicionado eficiente, manutenção, setpoint adequado, proteção solar", "Reduz consumo e pico no calor"],
            ["Geração FV ociosa/indisponível", "Conserto do inversor (IFAM), limpeza, monitoramento", "Aumenta autogeração e reduz fatura"],
            ["Sem acompanhamento gerencial", "Rotina de acompanhamento no PGEN, metas, comissão de energia, práticas ISO 50001", "Gestão contínua da energia"],
        ],
    )

    doc.add_heading("3.6 Conclusão e plano de gestão", level=2)
    bullets(doc, [
        "Síntese por campus (1 parágrafo + prioridade).",
        "Tabela consolidada comparando os 7 campi.",
        "Próximos passos: monitoramento mensal no PGEN, priorização das ações de maior impacto e revisão após implementação.",
    ])

    # 4. Roteiro de coleta no PGEN
    doc.add_heading("4. Roteiro de coleta no PGEN (passo a passo)", level=1)
    numbered(doc, [
        "Acessar https://pgen.app e aguardar a verificação de segurança.",
        "Na tela de filtros, selecionar: Tipo de Instituição: Instituto Federal; IF: a instituição desejada (IFAM, IFAP, IFRO, IFMG, IFSC, IFSul, IFC); Campus: o campus da análise; Bloco/Prédio: quando disponível, para análise por unidade.",
        "Navegar pelas abas do portal: Histórico (curvas diárias de consumo e potência — usar para os dias de referência verão/inverno); Mensal (consumo mensal de 2025 e comparação com o teto); Supervisão (visão em tempo real, potência atual, pico do dia e geração FV); Comparativo (comparar períodos verão × inverno lado a lado).",
        "Registrar para cada campus: consumo anual 2025 e consumo mensal (12 valores); potência média, demanda de pico + horário, consumo por período; reativos/fator de potência; geração fotovoltaica (se houver); print das curvas dos dias de referência.",
        "Preencher as tabelas da seção 6 deste documento.",
    ])

    # 5. Guia de leitura dos indicadores
    doc.add_heading("5. Guia de leitura dos indicadores do PGEN", level=1)
    add_table(
        doc,
        ["Indicador", "O que mostra", "Como interpretar"],
        [
            ["Potência média (kW)", "Carga média no período", "Base do perfil; comparar entre campus e entre estações"],
            ["Demanda de pico (kW) + horário", "Maior potência e quando ocorre", "Indica o que pressiona a conta e o sistema"],
            ["Consumo por período (madrugada/manhã/tarde/noite)", "Distribuição da carga no dia", "Madrugada alta = iluminação/standby; tarde alta = ar-condicionado"],
            ["Consumo mensal (kWh)", "Energia consumida no mês", "Ver sazonalidade e efeito do calendário acadêmico"],
            ["Teto de consumo", "Limite de referência do PGEN", "Consumo acima do teto = alerta de desperdício"],
            ["Reativos / fator de potência", "Energia reativa e qualidade", "Reativo excedente alto = multa e perdas; exige correção"],
            ["Geração fotovoltaica", "Energia gerada pela usina", "Gerar abaixo do esperado = inversor, sujeira ou sombreamento"],
        ],
    )
    doc.add_paragraph("Dicas verão × inverno (o que olhar):")
    bullets(doc, [
        "No verão, esperar pico à tarde (ar-condicionado) e consumo maior que a média anual.",
        "No inverno, esperar pico pela manhã/noite (iluminação) e, em regiões frias, possível uso de aquecimento.",
        "Comparar a potência média e o horário do pico entre as estações, não só o consumo total.",
        "Verificar se os reativos mudam com a estação (cargas de ar-condicionado alteram o fator de potência).",
    ])

    # 6. Template por campus
    doc.add_heading("6. Template por campus", level=1)
    for c in CAMPUSES:
        doc.add_heading(f"Campus {c['n']} — {c['ifs']} {c['campus']} ({c['cidade'].split('/')[-1]})", level=2)

        doc.add_heading("A. Caracterização", level=3)
        add_table(
            doc,
            ["Campo", "Valor"],
            [
                ["Cidade/UF", c["cidade"]],
                ["Região climática", c["regiao"]],
                ["Nº de alunos", "(preencher)"],
                ["Área construída (m²)", "(preencher)"],
                ["Horários de aula", "(preencher)"],
                ["Geração fotovoltaica", c["geracao"]],
                ["Observações", c["obs"]],
            ],
        )

        doc.add_heading("B. Dados PGEN 2025", level=3)
        add_table(
            doc,
            ["Campo", "Valor"],
            [
                ["Consumo anual (kWh)", "(preencher)"],
                ["Potência média anual (kW)", "(preencher)"],
                ["Mês de maior consumo", "(preencher)"],
                ["Mês de menor consumo", "(preencher)"],
                ["Demanda de pico (kW) + horário", "(preencher)"],
                ["Reativos / fator de potência", "(preencher)"],
                ["Geração FV anual (kWh)", "(preencher)"],
            ],
        )

        doc.add_heading("C. Dias de referência verão × inverno", level=3)
        add_table(
            doc,
            ["Campo", "Período quente", "Período frio"],
            [
                ["Período identificado (meses)", c["quente"], c["frio"]],
                ["Dia de referência escolhido", c["dia_quente"], c["dia_frio"]],
                ["Critério/justificativa", c["criterio_quente"], c["criterio_frio"]],
                ["Potência média do dia (kW)", "(preencher)", "(preencher)"],
                ["Pico (kW) + horário", "(preencher)", "(preencher)"],
                ["Consumo por período", "(preencher)", "(preencher)"],
                ["Reativos/FP", "(preencher)", "(preencher)"],
            ],
        )

        doc.add_heading("D. Diagnóstico", level=3)
        doc.add_paragraph("(preencher: picos, reativos, madrugada, geração FV, causas prováveis)")
        doc.add_heading("E. Melhorias propostas", level=3)
        doc.add_paragraph("(preencher: ação, impacto esperado)")

    # 7. Tabela consolidada
    doc.add_heading("7. Tabela consolidada — comparativo dos 7 campi", level=1)
    add_table(
        doc,
        ["Campus", "Consumo anual 2025 (kWh)", "Potência média (kW)", "Pico (kW)", "FP/Reativos", "Verão × Inverno (destaque)", "Melhoria prioritária"],
        [
            [f"{c['ifs']} {c['campus']}", "(preencher)", "(preencher)", "(preencher)", "(preencher)", "(preencher)", "(preencher)"]
            for c in CAMPUSES
        ],
    )

    # 8. Referências
    doc.add_heading("8. Referências e fontes de apoio", level=1)
    bullets(doc, [
        "PGEN — Portal de Gerenciamento de Energia: https://pgen.app",
        "PGEN/labsSmart (IFSC): https://pgen.labsmart.ifsc.edu.br",
        "INMET — dados meteorológicos para definição dos períodos quente/frio por cidade.",
        "Normais climatológicas consultadas via climate-data.org, WeatherSpark e Climatempo (períodos 1991–2020/2021).",
        "ABNT NBR ISO 50001 — Sistemas de gestão de energia.",
    ])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"OK -> {OUT}")


if __name__ == "__main__":
    build()
