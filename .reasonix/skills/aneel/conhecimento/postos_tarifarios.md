# Postos tarifários

> Fonte: `Base de Dados e Análise das Tarifas das Distribuidoras de Energia Elétrica.pdf` (Guia Básico ANEEL).
> Classificação: *Regra explícita* / *Interpretação* / *Não determinado*.

## 1. Valores de posto disponíveis *(pág. 2)*
- Ponta
- Fora de Ponta
- Intermediário
- Ponta seca / Ponta úmida
- Fora Ponta seca / Fora Ponta úmida
- Não se aplica *(Regra explícita — pág. 2)*

## 2. Posto e unidade (quando se aplica) *(pág. 2)*
- A distinção de postos aplica-se principalmente às modalidades **Azul** e **Verde**. *(Interpretação — decorre das discretizações das pág. 9–13)*
- Modalidades **Convencional** e **Geração** usam "sem posto horário" ou "única". *(Regra explícita — pág. 12–13)*

## 3. Períodos seco e úmido (LIV-A / LIV-B) *(pág. 4)*
- Classificação antiga da ANEEL (metodologia anterior) incluía horários de ponta/fora de ponta e **períodos seco e úmido**. *(Regra explícita)*
- **LIV-A (período seco):** 7 ciclos de faturamento consecutivos — **maio a novembro**. *(Regra explícita)*
- **LIV-B (período úmido):** 5 ciclos de faturamento consecutivos — **dezembro de um ano até abril do ano seguinte**. *(Regra explícita)*
- Referência regulatória citada: Resolução ANEEL nº 414/2010. *(Regra explícita)*

## 4. Fim da distinção seca/úmida *(pág. 4, 6, 10)*
- As tarifas com distinção seca/úmida **deixaram de ser aplicáveis ao final de 2014**. *(Regra explícita — pág. 10)*
- Última aplicação com seca/úmida citada: **Cermoful**, REH nº 1.629 de 24/09/2013 (vigência 28/09/2013 a 27/09/2014). *(Regra explícita — pág. 5–6)*

## 5. Relação com a extração atual do banco
- Nosso banco preserva o campo `nom_posto_tarifario` (valores reais: Ponta, Fora ponta, Fora ponta seca/úmida, Ponta seca/úmida, Não se aplica, Intermediário...). *(Interpretação — coberto pelo dataset)*
- A conversão destes valores para o contrato do core (`PONTA`/`FORA PONTA`) é uma decisão pendente (P5/P3) e **não é determinada pelo documento**. *(Não determinado)*
