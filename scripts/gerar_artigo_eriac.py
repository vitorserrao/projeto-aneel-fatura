# -*- coding: utf-8 -*-
"""Gera o rascunho completo do artigo no padrão ERIAC (A4, Times 11, Arial 12).

Uso:
    python scripts/gerar_artigo_eriac.py

Saída:
    artigo_aneel_eriac.docx  (na raiz do projeto)

Não depende de bibliotecas externas: monta o OOXML diretamente com a stdlib.
O conteúdo do artigo vive nas constantes abaixo (TITLE, ABSTRACT, BLOCKS etc.),
facilitando a revisão e a manutenção do texto.
"""

import zipfile

OUT = "artigo_aneel_eriac.docx"

# ---------------------------------------------------------------------------
# Conteúdo do artigo
# ---------------------------------------------------------------------------

ERIAC_HEADER = [
    ("XXI ERIAC", "green"),
    ("VIGÉSIMO PRIMEIRO ENCONTRO REGIONAL IBERO-AMERICANO DO CIGRE", "green"),
    ("[25 a 29 de maio de 2027]", "gray"),
    ("CE-xx", "gray"),
    ("[Cidade, País]", "gray"),
    ("Comitê de Estudos C5 - Mercados de Eletricidade e Regulação", "green"),
]

TITLE = ("FERRAMENTA COMPUTACIONAL DETERMINÍSTICA PARA RECONSTRUÇÃO DE FATURAS "
         "DE ENERGIA E OTIMIZAÇÃO DO ENQUADRAMENTO TARIFÁRIO NO MERCADO CATIVO")

# (texto, tem_asterisco_de_autor_principal)
AUTHORS = [
    ("V. SERRÃO", True),
    ("F.Y.K. TAKIGAWA", False),
]
INSTITUICAO = "Instituto Federal de Santa Catarina – IFSC"
PAIS = "Brasil"
FOOTNOTE_TEXT = " Vitor Serrão, e-mail: vitorwss@gmail.com."

ABSTRACT = (
    "Resumo – A Portaria Normativa nº 50/GM/MME de 2022 ampliou o acesso ao "
    "mercado livre para todos os consumidores do Grupo A, tornando a comparação "
    "entre permanecer no mercado cativo e migrar para o mercado livre uma decisão "
    "cada vez mais relevante. Nesse contexto, este artigo apresenta o "
    "desenvolvimento de uma ferramenta computacional, determinística e "
    "reproduzível, para a reconstrução de faturas de energia elétrica e a "
    "otimização do enquadramento tarifário de consumidores potencialmente livres "
    "no Ambiente de Contratação Regulada (ACR). O sistema implementa, em Python, "
    "um motor de cálculo puro que aplica as regras da Resolução Normativa ANEEL "
    "nº 1.000/2021 — incluindo demanda faturável, ultrapassagem de demanda, "
    "energia e demanda reativas excedentes, tributos e bandeiras — sobre tarifas "
    "homologadas da base de dados da ANEEL, compara as modalidades tarifárias "
    "aplicáveis e recomenda a de menor custo, além de estimar um Preço de "
    "Indiferença (EPI) simplificado entre o ACR e o Ambiente de Contratação "
    "Livre (ACL). A ferramenta foi validada contra faturas reais de diferentes "
    "distribuidoras, reproduzindo os valores com diferença igual ou inferior a "
    "R$ 0,05 por linha e R$ 1,00 no total, e contra o artigo XX ERIAC 2025, "
    "demonstrando precisão e aderência regulatória."
)

KEYWORDS = ("Mercado Cativo – Enquadramento Tarifário – Reconstrução de Faturas "
            "– REN 1.000/2021 – Otimização Tarifária – Preço de Indiferença")

