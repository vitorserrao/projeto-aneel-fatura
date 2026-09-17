# Cartilha 2013 — Encargos setoriais

> Fonte: `PorDentrodaContadeLuz_2013.pdf` (ANEEL, 6ª edição, março 2013).
> Classificação: *Regra explícita* / *Interpretação* / *Não determinado*.

## Visão geral *(pág. 11)*
- Encargos setoriais são **criados por leis** (Congresso), com valores em resoluções/despachos da ANEEL, e **recolhidos pelas distribuidoras** na conta de luz. *(Regra explícita — pág. 11)*
- A Lei 12.783/2013 **extinguiu a RGR** e **reduziu a TFSEE**. *(Regra explícita — pág. 11)*

## Tabela dos encargos (para que serve / como é calculado)

### 1. CDE — Conta de Desenvolvimento Energético *(pág. 12)*
- Lei 10.438/2002 (alterada pela 12.783/2013).
- Finalidade: descontos em tarifas; subsídios à baixa renda; Luz para Todos; competitividade de eólica/PCH/biomassa/gás/carvão.
- **Como é calculado:** cotas definidas em função dos recursos necessários; Tesouro aporta recursos; custo **rateado por todos os consumidores do SIN**; valor das cotas calculado pela ANEEL. *(Regra explícita — pág. 12)*

### 2. TFSEE — Taxa de Fiscalização *(pág. 12)*
- Lei 9.427/1996 (alterada pela 12.783/2013); Decreto 2.410/1997.
- Finalidade: custear funcionamento da ANEEL.
- **Como é calculado:** paga por todos os consumidores; equivale a **0,4%** do benefício econômico anual (antes 0,5%). *(Regra explícita — pág. 12)*

### 3. PROINFA *(pág. 12)*
- Lei 10.438/2002; Decreto 5.025/2004.
- Finalidade: incentivar eólica/biomassa/PCH.
- **Como é calculado:** rateio dos custos e da energia gerada pelo programa, conforme **Plano Anual da Eletrobras**. *(Regra explícita — pág. 12)*

### 4. RGR — Reserva Global de Reversão *(pág. 13)*
- Decreto 41.019/1957.
- Finalidade: recursos para reversão de instalações e financiamento de expansão/melhoria.
- **Como era/está:** a partir da Lei 12.783/2013, **as distribuidoras ficam desobrigadas de recolher**. *(Regra explícita — pág. 13)*

### 5. CFURH — Compensação Financeira hídrica *(pág. 13)*
- Constituição Federal 1988.
- Finalidade: compensar União/estados/municípios pelo uso da água/terras.
- **Como é calculado:** **6,75%** × valor mensal de energia produzida (MWh) × **TAR** (Tarifa Atualizada de Referência). Distribuição: 45% municípios, 45% estados, 10% União (3% MMA, 3% MME, 4% FNDCT). *(Regra explícita — pág. 13)*

### 6. ESS — Encargos de Serviços do Sistema *(pág. 13)*
- Decreto 2.655/1998.
- Finalidade: aumentar confiabilidade/segurança da oferta.
- **Como é calculado:** custo apurado **mensalmente pela CCEE**, pago por todos os consumidores aos agentes de geração. *(Regra explícita — pág. 13)*

### 7. ONS *(pág. 14)*
- Lei 9.648/1998; Decreto 2.335.
- Finalidade: financiar o Operador Nacional do Sistema Elétrico.
- **Como é calculado:** valor definido **anualmente pelo ONS** e **aprovado pela ANEEL**. *(Regra explícita — pág. 14)*

### 8. P&D / EE *(pág. 14)*
- Lei 9.991/2000; 11.465/2007; 12.212/2010.
- Finalidade: pesquisa científica, tecnológica e eficiência energética.
- **Como é calculado:** distribuidoras aplicam **0,5%** da receita operacional líquida; outros agentes **1%** em P&D. *(Regra explícita — pág. 14)*

### 9. EER — Encargo de Energia de Reserva *(pág. 14)*
- Lei 10.848/2004; Res. Normativa 337/2008.
- Finalidade: cobrir custos da contratação de energia de reserva (administrativos/financeiros/tributários).
- **Como é calculado:** rateio entre usuários finais do SIN (incluindo consumidores livres e autoprodutores na parcela da interligação); definido **mensalmente pela CCEE**. *(Regra explícita — pág. 14)*

## Relevância para o projeto
- Esses encargos **compõem parte da tarifa** (a base de TUSD/TE já os embute). Para o MVP (TUSD/TE agregadas), não precisamos decompor os 8/9 encargos — a menos que se implemente **Componentes Tarifários** (SCEE) futuramente. *(Interpretação — nosso escopo atual é TUSD/TE agregada)*
