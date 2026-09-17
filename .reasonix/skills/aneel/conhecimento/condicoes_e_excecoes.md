# Condições e exceções

> Fonte: `Base de Dados e Análise das Tarifas das Distribuidoras de Energia Elétrica.pdf` (Guia Básico ANEEL).
> Classificação: *Regra explícita* / *Interpretação* / *Não determinado*.

## 1. Tarifa que chega ao consumidor *(pág. 2)*
- Entre `Base Econômica` e `Tarifa de Aplicação`, **o valor que efetivamente chega ao consumidor é o da Tarifa de Aplicação**. *(Regra explícita)*

## 2. Grupo A vs Grupo B (classes) *(pág. 2)*
- Grupo A → geralmente classe "Não se aplica".
- Grupo B → geralmente classe "Residencial". *(Regra explícita)*

## 3. SCEE — Sistema de Compensação *(pág. 1, 3, 5)*
- Para consumidores com SCEE, o painel **Componentes Tarifárias** é o de maior interesse. *(Regra explícita — pág. 1)*
- Para GDII/GDIII, verificar parcelas Fio A/Fio B; "a TUSD não se aplica e a TE do tipo SCEE é consultada no painel TE e TUSD". *(Regra explícita — pág. 5)*

## 4. Modalidade Convencional (Grupo A) *(pág. 4, 6)*
- Não consta mais nas modalidades atuais da ANEEL, **mas algumas distribuidoras ainda aplicam**. *(Regra explícita)*
- Exemplo: Roraima Energia (REH 3.434/2025). *(Regra explícita — pág. 6)*

## 5. Períodos seca/úmida *(pág. 4, 10)*
- Deixaram de ser aplicáveis **ao final de 2014** (última: Cermoful REH 1.629/2013). *(Regra explícita)*

## 6. Histórico anterior a 2010 *(pág. 1)*
- Acessado por **links para PDFs** das resoluções (não em tabela interativa). *(Regra explícita)*

## 7. Distribuidoras incorporadas/extintas *(pág. 4)*
- Algumas não existem mais ou foram incorporadas; aparecem com nomes distintos dos originais. *(Regra explícita)*
- No nosso banco: sigla não é identidade única — CNPJ é (caso RGE/Sulgipe etc.). *(Interpretação — decisão nossa de projetojá validada)*

## 8. Tarifas com valores negativos *(pág. 6–7)*
- Ocorrem (ex.: TUSD -122,63 R$/MWh; TE -289,92 R$/MWh). São dados reais a preservar. *(Regra explícita + decisão nossa de ingestão)*

## 9. Acessantes especiais *(pág. 2, 8)*
- Existem ~855 acessantes especiais; na discretização de análise do documento, foram **desconsiderados**, focando no Grupo A. *(Regra explícita — pág. 8)*

## 10. Fora do escopo do MVP (decisão nossa já registrada)
- Bandeiras tarifárias, MMGD/SCEE, curva de carga real/CTR, integração automática com ACL/PLD/CCEE — documentados em `docs/premissas.md`. *(Regra do projeto; não do PDF)*
