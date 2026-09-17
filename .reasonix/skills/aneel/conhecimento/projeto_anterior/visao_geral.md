# Projeto anterior (Kevin Wu) — Visão geral

> Fonte: `C:\Users\vitor\Downloads\OneDrive_2026-09-10\Kevin Wu` (arquivos originais, não alterados).
> Hierarquia de confiança: este material é **referência de validação (5ª prioridade)**, NUNCA verdade automática.

## 1. O que era o projeto
Conjunto de ferramentas Excel (algumas com macro VBA) para:
1. **Analisar** a base de dados de tarifas da ANEEL (TUSD/TE, filtros, médias, discretização).
2. **Recriar faturas** de energia do **Grupo A** (consumidores de alta tensão, sem SCEE) comparando modalidades Azul/Verde/Convencional/Monômia/Branca.
3. **Calcular percentuais de desconto do SCEE** (GD I/II/III) por subgrupo/modalidade/posto, a partir dos componentes tarifários (Fio A/Fio B/encargos/perdas).

## 2. Componentes principais (arquivos)

| Arquivo | Finalidade | Importância |
|---|---|---|
| `Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm` | Simulador de fatura Grupo A (11 abas) | **Muito alta** — fonte dos cálculos de fatura |
| `Calculador de Porcentagens SCEE` (subpasta, .xlsm + 2 .xlsx aux.) | Percentual de desconto SCEE por subgrupo/modalidade/posto | **Alta** — regra do SCEE |
| `Análise de Tarifas - Prévia.xlsx` | Análise/médias/boxplots por distribuidora | Média |
| `Filtros e Base de dados ANEEL - 27.06.25.xlsx` + `tarifas 2010-2025` | Base completa (TUSD/TE) de 2010 a 2025 | Média (já ingerimos no novo projeto) |
| `Discretização tarifas - eixo vertical.xlsx` | Discretização por componente/posto/modalidade | Média |
| `Banco de Dados ANEEL e Mem. Cal..xlsx` | Correspondência componentes ↔ memoriais de cálculo | Média |
| `Sobre FIOA e FIOB das distribuidoras.xlsx` | Componentes Fio A/Fio B por distribuidora | Média |
| `Devolutiva das Faturas da Celesc.xlsx` + PDFs | Casos reais de fatura SCEE (B1 Celesc 2023/2024) | **Alta** — casos de validação |
| `Guia Prático SCEE.docx` + docs Word/PPTX | Metodologia e explicitação | Média |
| `XXERIAC 2025` (artigo/ppt) | Divulgação científica (14_3336) | Baixa para cálculos |

## 3. Conclusão central
- O projeto anterior **recria faturas** somando linhas de cobrança (demanda, consumo, TE, TUSD, bandeira, reativos, CIP, outros) por modalidade, aplicando **tributos "por dentro"** e comparando modalidades.
- O novo sistema já reproduz parcialmente o motor (linhas × tarifa), mas **ainda não implementa o cálculo de tributos por dentro nem todos os componentes de fatura** — estes são conhecimento a migrar.