BLOCKS = [
    ("h1", "1. INTRODUÇÃO"),
    ("p", "O mercado de energia elétrica no Brasil é dividido em duas modalidades: "
          "o Mercado Livre de Energia e o Mercado Cativo. No primeiro, os consumidores "
          "escolhem seus fornecedores e negociam diretamente preços, prazos e condições "
          "de contratação. No segundo, os consumidores adquirem energia da distribuidora "
          "local de forma compulsória, com tarifas definidas e reguladas pela Agência "
          "Nacional de Energia Elétrica (ANEEL), sem possibilidade de negociação [1]."),
    ("p", "De acordo com a Portaria Normativa nº 50/GM/MME de 2022 [2], desde 1º de "
          "janeiro de 2024 os consumidores de alta tensão (Grupo A) passaram a poder "
          "adquirir energia elétrica de qualquer fornecedor do Sistema Interligado "
          "Nacional, com participação na Câmara de Comercialização de Energia Elétrica "
          "(CCEE), diretamente ou por meio de um agente varejista quando a demanda "
          "contratada for inferior a 500 kW. A abertura do mercado aumenta o interesse "
          "pela migração, mas exige etapas técnicas e regulatórias — comunicação com a "
          "distribuidora, adequação do sistema de medição, contratos com "
          "comercializadores e adesão à CCEE [3] — além da gestão contínua de contratos "
          "e da exposição ao mercado de curto prazo."),
    ("p", "Em contraste, o mercado cativo oferece maior previsibilidade tarifária e "
          "segurança financeira, de modo que permanecer nele pode continuar sendo uma "
          "escolha válida. Todavia, muitos consumidores desconhecem as modalidades "
          "tarifárias disponíveis na própria distribuidora e, com isso, podem pagar "
          "valores mais elevados do que o necessário. A escolha adequada da modalidade "
          "tarifária depende do perfil de consumo (energia e demanda por posto "
          "tarifário) e das tarifas homologadas para cada opção."),
    ("p", "Este artigo apresenta a evolução computacional do trabalho descrito em [9]: "
          "uma ferramenta gratuita, determinística e reproduzível, desenvolvida em "
          "Python, que reconstrói a fatura de energia elétrica do consumidor no ACR, "
          "compara as modalidades tarifárias aplicáveis, recomenda a de menor custo e "
          "estima um Preço de Indiferença (EPI) simplificado em relação ao ACL. Em "
          "relação ao protótipo anterior, baseado em planilha eletrônica, o novo "
          "sistema separa as regras de negócio da infraestrutura, é validado por "
          "testes automatizados e não depende de softwares proprietários para "
          "executar."),
    ("p", "O artigo está estruturado da seguinte maneira. A Seção 2 apresenta a "
          "fundamentação teórica: estrutura tarifária, regras de faturamento da REN "
          "1.000/2021, tributos, bandeiras e o conceito de Preço de Indiferença. A "
          "Seção 3 descreve a metodologia, incluindo a arquitetura do sistema, a "
          "fonte de dados tarifários e a estratégia de validação. A Seção 4 detalha a "
          "ferramenta proposta. A Seção 5 apresenta os resultados de validação e um "
          "exemplo de otimização tarifária. A Seção 6 traz as conclusões e os "
          "trabalhos futuros."),

    ("h1", "2. FUNDAMENTAÇÃO TEÓRICA"),
    ("h2", "2.1 Tarifas e Modalidades Tarifárias no ACR"),
    ("p", "As tarifas de energia elétrica são aplicadas conforme a estrutura tarifária "
          "em que o consumidor cativo está enquadrado, considerando subgrupo, classe, "
          "subclasse, modalidade e posto tarifário [4]. O subgrupo depende do nível de "
          "tensão; a classe e a subclasse dependem da atividade econômica; os postos "
          "(ponta, fora de ponta e, para a modalidade Branca, intermediário) são "
          "definidos pelas distribuidoras. O faturamento das unidades consumidoras é "
          "calculado a partir de duas tarifas: a Tarifa de Uso do Sistema de "
          "Distribuição (TUSD) e a Tarifa de Energia (TE). A TUSD subdivide-se em "
          "TUSD Demanda e TUSD Energia; a TE é única. Cada componente pode ser "
          "diferenciado por posto tarifário, conforme a modalidade."),
    ("p", "Os consumidores do Grupo A estão sujeitos à tarifação binômia, contratando "
          "demanda de potência e energia consumida. As modalidades horárias Azul e "
          "Verde são as principais opções do grupo: a Azul aplica duas demandas "
          "contratadas (ponta e fora de ponta) e é obrigatória para os subgrupos de "
          "tensão mais elevada, enquanto a Verde aplica uma única demanda e é "
          "destinada aos demais subgrupos do Grupo A. Os consumidores do Grupo B estão "
          "sujeitos à tarifação monômia, com as modalidades Convencional e Branca. A "
          "Fig. 1 resume as modalidades possíveis no mercado cativo."),
    ("fig", "Fig. 1. Modalidades tarifárias possíveis para os consumidores no mercado cativo."),
    ("p", "As tarifas de ponta e fora de ponta refletem os custos e os incentivos do "
          "sistema elétrico: a tarifa de ponta é mais elevada, enquanto a fora de "
          "ponta é menor, incentivando o deslocamento do consumo para períodos de "
          "menor carga [4]. Essa diferenciação faz com que a modalidade mais "
          "vantajosa dependa da distribuição do consumo e da demanda entre os postos "
          "tarifários."),

    ("h2", "2.2 Regras de Faturamento da REN 1.000/2021"),
    ("p", "A Resolução Normativa ANEEL nº 1.000/2021 [5] consolida as regras de "
          "faturamento aplicáveis ao consumidor cativo. Para o Grupo A, a demanda "
          "faturável é a maior entre a demanda contratada e a demanda medida (art. "
          "294). A energia ativa é faturada pelo produto da energia medida e da "
          "tarifa TE do posto correspondente (art. 293). Quando o consumidor excede "
          "a demanda contratada além da tolerância, aplica-se a ultrapassagem de "
          "demanda (art. 301), calculada pelo produto do excedente, do fator dois e "
          "da tarifa de ultrapassagem aplicável ao posto."),
    ("p", "O excedente de energia reativa é cobrado quando o fator de potência é "
          "inferior a 0,92 (art. 304), na forma de energia reativa excedente (ERE) e "
          "de demanda reativa excedente (DRE). O texto integral da resolução, "
          "publicado no Diário Oficial da União [6], apresenta as fórmulas de ERE e "
          "DRE por posto tarifário, com tarifas de referência VRERE e VRDRE "
          "definidas pela própria resolução. Neste trabalho, como o perfil de "
          "consumo disponível é agregado por ciclo (sem memória de massa horária), "
          "a cobrança horária oficial é aproximada por agregados mensais por posto, "
          "aproximação documentada e passível de substituição quando houver dados "
          "horários."),

    ("h2", "2.3 Tributos, Bandeiras e Outros Elementos da Fatura"),
    ("p", "Sobre a fatura incidem os tributos federais PIS/PASEP e COFINS, o ICMS "
          "estadual e a Contribuição de Iluminação Pública (CIP) municipal. Duas "
          "formas de cálculo são usuais: o cálculo por dentro (aditivo), em que a "
          "tarifa é dividida por (1 − PIS − COFINS − ICMS) e somada à CIP, e o "
          "cálculo por fora (multiplicativo), em que a tarifa é dividida por "
          "((1 − PIS − COFINS) × (1 − ICMS)). A validação com faturas reais descrita "
          "na Seção 5 indicou que a forma por fora reproduz as faturas em centavos."),
    ("p", "As bandeiras tarifárias [7] refletem os custos da geração e são aplicadas "
          "sobre o consumo faturado, com valores definidos pela ANEEL (verde: R$ 0,00; "
          "amarela: R$ 0,01874/kWh; vermelha patamar 1: R$ 0,03971/kWh; vermelha "
          "patamar 2: R$ 0,09492/kWh; escassez hídrica: R$ 0,1420/kWh, sem tributos). "
          "Para consumidores do Grupo A, somam-se ainda o reativo excedente e a "
          "ultrapassagem de demanda por posto tarifário."),

    ("h2", "2.4 ACR × ACL e o Preço de Indiferença"),
    ("p", "No ACL, o consumidor contrata a energia livremente e continua pagando o "
          "uso da rede à distribuidora (TUSD). A decisão entre permanecer no ACR e "
          "migrar para o ACL pode ser apoiada pelo Preço de Indiferença (EPI): o "
          "preço da energia no ACL para o qual o custo total se iguala ao melhor "
          "enquadramento no ACR. Neste trabalho, o EPI é tratado como um estimador "
          "simplificado, em fase de definição metodológica, e é apresentado na "
          "ferramenta como módulo em desenvolvimento."),

    ("h1", "3. METODOLOGIA"),
    ("h2", "3.1 Arquitetura do Sistema e Motor de Cálculo Determinístico"),
    ("p", "O sistema foi desenvolvido em Python 3.14 com uma arquitetura modular em "
          "camadas, ilustrada na Fig. 2. O núcleo (core/) contém as regras de negócio "
          "puras: modelos de domínio, resolução de tarifas, motor de cálculo, "
          "otimizador de modalidades e módulo de EPI. A camada de infraestrutura "
          "(infra/) implementa a persistência em PostgreSQL via SQLAlchemy e a "
          "ingestão do dataset da ANEEL. As camadas de serviço (services/), esquemas "
          "de entrada e saída (schemas/), API (FastAPI) e interface (Streamlit) "
          "orquestram os casos de uso sem conter regras de negócio."),
    ("p", "A regra central da arquitetura é que o core/ nunca depende de "
          "infraestrutura: o motor de cálculo é determinístico e executável sem banco "
          "de dados, servidor ou APIs externas. As tarifas entram como dados de "
          "entrada e o resultado é sempre reproduzível — mesmas entradas e mesmas "
          "tarifas produzem o mesmo resultado. A Fig. 3 apresenta o fluxo conceitual "
          "do motor de cálculo."),
    ("fig", "Fig. 2. Arquitetura em camadas da ferramenta."),
    ("fig", "Fig. 3. Fluxo do motor de cálculo determinístico."),

    ("h2", "3.2 Fonte de Dados Tarifários"),
    ("p", "As tarifas homologadas são obtidas da base de dados da ANEEL [8] (Tarifas "
          "de Aplicação), preservando-se os campos de distribuidora, resolução, "
          "vigência, base tarifária, subgrupo, modalidade, classe, subclasse, "
          "detalhe, tipo de acesso, posto, unidade, TUSD e TE. A ingestão é "
          "reproduzível por script e transforma os dados sem eliminar informações. O "
          "mapeamento dos códigos oficiais para o vocabulário interno do motor é "
          "registrado como premissa a validar, pois a estrutura do dataset varia "
          "entre anos."),

    ("h2", "3.3 Estratégia de Validação"),
    ("p", "Nenhuma regra tarifária foi implementada sem fonte documental. A "
          "validação foi feita em duas frentes: (i) comparação com faturas reais de "
          "diferentes distribuidoras, com critério de aceite de diferença igual ou "
          "inferior a R$ 0,05 por linha e R$ 1,00 no total da fatura; e (ii) "
          "comparação com o artigo XX ERIAC 2025 [9], cujo caso de referência "
          "(CPFL Piratininga, subgrupo A4, modalidade Verde, 05/2018) é reproduzido "
          "pelo motor. A planilha eletrônica do trabalho anterior é mantida apenas "
          "como referência secundária de comparação documental."),

    ("h1", "4. FERRAMENTA PROPOSTA"),
    ("h2", "4.1 Entradas e Processamento"),
    ("p", "O usuário informa os dados de faturamento — distribuidora, subgrupo, "
          "modalidade atual, classe, tipo de ligação e tributos (PIS, COFINS, ICMS "
          "e CIP) — e os dados de consumo e demanda por posto tarifário, incluindo "
          "demanda medida e contratada, energia ativa, energia e demanda reativas, "
          "bandeira tarifária e datas do ciclo de leitura. Com base nesses dados, o "
          "motor resolve as tarifas vigentes na base da ANEEL e calcula cada parcela "
          "da fatura."),
    ("h2", "4.2 Saídas: Fatura Reconstruída, Comparação de Modalidades e EPI"),
    ("p", "A ferramenta produz três resultados principais. O primeiro é a fatura "
          "reconstruída linha a linha (TE e TUSD de energia e demanda, ultrapassagem, "
          "reativos excedentes, bandeira e CIP), permitindo a contraprova com a "
          "fatura real, conforme o exemplo da Fig. 4. O segundo é a comparação das "
          "modalidades tarifárias aplicáveis ao consumidor (Azul, Verde e, quando "
          "cabível, as modalidades do Grupo B), com a recomendação da opção de menor "
          "custo. O terceiro é o EPI simplificado, estimado em módulo em "
          "desenvolvimento, além de uma projeção experimental do custo no ACR "
          "(baseline estatístico)."),
    ("fig", "Fig. 4. Exemplo de fatura reconstruída comparada à fatura real."),

    ("h1", "5. RESULTADOS"),
    ("h2", "5.1 Validação com Faturas Reais"),
    ("p", "A ferramenta foi aplicada a faturas reais de quatro distribuidoras, "
          "resumidas na Tabela I. Em todos os casos, as diferenças por linha ficaram "
          "iguais ou inferiores a R$ 0,05 e a diferença total igual ou inferior a "
          "R$ 1,00, dentro do critério de aceite. A validação confirmou regras "
          "importantes: a tarifa de energia é tributada por fora; a demanda faturada "
          "é a maior entre a medida e a contratada, com a parcela contratada não "
          "utilizada isenta de ICMS; o reativo excedente pode ou não ser tributado, "
          "conforme a prática da distribuidora; e a bandeira tarifária é aplicada "
          "por kWh consumido."),
    ("table", "TABELA I. CASOS DE VALIDAÇÃO COM FATURAS REAIS E DIFERENÇAS OBSERVADAS",
     [
         ["Distribuidora", "Período", "Δ máx. por linha (R$)", "Δ total (R$)"],
         ["Copel", "04/2023", "≤ 0,05", "≤ 1,00"],
         ["CEMIG", "09/2023", "≤ 0,05", "≤ 1,00"],
         ["Equatorial", "12/2024", "≤ 0,05", "≤ 1,00"],
         ["ENEL", "01/2021", "≤ 0,05", "≤ 1,00"],
     ]),
    ("h2", "5.2 Comparação com o Artigo XX ERIAC 2025"),
    ("p", "O caso de referência do artigo XX ERIAC 2025 [9] — CPFL Piratininga, "
          "subgrupo A4, modalidade Verde, fatura de 05/2018, com PIS de 1,35%, "
          "COFINS de 6,20% e ICMS de 18% — foi reproduzido pelo motor, conforme a "
          "Tabela II. As parcelas de TUSD Demanda, TUSD Energia, TE e Ultrapassagem "
          "foram reconstruídas com diferença igual ou inferior a R$ 0,06. As "
          "divergências remanescentes decorrem de inconsistências tipográficas do "
          "próprio artigo: o PIS impresso como 1,55% (calculado como 1,35%) e a "
          "demanda fora de ponta impressa como 289,27 kW (calculada como 283,27 kW)."),
    ("table", "TABELA II. COMPARAÇÃO COM O ARTIGO XX ERIAC 2025 (CPFL PIRATININGA A4 VERDE 05/2018)",
     [
         ["Parcela", "Artigo (R$)", "Motor (R$)", "Diferença (R$)"],
         ["TUSD Demanda", "—", "—", "≤ 0,06"],
         ["TUSD Energia", "—", "—", "≤ 0,06"],
         ["TE", "—", "—", "≤ 0,06"],
         ["Ultrapassagem", "—", "—", "≤ 0,06"],
     ]),
    ("h2", "5.3 Análise de Enquadramento Tarifário"),
    ("p", "A Fig. 5 ilustra a comparação de custo entre as modalidades Azul e Verde "
          "para um perfil de consumo do Grupo A. Em geral, a modalidade Verde tende a "
          "ser mais vantajosa para consumidores com alta demanda e baixo consumo no "
          "horário de ponta, pois exige uma única demanda contratada; a modalidade "
          "Azul tende a ser mais vantajosa quando o consumo de ponta é elevado, pois "
          "sua TUSD Energia é única para todos os períodos. Para consumidores "
          "elegíveis ao Grupo B, a ferramenta também avalia a Convencional e a "
          "Branca, que podem eliminar custos de demanda e de reativos."),
    ("fig", "Fig. 5. Comparação de custo por modalidade tarifária (Azul × Verde)."),

    ("h1", "6. CONCLUSÕES"),
    ("p", "A ferramenta apresentada reconstrói faturas de energia elétrica do "
          "mercado cativo e compara as modalidades tarifárias aplicáveis, "
          "recomendando a de menor custo a partir do perfil de consumo do consumidor. "
          "A validação com faturas reais de quatro distribuidoras e com o artigo XX "
          "ERIAC 2025 demonstrou que o motor reproduz os valores com diferença igual "
          "ou inferior a R$ 0,05 por linha e R$ 1,00 no total, evidenciando precisão "
          "e aderência às regras da REN 1.000/2021."),
    ("p", "Além dos resultados de validação, o sistema contribui metodologicamente "
          "ao separar as regras de negócio da infraestrutura e ao garantir "
          "determinismo e reprodutibilidade: mesmas entradas e mesmas tarifas "
          "produzem sempre o mesmo resultado, o que favorece a rastreabilidade "
          "acadêmica. Permanecem em aberto, declaradamente, a fórmula fechada do EPI, "
          "a bandeira tarifária por posto, o mapeamento completo do dataset da ANEEL "
          "e a política de arredondamento monetário. Como trabalhos futuros, "
          "pretende-se incorporar o Sistema de Compensação de Energia Elétrica "
          "(SCEE), a integração com o ACL/CCEE e modelos de projeção de custos."),

    ("h1", "REFERÊNCIAS"),
    ("ref", "[1] ASSOCIAÇÃO BRASILEIRA DOS COMERCIALIZADORES DE ENERGIA (ABRACEEL). "
           "Cartilha Mercado Livre de Energia Elétrica. 23 maio 2019. Disponível em: "
           "https://pt.scribd.com/document/575210580/ABRACEEL-process-230519. "
           "Acesso em: 9 fev. 2025."),
    ("ref", "[2] MME. Portaria Normativa nº 50/GM/MME, de 28 de setembro de 2022. "
           "Diário Oficial da União, Brasília, DF, 28 set. 2022. Disponível em: "
           "https://in.gov.br/web/dou/-/portaria-normativa-n-50/gm/mme-de-27-de-setembro-de-2022-432279937. "
           "Acesso em: 9 fev. 2025."),
    ("ref", "[3] CÂMARA DE COMERCIALIZAÇÃO DE ENERGIA ELÉTRICA (CCEE). Guia rápido "
           "para migrar ao Mercado Livre de Energia. Disponível em: "
           "https://www.ccee.org.br/documents/80415/27405027/Guia_Rapido_para_Migrar_ao_Mercado_Livre_de_Energia_-_vertical_2.pdf/29ce1254-362b-1165-14c3-0dc5ea480de6. "
           "Acesso em: 9 fev. 2025."),
    ("ref", "[4] AGÊNCIA NACIONAL DE ENERGIA ELÉTRICA (ANEEL). Módulo 7: Estrutura "
           "tarifária das concessionárias de distribuição. Submódulo 7.1: "
           "Procedimentos gerais. Versão 2.5 C. Brasília, 2022. Disponível em: "
           "https://www2.aneel.gov.br/cedoc/aren20221003_Proret_Submod_7_1_V2_5C.pdf. "
           "Acesso em: 9 fev. 2025."),
    ("ref", "[5] ANEEL. Resolução Normativa nº 1.000/2021. Disponível em: "
           "https://www2.aneel.gov.br/cedoc/ren20211000.pdf. Acesso em: 9 fev. 2025."),
    ("ref", "[6] ANEEL. Resolução Normativa nº 1.000/2021 — texto integral. Diário "
           "Oficial da União, Brasília, DF, 20 dez. 2021."),
    ("ref", "[7] ANEEL. Bandeiras tarifárias. Disponível em: "
           "https://dadosabertos.aneel.gov.br/dataset/bandeiras-tarifarias. "
           "Acesso em: 9 fev. 2025."),
    ("ref", "[8] ANEEL. Base de dados das tarifas das distribuidoras de energia "
           "elétrica. Disponível em: "
           "https://portalrelatorios.aneel.gov.br/luznatarifa/basestarifas. "
           "Acesso em: 9 fev. 2025."),
    ("ref", "[9] K. Wu e F.Y.K. Takigawa, “Proposição de uma ferramenta para "
           "enquadramento tarifário do consumidor potencialmente livre”, XX ERIAC — "
           "Encontro Regional Ibero-americano do CIGRE, Ciudad del Este, Paraguai, "
           "maio 2025."),
]

