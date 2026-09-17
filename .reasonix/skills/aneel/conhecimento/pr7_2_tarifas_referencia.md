# PRORET 7.2 — Tarifas de Referência

> Fonte: `PRORET 7.2_TARIFAS DE REFERÊNCIA.pdf` (Submódulo 7.2, Versão 2.5).
> Classificação: *Regra explícita* / *Interpretação* / *Não determinado*.
> As equações são numeradas como no documento (1) a (18).

## 1. Objetivo e abrangência *(pág. 2)*
- Metodologia de cálculo das **Tarifas de Referência**, necessárias para TUSD e TE. *(Regra explícita — pág. 2)*
- Aplica-se a revisões/reajustes. *(Regra explícita — pág. 2)*

## 2. Agrupamentos por nível de tensão (Tabela 1) *(pág. 2)*
| Grupo/Subgrupo | Agrupamento |
|---|---|
| A2 | AT-2 (88 a 138 kV) |
| A3 | AT-3 (69 kV) |
| A3a e A4 | MT (acima de 1 kV e inferior a 69 kV) |
| AS e B | BT (igual ou inferior a 1 kV) |

*(Regra explícita — pág. 2)*

## 3. TUSD FIO B — base estatística *(pág. 2–7)*
### 3.1 Custo Marginal de Capacidade (CMC) *(pág. 2)*
- Equação **(1)**:
  ```
  CMC(u,j) = Σ_k CMEx(k) × Ø(k,k0) × RP(u,k,j)
  ```
- Termos: posto (ponta/FP), consumidor-tipo, agrupamento, custo marginal de expansão, proporção de fluxo, responsabilidade de potência. *(Regra explícita — pág. 2–3)*

### 3.2 Custo Marginal de Expansão (CMEx) *(pág. 3)*
- Obtido por **custos médios** do sistema (módulos de equipamentos/obras); considera IRPJ/CSLL, WACC, O&M e vida útil. *(Regra explícita — pág. 3)*

### 3.3 Proporção de Fluxo de Potência *(pág. 3)*
- Parcela de utilização do sistema a montante a partir de fluxos diretos/indiretos, no diagrama unifilar simplificado na carga máxima. *(Regra explícita — pág. 3)*

### 3.4 Responsabilidade de Potência (RP) *(pág. 4)*
- Equação **(2)**:
  ```
  RP(u,k,j) = (1 + fpp) · Σ_{h∈u} π(j,k,h) · P(j,h)
  ```
- fpp (fator perdas potência), equação **(3)** (formula longa de perdas/caminhos). *(Regra explícita — pág. 4–5)*

### 3.5 Estrutura Vertical (EV) *(pág. 6)*
- Equações **(4)**, **(5)**, **(6)**:
  ```
  EVF(k) = EVM(k)·m(k)
  EVM(k) = RT%(k)·(100% − VPB%TC) + PC%(k)·VPB%TC
  PC%(k) = (p·NUCk / Σ p·NUCk)·100%
  ```
- p = 1 (grupo B/BT) ou 10 (grupo A/AT-MT). *(Regra explícita — pág. 6)*

### 3.6 Tarifas de Referência TUSD FIO B *(pág. 6–7)*
- Equações **(7)** e **(8)**:
  ```
  TR_FIOB_FP[k] = VPBSGER·EVF(k) / [MFP(k) + RPFP_FIOB[k]·MP(k)]
  TR_FIOB_P[k]  = RPFP_FIOB[k] · TR_FIOB_FP[k]
  ```
- Relação ponta/FP limitada a **10,00**. *(Regra explícita — pág. 6–7)*

## 4. TUSD FIO A *(pág. 7–8)*
- Equações **(9)** e **(10)** (tarifa de referência FIO A por componente j, posto, fronteira). *(Regra explícita — pág. 7)*

## 5. TUSD TRANSPORTE *(pág. 8–10)*
- Equação **(11)**:
  ```
  TR_TRANSP[u,k] = Σ_j TR_FIOA[u,k](j)·ma(j) + TR_FIOB[u,k]
  ```
- Adequação por modalidade *(pág. 8)*:
  - **Verde**: converte posto ponta para R$/MWh via **Fator de Carga (FC)**.
  - **Convencional Binômia**: ponta+FP → única R$/kW (perfil típico).
  - **Convencional Monômia**: → R$/MWh (mercado de referência de demanda/energia).
  - **Branca**: baseada na monômia + fatores (item 10 do 7.1). *(Regra explícita — pág. 8)*

### 5.1 Modalidade Distribuição *(pág. 8–10)*
- 5 tipos de conexão **D1–D5**; regras FIO A/FIO B por tipo. *(Regra explícita — pág. 8–9)*
- Fator k: equações **(12)** e **(13)**:
  ```
  TRFIOB,D-k [u] = kk · TRFIOB[u,k]
  TRFIOB,D-BT   = kBT · TRFIOB,BT
  ```
*(Regra explícita — pág. 9–10)*

### 5.2 Modalidade horária Branca *(pág. 10)*
- **Ponta** = 5× fora ponta; **Intermediária** = 3×; **Fora ponta** = TUSD Convencional monômia × **kz**. *(Regra explícita — pág. 10)*

## 6. TUSD PERDAS *(pág. 10–12)*
- **Perdas técnicas** (eq. **14**–**16**): `TR_PTk = FPE%(k)·PME/100·θk`; θk ponderador carga/geração; Fator FPE por matriz de fluxo. *(Regra explícita — pág. 10–11)*
- **Perdas não técnicas/receitas irrecuperáveis** (eq. **17**):
  ```
  TR_PNT/RI,k = EUSDk(R$) / ΣEUSDki(R$) · 1/MEk · CUSTO_PNT/RI
  ```
*(Regra explícita — pág. 12)*

## 7. TUSD ENCARGOS *(pág. 12–13)*
- TFSEE, P&D_EE, CDE e CDE CONTAS com regras específicas; demais encargos unitários R$/MWh. *(Regra explícita — pág. 12)*
- **Tabela 2 — Trajetória das Tarifas de Referência da CDE (2016–2030)** por agrupamento AT-2/AT-3, MT, BT (valores decrescentes de 1,00 a 0,45/0,75/1,00). *(Regra explícita — pág. 12–13)*

## 8. TE ENERGIA *(pág. 13–14)*
- Posto **fora ponta e intermediário** = 1,00; **ponta** = 1,72. *(Regra explícita — pág. 13)*
- Convencional = média ponderada (eq. **18**):
  ```
  TR_ENEC = (RPFPTE·HP + HFP) / (HP + HFP)
  ```
*(Regra explícita — pág. 13)*

## 9. TE TRANSPORTE / PERDAS / ENCARGOS *(pág. 13–14)*
- Valor unitário R$/MWh em qualquer subgrupo/posto (fator de ajuste na aplicação recupera custos). *(Regra explícita — pág. 13)*

## 10. Casos especiais *(pág. 13–14)*
- **Subgrupo A1** (≥230 kV com CUSD): TUSD FIO A = TUST do ponto de conexão; FIO B = 0. *(Regra explícita — pág. 13–14)*
- **Subgrupo B4 (IP)**: B4a = 55% e B4b = 60% das TR do B1. *(Regra explícita — pág. 14)*
- **Centrais geradoras**: conforme Submódulo 7.4. *(Regra explícita — pág. 14)*
