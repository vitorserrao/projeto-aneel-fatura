# Cartilha 2013 — Tributos na conta de luz

> Fonte: `PorDentrodaContadeLuz_2013.pdf` (ANEEL, 6ª edição, março 2013).
> Classificação: *Regra explícita* / *Interpretação* / *Não determinado*.

## Visão geral *(pág. 15)*
- Tributos são pagamentos compulsórios devidos ao poder público, **embutidos nos preços**; também na conta de luz. As distribuidoras recolhem e repassam aos entes. *(Regra explícita — pág. 15)*
- A redução após a Lei 12.783/2013 decorre da **redução da base de cálculo**, não da alteração de alíquotas. *(Regra explícita — pág. 15)*

## 1. PIS e COFINS (tributos federais) *(pág. 15)*
- Finalidade: programas do trabalhador (PIS) e seguridade social (COFINS).
- **Alíquotas nominais:** PIS **1,65%**; COFINS **7,60%**, apurados de forma **não-cumulativa**. *(Regra explícita — pág. 15)*
- A **alíquota efetiva/média** varia com os créditos apurados mensalmente (ex.: energia adquirida para revenda). *(Regra explícita — pág. 15)*

### Exemplo (não-cumulativo) *(pág. 15)*
| Item | Valor |
|---|---|
| Faturamento bruto | R$ 10.000,00 |
| PIS débito | R$ 165,00 |
| COFINS débito | R$ 760,00 |
| PIS/COFINS a débito total | R$ 925,00 |
| Custos/despesas | R$ 4.000,00 |
| PIS/COFINS a crédito | R$ 370,00 |
| **PIS/COFINS a pagar** | **R$ 555,00** |
| **Alíquota efetiva/média** | **5,55%** |

*(Regra explícita — pág. 15)*

## 2. ICMS (tributo estadual) *(pág. 16)*
- Art. 155 da Constituição Federal; alíquotas variáveis por estado/DF.
- Cobrado diretamente na conta; distribuidora repassa ao estado.
- **Cálculo "por dentro"** (imposto embutido): o impacto efetivo é maior que a alíquota nominal. *(Regra explícita — pág. 16)*
- Exemplo dado: alíquota nominal 25% → impacto real ≈ **33%**; conta de R$ 100 com imposto direto iria para R$ 125, mas com imposto embutido vai para **R$ 133**. *(Regra explícita — pág. 16)*

## 3. CIP — Contribuição de Iluminação Pública (tributo municipal) *(pág. 16)*
- Art. 149-A da Constituição; forma de cobrança e base definidas por **lei municipal**.
- A concessionária apenas **arrecada e repassa** ao município; o repasse ocorre **mesmo que o consumidor não pague** a conta. *(Regra explícita — pág. 16)*

## Relevância para o projeto
- Estes tributos **não fazem parte da base tarifária da ANEEL** (que é líquida). Para o MVP ACR×ACL, a comparação de custo é feita **sem tributos**. *(Interpretação — coerente com composicao_tarifa.md e docs/premissas.md)*
- Se, futuramente, quisermos projetar o **custo final na fatura**, o ICMS "por dentro" e o PIS/COFINS não-cumulativo seriam os itens a modelar — fora do MVP. *(Não determinado para a base atual / pendência futura)*