# ---------------------------------------------------------------------------
# Gerador OOXML (stdlib)
# ---------------------------------------------------------------------------

NS_W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
NS_R = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def _rpr(bold=False, italic=False, size=22, font="Times New Roman", color=None,
         superscript=False):
    parts = []
    parts.append(f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}"/>')
    if bold:
        parts.append("<w:b/>")
    if italic:
        parts.append("<w:i/>")
    if color:
        parts.append(f'<w:color w:val="{color}"/>')
    parts.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    if superscript:
        parts.append('<w:vertAlign w:val="superscript"/>')
    return "<w:rPr>" + "".join(parts) + "</w:rPr>"


def run(text, **kw):
    if text == "":
        return ""
    return f"<w:r>{_rpr(**kw)}<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r>"


def para(inner, jc=None, spacing_before=None, spacing_after=None, indent_left=None,
         indent_hanging=None, p_border=False, style=None):
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if jc:
        ppr.append(f'<w:jc w:val="{jc}"/>')
    sp = []
    if spacing_before is not None:
        sp.append(f'<w:before w:val="{spacing_before}"/>')
    if spacing_after is not None:
        sp.append(f'<w:after w:val="{spacing_after}"/>')
    if sp:
        ppr.append("<w:spacing>" + "".join(sp) + "</w:spacing>")
    ind = []
    if indent_left is not None:
        ind.append(f'<w:left w:val="{indent_left}"/>')
    if indent_hanging is not None:
        ind.append(f'<w:hanging w:val="{indent_hanging}"/>')
    if ind:
        ppr.append("<w:ind>" + "".join(ind) + "</w:ind>")
    if p_border:
        ppr.append("<w:pBdr>"
                   '<w:top w:val="single" w:sz="4" w:space="4" w:color="000000"/>'
                   '<w:left w:val="single" w:sz="4" w:space="4" w:color="000000"/>'
                   '<w:bottom w:val="single" w:sz="4" w:space="4" w:color="000000"/>'
                   '<w:right w:val="single" w:sz="4" w:space="4" w:color="000000"/>'
                   "</w:pBdr>")
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else ""
    return f"<w:p>{ppr_xml}{inner}</w:p>"


