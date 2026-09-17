# Projeto anterior — Estrutura de arquivos

> Inventário da pasta `C:\Users\vitor\Downloads\OneDrive_2026-09-10\Kevin Wu`.

## Tipos
- **Excel .xlsx** (sem macro): 6 (bases/tabelas/análises).
- **Excel .xlsm** (com macro): 2 (simuladores).
- **Word .docx**: 4.
- **PowerPoint .pptx**: 2.
- **PDF**: 6.
- **PNG**: 5.
- **TXT/LINKS**: 4 (1 `LINKS.txt` + certificados extras).

## Arquivos principais

### `Simulador de Fatura/`
- `Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm` — simulador de fatura Grupo A (11 abas).
- `Calculador de Porcentagens SCEE/Calculador de Porcentagens - SCEE - Macro Habilitada.xlsm` — calculador SCEE (15 abas).
- `Calculador de Porcentagens SCEE/componentes scee 2022_2025 - 26.08.25.xlsx` e `Tarifas TE e TUSD - 2022 até 2025 - 26.08.25.xlsx` — dados auxiliares do SCEE.
- `tarifas 2010-2025 - 27.06.25.xlsx` — base completa de tarifas (4 abas).
- `Exemplos de Faturas de Energia/LINKS.txt` — links de faturas reais.

### `Base de Dados e Análise de Tarifas/`
- `Análise de Tarifas - Prévia.xlsx` — análise/boxplots (32 MB).
- `Filtros e Base de dados ANEEL - 27.06.25.xlsx` — base com filtros (22 MB).
- `Discretização tarifas - eixo vertical.xlsx` — discretização por componente/posto.
- `Banco de Dados ANEEL e Mem. Cal..xlsx` — componente ↔ memorial de cálculo.
- `Base de Dados e Análise das Tarifas das Distribuidoras de Energia Elétrica.docx` + 4 PNGs + 1 PPTX.

### `Faturamento Consumidores SCEE/`
- `Faturas no SCEE - apresentações e outros documentos/` — faturas Celesc (2 PDFs + 2 devolutivas + 1 PPTX).
- `Faturas no SCEE - cálculos e contas matemáticas/Devolutiva das Faturas da Celesc.xlsx` — 2 abas (dez.2023/jan.2024).
- `Guia Prático para o Cálculo dos Percentuais de Desconto do SCEE.docx`.
- `Sobre FIOA e FIOB das distribuidoras.xlsx` — 9 abas.

### `Verificar Simuladores de Faturas das Distribuidoras/`
- 5 `.xlsx` + 1 `.docx` (mapeamento de simuladores).

### `XXERIAC 2025/`
- artigo `.docx` + apresentação `.pptx` + 3 certificados PDF.

## Relações entre arquivos
- `Ferramenta de Recriar Faturas` consome a base de tarifas (equivalente a `tarifas 2010-2025`).
- `Calculador SCEE` consome `componentes scee` e `Tarifas TE e TUSD` (componentes Fio A/B).
- `Devolutiva das Faturas da Celesc` é o caso real de validação SCEE.
- `Análise de Tarifas - Prévia` usa a `Filtros e Base de dados ANEEL`.
