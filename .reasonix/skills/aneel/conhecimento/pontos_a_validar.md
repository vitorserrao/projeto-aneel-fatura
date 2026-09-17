# Pontos que ainda precisam ser validados

> Classificação final: aqui consolidamos os itens que o documento **não** determina ou que dependem de validação regulatória externa, para orientar a implementação (sem presumir).

## 1. Fórmula de faturamento de demanda
- Como aplicar a **demanda** (contratada vs medida, fator de carga, reativos, multas) não consta no documento. *(Não determinado)*
- Ref. do projeto: pendência **P3/P5** (`docs/premissas.md`).

## 2. Mapeamento de `posto` e `unidade` para o contrato do core
- O documento lista valores (`Ponta`, `Fora de Ponta`, `seca/úmida`, `Não se aplica`) e unidades (`R$/kW`=demanda, `R$/MWh`=consumo+TE), mas **não define** como agrupar `posto` em `PONTA`/`FORA PONTA`/`SEM POSTO` para o motor. *(Interpretação necessária / Não determinado)*
- Além do caso "Intermediário" (presente no banco) e o tratamento de "Não se aplica". *(Não determinado)*

## 3. EPI / comparação ACR × ACL
- **Não é abordado no documento**. Toda a fórmula de Preço de Indiferença precisa de fonte regulatória externa. *(Não determinado)*
- Ref. do projeto: pendência **P2** (`docs/premissas.md`).

## 4. Como compor TUSD energia + TE (soma na fatura)
- O documento afirma que a fatura é a "soma das tarifas aplicáveis", mas não detalha **quais** componentes entram em cada situação (te+tuSD, energia+demanda, por posto). *(Regra parcial / lacuna explícita)*

## 5. Tratamento de SCEE/Componentes (GDII/GDIII)
- O documento lista parcelas Fio A/Fio B, mas **não** fornece a fórmula de faturamento da energia compensada. *(Não determinado)*
- SCEE está fora do MVP, mas o conhecimento deve ficar registrado para evolução.

## 6. Aplicação de tributos
- Documento informa base **líquida (sem tributos)**, mas não fornece alíquotas/fórmula dos tributos. *(Não determinado)*

## 7. Elegibilidade de modalidades por perfil (Azul/Verde/Convencional/Geração)
- O documento mostra as modalidades e subgrupos, mas **não determina** o critério de enquadramento de um consumidor a cada modalidade (fonte regulatória necessária). *(Não determinado)*
- Ref. do projeto: pendência **P4** (`docs/premissas.md`).

## 8. Convencional ainda aplicada (cronologia)
- Exemplos (Roraima 2025) mostram exceções; a regra geral de quando a Convencional se aplica precisa de fonte. *(Não determinado)*

## 9. Histórico anterior a 2010
- Documento remete a PDFs de resoluções (não estruturado). Confirmar se nosso banco cobre ou se é fora do escopo. *(Não determinado)*

## 10. Bandeiras tarifárias
- Não mencionadas no documento. *(Não determinado — fora do MVP)*