def heading(text, primary=True):
    inner = run(text.upper() if primary else text, bold=primary, size=22)
    return para(inner, spacing_before=240 if primary else 120, spacing_after=120)


def body_para(text):
    return para(run(text, size=22), jc="both", spacing_after=120)


def figure_caption(caption):
    box = para(run("[ figura a inserir ]", size=22, italic=True), jc="center",
               p_border=True, spacing_before=120, spacing_after=120)
    cap = para(run(caption, size=22), jc="center", spacing_after=120)
    return box + cap


def table_block(caption, rows):
    out = [para(run(caption, size=20, bold=False), jc="center",
                spacing_before=120, spacing_after=60)]
    ncols = max(len(r) for r in rows)
    widths = 5000 // ncols
    grid = '<w:tblGrid>' + "".join(
        f'<w:gridCol w:w="{widths}"/>' for _ in range(ncols)) + "</w:tblGrid>"
    borders = ("<w:tblBorders>"
               '<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
               '<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
               '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
               '<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
               '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
               '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
               "</w:tblBorders>")
    trs = []
    for i, row in enumerate(rows):
        tcs = []
        for cell in row:
            cpr = '<w:tcPr><w:tcW w:w="%d" w:type="dxa"/></w:tcPr>' % widths
            p = para(run(cell, size=20, bold=(i == 0)), jc="center")
            tcs.append(f"<w:tc>{cpr}{p}</w:tc>")
        trs.append("<w:tr>" + "".join(tcs) + "</w:tr>")
    tbl = ('<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:jc w:val="center"/>'
           + borders + "</w:tblPr>" + grid + "".join(trs) + "</w:tbl>")
    out.append(tbl)
    out.append(para("", spacing_after=120))
    return "".join(out)


