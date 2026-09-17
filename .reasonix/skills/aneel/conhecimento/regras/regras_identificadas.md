# Projeto anterior — Regras de negócio identificadas

> Separação: **FÓRMULA** (expressão) × **REGRA DE NEGÓCIO** (condição de aplicação).

## 1. Enquadramento por potência
- REGRA: o consumidor é Grupo B se a **potência aparente ≤ 112,5 kVA**; Convencional Binômia se **potência ativa ≤ 300 kW** (parâmetros no Painel Inicial).
- Fórmula: comparação simples com limite.

## 2. Aplicação de tributos
- REGRA: tributação **"por dentro"** (imposto embutido na base), com ICMS multiplicativo e PIS/COFINS somados.
- Fórmula: `tarifa_com_imposto = tarifa / ((1 − PIS − COFINS) × (1 − ICMS))` (Fatura - 1, K20).
- Tipo de cobrança do ICMS configurável: **por fora (1)** ou **por dentro (2)** (Painel Inicial).

## 3. Seleção de modalidade (comparação)
- REGRA: o simulador calcula **todas** as modalidades (Azul, Verde, Convencional Binômia, Convencional Monômia, Branca) para o mesmo perfil e apresenta o total de cada; a modalidade **indisponível** (não praticada pela distribuidora) aparece como texto "Modalidade Tarifária Indisponível...".
- Fórmula: soma de linhas de cobrança por modalidade.

## 4. Sectores seca / úmida (horário de leitura)
- REGRA: para datas de leitura **anteriores a 2014**, a tarifa de energia/TUSD energia é separada por período **seco** e **úmido** (novembro=seca, dezembro=úmida no exemplo); "colocar um SE (data < 2014)" está anotado na planilha.
- Entrada: `% Consumo Mês Atual × Mês Anterior` (proporção entre leituras).

## 5. Postos tarifários
- REGRA: Ponta (P), Intermediário (INT), Fora Ponta (FP). O posto Intermediário é fracionado no FP via parâmetro `% Consumo Intermediário no Período de Fora Ponta` (máx 1, ex.: 0,10).
- Fórmula na aba `Horários P, INT e FP` (distribuído por distribuidora).

## 6. Cobranças adicionais
- REGRA: incluir, quando aplicável: **bandeira tarifária** (adicional R$/kWh por mês), **ultrapassagem de demanda**, **reativos excedentes** (energia kVArh e demanda kVAr), **CIP/COSIP** (fixo), **outros valores** (doações/taxas).
- Fórmula: cada linha é `quantidade × tarifa` e entra no total.

## 7. SCEE (desconto da energia compensada)
- REGRA: na energia compensada (SCEE), a TUSD sofre desconto nos componentes **não associados à energia**; o percentual é a razão entre a **TUSD sem Fio A** e a **TUSD total** (calculador SCEE), variando por subgrupo/modalidade/posto e por geração (GD I/II/III com trajetória temporal).
- Fórmula (conceito): `%TUSD = TUSD_sem_Fio_A / TUSD_total`.

## 8. Correlação Grupo A → Grupo B (correlação de enquadramento)
- REGRA: para atividade econômica (ex.: Comercial/Industrial B3, Iluminação Pública B4), existe correlação de subgrupo/classe/subclasse/posto entre as duas divisões; a planilha usa isso nos casos de reenquadramento/mono/binômio.
