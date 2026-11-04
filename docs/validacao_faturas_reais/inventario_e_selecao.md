# Inventário e seleção — faturas reais para validação

> Referência: **faturas reais** (ground truth). Planilha do projeto anterior e artigo
> entram apenas como comparação secundária documental. Tolerância: **≤ R$ 0,05/linha
> e ≤ R$ 1,00/total**. Comparação em duas camadas: (1) tarifas líquidas da fatura;
> (2) tarifas do nosso banco.

## 1. Pastas

- `C:\Users\vitor\Downloads\fwdfaturagrupoa` — PDFs textuais (Equatorial Pará 12/2024,
  CEMIG BH 09–12/2023, fatura agrupadora 400000128005).
- `C:\Users\vitor\Downloads\OneDrive_2026-09-10\Kevin Wu\Simulador de Fatura\Exemplos de Faturas de Energia\grupo A` —
  exemplos COPEL/ENEL (PDF) e CPFL/ELEKTRO/CELESC (imagens).

## 2. Classificação das faturas

| Arquivo | Distribuidora | Subgrupo | Modalidade | Competência | Tipo |
|---|---|---|---|---|---|
| COPEL - grupo A.pdf | Copel | A4 | Verde | 04/2023 | PDF textual (já validada) |
| ENEL - grupo A.pdf | Enel SP | A4 | Verde | 01/2021 | PDF textual |
| 23-09 a 23-12 BH CI_934 / CII_112 | CEMIG | A4 | Verde (THS) | 09–12/2023 | PDF textual, tarifas líquidas impressas |
| *_DEZEMBRO_2024 (Equatorial) | Equatorial Pará | A4/A3 | Verde (A4_VD/A3_VD) | 12/2024 | PDF textual |
| 400000128005 (COMPLETA SEM ULTRAPASSAGEM) | Equatorial Pará | A4 (agrupadora) | Verde | 12/2024 | PDF textual (79 pág.) |
| CPFL 2.0/3.1/3.2 - grupo A.jpg | CPFL | ? | ? | ? | imagem |
| ELEKTRO 2.0 - grupo A.png | Elektro | ? | ? | ? | imagem |
| celesc 3.x/5.x - grupo A.webp | Celesc | ? | ? | ? | imagem |

## 3. Seleção inicial

- **Verde (PDF textual):**
  1. COPEL ON PETRO 04/2023 (caso já validado — revalidar nas duas camadas).
  2. CEMIG BH CI_934 09/2023 (imprime tarifa líquida e tarifa com impostos).
  3. ENEL A4 Comercial 01/2021 (linhas TUSD/TE detalhadas).
  4. Equatorial ABAETETUBA 12/2024 (A4 Verde, fp 0,885 → reativos excedentes).
- **Azul:** candidatos nas imagens (CPFL 3.1/3.2, CELESC) — classificar via leitura
  visual (view_image) na fase 2; se nenhuma for Azul, solicitar uma fatura Azul.

## 4. Formato do caso de validação (JSON)

Cada fatura vira um arquivo `docs/validacao_faturas_reais/casos/<id>.json`:

```json
{
  "id": "copel_2023_04",
  "meta": {
    "fonte": "caminho do PDF",
    "distribuidora": "COPEL-DIS",
    "subgrupo": "A4",
    "modalidade": "Verde",
    "competencia": "04/2023",
    "total_fatura": 9854.93
  },
  "perfil": {
    "data_referencia": "2023-03-15",
    "consumo_ponta_kwh": 55,
    "consumo_fora_ponta_kwh": 9094,
    "demanda_medida_unica_kw": 150.65,
    "demanda_contratada_unica_kw": 260,
    "reativo_energia_fora_ponta_kvArh": 0,
    "cip_cosip_rs": 0,
    "outros_rs": 115.01,
    "bandeira_adicional_r_kwh": 0
  },
  "tributos": {"pis": 0.0095, "cofins": 0.0438, "icms": 0.18, "tipo_icms": "fora"},
  "tarifas_liquidas": [
    {"componente": "TE", "grandeza": "ENERGIA", "posto": "PONTA", "unidade": "R$/MWh", "valor": 388.08}
  ],
  "linhas_esperadas": [
    {"descricao": "ENERGIA ELETRICA TE PONTA", "quantidade": 55, "tarifa": 0.499818, "valor": 27.49}
  ]
}
```

Regras de extração:
- `tarifas_liquidas` = tarifa **sem impostos** (da seção "Informações Suplementares"
  ou derivada da tarifa com impostos pelo fator por fora/dentro).
- `linhas_esperadas` = linhas de cobrança da fatura, na ordem impressa.
- `perfil` usa os mesmos nomes de campos do schema `Consumidor`.