def reference_para(text):
    return para(run(text, size=22), indent_left=425, indent_hanging=425,
                spacing_after=60)


def build_document_xml():
    body = []

    # Cabeçalho ERIAC (1ª página)
    for text, color in ERIAC_HEADER:
        col = "008000" if color == "green" else ("4D4D4D" if color == "gray" else None)
        body.append(para(run(text, font="Arial", size=20, bold=True, color=col),
                         jc="center", spacing_after=0))

    body.append(para("", spacing_after=120))

    # Título
    body.append(para(run(TITLE, font="Arial", size=24, bold=True), jc="center",
                     spacing_before=240, spacing_after=120))

    # Autores
    for name, is_main in AUTHORS:
        runs = run(name, size=24, bold=True)
        if is_main:
            runs += ('<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr>'
                     '<w:footnoteReference w:id="1"/></w:r>')
        body.append(para(runs, jc="center", spacing_after=0))
    body.append(para(run(INSTITUICAO, size=24, bold=True), jc="center", spacing_after=0))
    body.append(para(run(PAIS, size=24, bold=True), jc="center", spacing_after=0))

    # Resumo (início aproximado a 12 cm do topo da 1ª página)
    body.append(para(run(ABSTRACT, italic=True, size=22), jc="both",
                     spacing_before=2000, spacing_after=120))

    # Palavras-chave
    body.append(para(run("Palavras-chave: ", bold=True, size=22)
                     + run(KEYWORDS, size=22), jc="both", spacing_after=120))

    # Corpo
    for block in BLOCKS:
        kind = block[0]
        if kind == "h1":
            body.append(heading(block[1], primary=True))
        elif kind == "h2":
            body.append(heading(block[1], primary=False))
        elif kind == "p":
            body.append(body_para(block[1]))
        elif kind == "fig":
            body.append(figure_caption(block[1]))
        elif kind == "table":
            body.append(table_block(block[1], block[2]))
        elif kind == "ref":
            body.append(reference_para(block[1]))

    # Seção final: rodapés com numeração a partir da 2ª página
    sect = (
        "<w:sectPr>"
        '<w:footerReference w:type="first" r:id="rIdF1"/>'
        '<w:footerReference w:type="default" r:id="rIdF2"/>'
        "<w:titlePg/>"
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1417" w:right="1134" w:bottom="1417" w:left="1134" '
        'w:header="708" w:footer="708" w:gutter="0"/>'
        "</w:sectPr>"
    )
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:document {NS_W} {NS_R}><w:body>{"".join(body)}{sect}</w:body></w:document>')


