# Componentes tarifários

> Fonte: `Base de Dados e Análise das Tarifas das Distribuidoras de Energia Elétrica.pdf` (Guia Básico ANEEL).
> Classificação: *Regra explícita* / *Interpretação* / *Não determinado*.

## 1. Painel "Componentes Tarifárias" *(pág. 1)*
- Apresenta detalhadamente os itens que compõem as tarifas. *(Regra explícita)*
- Exemplos citados: `TUSD_CCT`, `TUSD_ONS`, `TE_CDE_COVID`, `TE_TUST_CI`. *(Regra explícita — pág. 1)*
- **Total de 40 componentes tarifários** disponíveis; cada um representa encargo, custo setorial ou item de ajuste regulatório. *(Regra explícita — pág. 1)*

## 2. Quando usar o painel de componentes *(pág. 1, 3)*
- Em geral, o painel **TUSD e TE** é o mais utilizado. *(Regra explícita — pág. 1)*
- Para consumidores com **SCEE** (Sistema de Compensação de Energia Elétrica), o painel **Componentes Tarifárias é de maior interesse**. *(Regra explícita — pág. 1)*

## 3. Diferença entre os dois painéis *(pág. 3)*
- A estrutura da tabela é semelhante; a diferença está nas **duas últimas colunas**:
  - Painel TUSD e TE → colunas **TUSD** e **TE**.
  - Painel Componentes Tarifárias → colunas **Componente tarifária** e **Valor**. *(Regra explícita — pág. 3)*

## 4. Parcelas para SCEE — GDII e GDIII *(pág. 5)*
Para verificar percentuais de desconto na TUSD/TE usados no faturamento da energia compensada (SCEE) de consumidores GDII/GDIII, filtrar no painel **Componentes Tarifárias**:

- **Fio A**:
  - TUSD RB
  - TUSD FR
  - Conexão T
  - Conexão D
  - CUSD
  - TUSDG-T
  - TUSDG-NOS
- **Fio B**:
  - TUSD-TFSEE
  - TUSD-PeD

*(Regra explícita — pág. 5)*

- Observação do documento: "a TUSD não se aplica e a TE do tipo SCEE deve ser consultada diretamente no painel TE e TUSD". *(Regra explícita — pág. 5)*

## 5. Memorial de cálculo *(pág. 5)*
- Documento técnico que detalha como foram apurados/justificados os valores cobrados. *(Regra explícita — pág. 5)*
- Anexo citado: correspondências entre os componentes tarifários da base e os componentes dos memoriais de cálculo (**CELESC-DIS, COELBA, CELPE, COPEL, CEMIG e CPFL PAULISTA**), todas com formato padrão (mesmas componentes). *(Regra explícita — pág. 5)*

## 6. Relação com nosso banco atual
- Nosso banco armazena **apenas TE e TUSD** (componentes de nível agregado), **não** os 40 componentes individuais detalhados. *(Interpretação/Não determinado — não há impacto até usarmos SCEE/componentes)*
- SCEE está **fora do MVP** (decisão de escopo do projeto), portanto os 40 componentes individuais e o detalhamento Fio A/Fio B ficam como evolução futura. *(Interpretação coerente com o fora-do-MVP)*
