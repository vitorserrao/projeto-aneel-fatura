# Projeto anterior — Fluxo consolidado do projeto

## Fluxo geral (ENTRADAS → PARÂMETROS → CÁLCULOS → RESULTADOS)

```
ENTRADAS (Painel Inicial)
  distribuidora, subgrupo, modalidade, REH, datas de leitura
  demanda faturada/contratada por posto (P/FP)
  consumo por posto (P/FP), reativos
  tributos: PIS, COFINS, ICMS, CIP/COSIP
  bandeira, % mês, % intermediário/FP, tipo ICMS (fora/dentro)
        │
        ▼
PARÂMETROS (constantes + banco)
  limites: 112,5 kVA (comer B) e 300 kW (Conv. Binômia)
  base de tarifas ANEEL 2010–2025 (vigência)
        │
        ▼
PROCESSAMENTO (filtra tarifa por distrib./REH/subgrupo/modalidade/vigência)
        │
        ▼
CÁLCULO (Fatura - 1/2): para cada modalidade
  monta linhas: TUSD demanda, TUSD energia, TE, bandeira,
                ultrapassagem, reativos, CIP, outros
  tarifa_com_imposto = tarifa / ((1−PIS−COFINS)×(1−ICMS))
  valor = quantidade × tarifa_com_imposto
        │
        ▼
RESULTADO
  total R$ por modalidade (Azul, Verde, Conv.Binômia, Conv.Monômia, Branca)
  comparação e marcação de modalidade indisponível
```

## Fluxo do SCEE (Calculador de Porcentagens)
```
Componentes tarifários (Fio A: TUSD RB/FR/CONEXÃO/CUSD/TUSDG; Fio B; encargos; perdas)
        │
        ▼
TUSD total vs TUSD sem Fio A (por subgrupo/modalidade/posto)
        │
        ▼
%TUSD (desconto) = TUSD_sem_Fio_A / TUSD_total
   -> aplicado à energia compensada (GD I/II/III com trajetória temporal)
```

## Observações
- O `Painel Inicial`, `Processamento de Dados` e `Fatura - 1/-2` são a espinha dorsal do simulador Grupo A.
- O `SCEE` é calculado em ferramenta separada, a partir de componentes tarifários por distribuidora.