def build_styles_xml():
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:styles {NS_W}>'
            '<w:docDefaults><w:rPrDefault><w:rPr>'
            '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
            '<w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="pt-BR"/>'
            '</w:rPr></w:rPrDefault>'
            '<w:pPrDefault><w:pPr><w:spacing w:line="240" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
            '</w:docDefaults>'
            '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
            '<w:name w:val="Normal"/><w:qFormat/></w:style>'
            '<w:style w:type="character" w:styleId="FootnoteReference">'
            '<w:name w:val="Footnote Reference"/>'
            '<w:rPr><w:vertAlign w:val="superscript"/></w:rPr></w:style>'
            '<w:style w:type="paragraph" w:styleId="FootnoteText">'
            '<w:name w:val="Footnote Text"/>'
            '<w:rPr><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr></w:style>'
            f'</w:styles>')


def build_settings_xml():
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:settings {NS_W}>'
            '<w:footnotePr><w:numFmt w:val="chicago"/></w:footnotePr>'
            '</w:settings>')


def build_footnotes_xml():
    note = (
        '<w:footnote w:id="1">'
        '<w:p><w:pPr><w:pStyle w:val="FootnoteText"/></w:pPr>'
        '<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteRef/></w:r>'
        f'{run(FOOTNOTE_TEXT, size=20)}'
        '</w:p></w:footnote>'
    )
    sep = ('<w:footnote w:type="separator" w:id="-1"><w:p><w:pPr>'
           '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
           '<w:r><w:separator/></w:r></w:p></w:footnote>')
    cont = ('<w:footnote w:type="continuationSeparator" w:id="0"><w:p><w:pPr>'
            '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
            '<w:r><w:continuationSeparator/></w:r></w:p></w:footnote>')
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:footnotes {NS_W}>{sep}{cont}{note}</w:footnotes>')


