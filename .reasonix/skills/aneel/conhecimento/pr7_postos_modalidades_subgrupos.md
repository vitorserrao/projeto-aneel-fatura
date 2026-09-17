# PRORET 7 — Postos, modalidades e subgrupos

> Fonte: PRORET 7.1 (Tabela 1, §5) e 7.2 (Tabela 1 de agrupamentos).
> Classificação: *Regra explícita* / *Interpretação* / *Não determinado*.

## 1. Postos tarifários *(7.1 §5, pág. 3–4)*
- **Ponta**: 3 horas diárias consecutivas definidas pela distribuidora (aprovado ANEEL); exceto fins de semana/feriados.
- **Intermediário**: 2 horas (1 antes + 1 depois da ponta).
- **Fora de Ponta**: demais horas.
- Pode ocorrer flexibilização (item 10 do 7.1). *(Regra explícita)*

## 2. Modalidades tarifárias *(7.1 §5, pág. 4)*
| Modalidade | Grupo | Característica de faturamento |
|---|---|---|
| Azul | A | consumo e **demanda** diferenciados (ponta/FP) |
| Verde | A | consumo diferenciado; **demanda única** |
| Convencional Binômia | A | consumo + demanda, sem distinção horária |
| Branca | B | consumo diferenciado por hora |
| Convencional Monômia | B | consumo, sem distinção horária |
| Geração | geradoras | demanda, sem distinção horária |
| Distribuição | distribuidoras conectadas | demanda e consumo diferenciados |
| Pré-pagamento | consumidores | RN 610/2014 |

*(Regra explícita — 7.1 pág. 4)*

## 3. Subgrupos tarifários *(7.1, pág. 4; 7.2, pág. 2)*
- Grupo A (≥ 2,3 kV): **A1, A2, A3, A3a, A4, AS**.
- Grupo B (< 2,3 kV): **B1 (residencial), B2 (rural), B3 (demais classes), B4 (Iluminação Pública)**. *(Regra explícita — 7.1 pág. 4; Tabela 1 pág. 6)*

### Correlação com agrupamentos (nível de tensão) *(7.2 Tabela 1)*
| Subgrupo | Agrupamento |
|---|---|
| A2 | AT-2 (88–138 kV) |
| A3 | AT-3 (69 kV) |
| A3a, A4 | MT (>1 kV e <69 kV) |
| AS, B | BT (≤1 kV) |

*(Regra explícita — 7.2 pág. 2)*

## 4. Tabela 1 do 7.1 — tarifas por subgrupo × modalidade (grandezas)
- **A1 (≥230 kV):** Azul (R$/kW e R$/MWh em ponta/intermediária/FP), Distribuição, Geração.
- **A2, A3:** Azul, Geração, Distribuição (R$/kW demanda + R$/MWh energia por posto).
- **A3a, A4, AS:** Azul, **Verde** (demanda única R$/kW + energia R$/MWh), Convencional Binômia, Distribuição, Geração.
- **B1/B2/B3:** Convencional Monômia, Branca, Pré-pagamento (R$/MWh).
- **B4 (IP):** Convencional (R$/MWh).
- **Distribuição** e **Geração**: tarifas próprias (R$/kW e/ou R$/MWh). *(Regra explícita — 7.1 pág. 5–6)*

## 5. Adequação por modalidade (conversões) *(7.2 pág. 8)*
- **Verde**: TUSD TRANSPORTE ponta → R$/MWh via **Fator de Carga (FC)**.
- **Convencional Binômia** (A): ponta+FP → única R$/kW.
- **Convencional Monômia** (B): ponta+FP → R$/MWh.
- **Branca** (B): derivada da monômia + fatores (ponta = 5×FP; intermediária = 3×FP). *(Regra explícita — 7.2 pág. 8, 10)*

## 6. Fatores padrão para construção (7.1 Tabela 2)
- Relação Ponta/FP: A2/A3/A4/AS = **Relação Atual**; B = **5,00**; Intermediária/FP B = **3,00**.
- Fator de cruzamento Azul/Verde = **0,66**.
- Fator de Ponta da Energia = **1,72**; Fora de Ponta = **1,00**; Convencional = **1,06**. *(Regra explícita — 7.1 pág. 12)*

## 7. Relação com o projeto
- Este mapa (subgrupo × modalidade × grandeza) é a **referência estrutural** para o motor de cálculo: determina quais parcelas de demanda/energia e postos existem para cada modalidade. *(Interpretação)*
- A elegibilidade exata por perfil (quando uma modalidade é "aplicável" a um consumidor) ainda é matéria de decisão regulatória/comercial e **não** está resolvida aqui. *(Não determinado para a regra de negócio)*
