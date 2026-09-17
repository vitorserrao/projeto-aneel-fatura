# PRORET 7 — Consolidação de fórmulas e tabelas

> Fontes: PRORET 7.2 (equações 1–18) e 7.1 (Tabelas 2 e 3).
> Classificação: *Regra explícita* / *Interpretação* / *Não determinado*.
> Equações numeradas conforme documento original.

## Fórmulas de Tarifas de Referência (Submódulo 7.2)

| # | Fórmula | Página (7.2) | Nota |
|---|---|---|---|
| (1) | `CMC(u,j) = Σ_k CMEx(k) · Ø(k,k0) · RP(u,k,j)` | 2 | custo marginal de capacidade |
| (2) | `RP(u,k,j) = (1 + fpp) · Σ_{h∈u} π(j,k,h) · P(j,h)` | 4 | responsabilidade de potência |
| (3) | perdas de potência por caminhos (fpp) | 5 | fator de perdas de potência |
| (4) | `EVF(k) = EVM(k) · m(k)` | 6 | estrutura vertical |
| (5) | `EVM(k) = RT%(k)·(100% − VPB%TC) + PC%(k)·VPB%TC` | 6 | estrutura modificada |
| (6) | `PC%(k) = (p·NUCk / Σ p·NUCk)·100%` | 6 | p=1 (B) ou 10 (A) |
| (7) | `TR_FIOB_FP[k] = VPBSGER·EVF(k) / [MFP(k) + RPFP_FIOB[k]·MP(k)]` | 6 | FIO B fora ponta |
| (8) | `TR_FIOB_P[k] = RPFP_FIOB[k] · TR_FIOB_FP[k]` | 6 | FIO B ponta (relação máx 10) |
| (9) | `TR_FIOA[u,k](j) = Σ (TRFIOA[u,k0](j) / (1 − fpp(k,k0)) · Ø(k,k0) · Pu(k,k0))` | 7 | FIO A |
| (10) | `TRFIOA[u,k0](j) = CUSTOFIOA[u,k0](j) / DT[u,k0]` | 7 | custo unitário FIO A |
| (11) | `TR_TRANSP[u,k] = Σ_j TR_FIOA[u,k](j)·ma(j) + TR_FIOB[u,k]` | 8 | TUSD transporte |
| (12) | `TRFIOB,D-k[u] = kk · TRFIOB[u,k]` | 10 | distribuição D3/D4 |
| (13) | `TRFIOB,D-BT = kBT · TRFIOB,BT` | 10 | distribuição D5 |
| (14) | `TR_PTk = FPE%(k)·PME/100·θk` | 11 | perdas técnicas |
| (15) | `θk = (EC+D(k) + EG_F(k)) / (EC+D(k) + EG(k) + EG_F(k))` | 11 | ponderador carga/geração |
| (16) | `[FPE%] = [PS]ᵀ · [FIS]⁻¹` | 11 | fator de perdas de energia |
| (17) | `TR_PNT/RI,k = EUSDk(R$) / ΣEUSDki(R$) · 1/MEk · CUSTO_PNT/RI` | 12 | não técnicas/irrecuperáveis |
| (18) | `TR_ENEC = (RPFPTE·HP + HFP) / (HP + HFP)` | 13 | TE convencional |

*(Regra explícita — 7.2)*

## Fatores numéricos (Submódulo 7.1 — Tabela 2, pág. 12)

| Fator | Valor |
|---|---|
| Relação Ponta/Fora de Ponta — A2/A3/A4/AS | Relação Atual |
| Relação Ponta/Fora de Ponta — B | 5,00 |
| Relação Intermediária/Fora de Ponta — B | 3,00 |
| Fator de cruzamento retas Azul/Verde | 0,66 |
| Fator de Ponta da Energia | 1,72 |
| Fator de Fora de Ponta da Energia | 1,00 |
| Fator Convencional da Energia | 1,06 |

*(Regra explícita — 7.1 pág. 12)*

## Apresentação na fatura (Submódulo 7.1 — Tabela 3, pág. 13)

| Custo | Componentes associados |
|---|---|
| Energia | TE-ENERGIA, TE-TRANSPORTE e bandeira tarifária em vigor |
| Serviços de Distribuição | TUSD – FIO B |
| Transmissão | TUSD – FIO A |
| Perdas de Energia | TUSD – PERDAS e TE-PERDAS |
| Encargos Setoriais | TUSD – ENCARGOS e TE-ENCARGOS |
| Outros | TUSD – OUTROS e TE-OUTROS |

*(Regra explícita — 7.1 pág. 13)*

## Trajetória CDE (Submódulo 7.2 — Tabela 2, pág. 12–13)
- Fatores por agrupamento (AT-2/AT-3, MT, BT) de 2016 a 2030, decrescendo de 1,00 até 0,33/0,67/1,00 (por ano de processo tarifário). *(Regra explícita — 7.2 pág. 12–13)*

## Regras de aplicação (Submódulo 7.3) — resumo
- **Tarifa de Aplicação = base econômica + base financeira** (TUSD e TE). *(Regra explícita — 7.3 pág. 2–3)*
- Base econômica = Tarifa de Referência × fator multiplicativo; base financeira = base econômica × fator financeiro. *(Regra explícita — 7.3)*

## Lacunas (não determinadas nestes 3 documentos)
- **Submódulo 7.4** (centrais geradoras) — referenciado, mas não incluso.
- **Módulo 4** (componentes financeiros) — base para o fator financeiro.
- Valores concretos de CMEx/WACC/etc. — dependem de cada processo tarifário, não estão no texto.