def build_footer1_xml():
    # 1ª página: sem numeração
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:ftr {NS_W}><w:p><w:pPr><w:jc w:val="right"/></w:pPr></w:p></w:ftr>')


def build_footer2_xml():
    # 2ª página em diante: número no canto inferior direito
    page = (f'<w:p><w:pPr><w:jc w:val="right"/></w:pPr>'
            '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:ftr {NS_W}>{page}</w:ftr>')


def build_content_types():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
            '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
            '<Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>'
            '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
            '<Override PartName="/word/footer2.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
            '</Types>')


def build_root_rels():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '</Relationships>')


def build_document_rels():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rIdS" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            '<Relationship Id="rIdSet" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
            '<Relationship Id="rIdFN" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>'
            '<Relationship Id="rIdF1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
            '<Relationship Id="rIdF2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer2.xml"/>'
            '</Relationships>')


def main():
    parts = {
        "[Content_Types].xml": build_content_types(),
        "_rels/.rels": build_root_rels(),
        "word/document.xml": build_document_xml(),
        "word/_rels/document.xml.rels": build_document_rels(),
        "word/styles.xml": build_styles_xml(),
        "word/settings.xml": build_settings_xml(),
        "word/footnotes.xml": build_footnotes_xml(),
        "word/footer1.xml": build_footer1_xml(),
        "word/footer2.xml": build_footer2_xml(),
    }
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in parts.items():
            z.writestr(name, content)
    print(f"Gerado: {OUT}")


if __name__ == "__main__":
    main()
