# SKILL — ANEEL Tarifas (base de conhecimento consolidada)

## Origem
Conhecimento extraído de:
1. **Documentos oficiais da ANEEL** (PRORET 7.1/7.2/7.3, cartilha "Por Dentro da Conta de Luz" 2013, Guia Base de Dados) — `fontes/`.
2. **Projeto anterior do GESE/IFSC** de Kevin Wu (planilhas Excel, sem Python) — `C:\Users\vitor\Downloads\OneDrive_2026-09-10\Kevin Wu`.
3. **Pesquisa em fontes oficiais** (ANEEL / Governo Federal) — REN 1.000/2021, MME/ANEEL — para fechar pendências do motor (ver `regras/ren1000_2021_faturamento.md`).
4. **Material didático do IFSC** — aula "Ambientes de Comercialização e Tarifas" (Prof. Pedro César C. Vieira, Regulação Técnica e Econômica, 2025) — ver `regras/ambientes_comercializacao_e_tarifas_aula.md`.

## Finalidade
Essa base serve para:
- estudar a metodologia anterior;
- compreender cálculos e fórmulas (fatura ACR, tributos, SCEE);
- reproduzir casos de referência;
- validar o novo sistema computacional (motor/tarifas/otimização/EPI);
- comparar resultados do novo código com os do projeto anterior e com as regras oficiais.

## Estrutura da base (`conhecimento/`)
- `projeto_anterior/` — visão geral, estrutura de arquivos, fluxo do projeto.
- `calculos/` — fórmulas Excel (tributos, fatura, SCEE) e cálculos consolidados.
- `regras/` — regras de negócio identificadas + **`ren1000_2021_faturamento.md`** (regras oficiais REN 1.000/2021) + **`ambientes_comercializacao_e_tarifas_aula.md`** (ACR/ACL, abertura de mercado, fórmulas das modalidades, tributos, bandeiras) + `pontos_pendentes_pesquisa.md`.
- `metodologia/` — metodologia do projeto anterior.
- `validacao/` — casos de teste e resultados de referência.
- Arquivos `pr7_*.md`, `cartilha_2013_*.md`, `*_tarifarios.md` (documentos oficiais, processados antes).

## Regra fundamental
**O projeto anterior NÃO deve ser considerado automaticamente como verdade.**

Quando uma fórmula ou regra for reutilizada:
1. localizar sua origem (registrada como `Arquivo → Aba → Célula`);
2. entender a lógica;
3. registrar a premissa;
4. verificar a aplicabilidade ao novo projeto (regras oficiais e dados ANEEL);
5. criar um caso de teste;
6. comparar resultados;
7. registrar divergências.

## Hierarquia de confiança
1. Legislação e regulamentação oficial.
2. Dados oficiais da ANEEL.
3. Documentação técnica oficial (PRORET etc.).
4. Metodologia definida para o novo projeto.
5. Conhecimento extraído do projeto anterior (Kevin Wu).
6. Inferências.

Se houver conflito com fonte oficial, registrar explicitamente:
```
Projeto anterior: ...
Fonte oficial: ...
Diferença: ...
Impacto: ...
```

## Rastreabilidade
Todo conhecimento importante deve indicar:
```
Fonte: Arquivo → Aba → Célula
Conhecimento: ...
Interpretação: ...
Uso futuro: ...
```

## Principais regras já identificadas (resumo)

### Oficiais (REN 1.000/2021 — prioridade 1) — ver `regras/ren1000_2021_faturamento.md`
- **Demanda faturável** = maior entre **contratada** e **medida**.
- **Ultrapassagem** (tolerância **5%**) = `[PAM − PAC] × 2 × VD_ult`.
- **Reativos:** fator de potência limite **0,92**; excedente cobrado.
- **Elegibilidade:** Azul = todos A (obrig. A1-A3); **Verde = A3a, A4, AS**;
  Branca = B (vedada baixa renda/IP/pré-pagamento); Convencional Binômia extinta.
- **Verde** = demanda **única**; **Azul** = demanda ponta + fora ponta.
- **Intermediário** = exclusivo da Branca (Grupo B) ⇒ **fora do Grupo A**.
- **Tributos (conta oficial):** `Tarifa / (1 − PIS − COFINS − ICMS) + CIP`.

### Do projeto anterior (prioridade 5) — ver `calculos/formulas_excel.md`
- **Tributo "por dentro" (Kevin Wu):** `tarifa / ((1−PIS−COFINS) × (1−ICMS))`
  → ⚠️ **conflito com a fórmula oficial**; prevalece a oficial.
- **Valor** = `quantidade × tarifa_com_imposto`.
- **SCEE:** `%TUSD = TUSD_sem_Fio_A / TUSD_total`.
- **Postos/secas-úmidas** antes de 2014.

### Pendências (sem fonte oficial) — ver `regras/pontos_pendentes_pesquisa.md`
- P6 precedência de vigência sobreposta; P7 arredondamento; P2 fórmula do EPI
  (pista metodológica: GESE "Preço de indiferença").

### Material didático IFSC (aula RTE) — ver `regras/ambientes_comercializacao_e_tarifas_aula.md`
- **ACR × ACL:** Decreto 5.163/2004; consumidor livre ≥ 0,5 MW; especial 0,5–1,0 MW (fontes incentivadas).
- **Abertura do mercado:** 2024 (Grupo A) → 2026 (B3/B4) → 2028 (B1/B2).
- **TF = TE + TUSD**; no ACL o consumidor segue pagando o uso da rede.
- **Fórmulas Azul/Verde** (consumo por posto; demanda faturável = máx(medida; contratada)).
- **Ultrapassagem** = `2 × VR × (PAM − PAC)` quando excede 5%.
- **Reativos:** fator de potência < 0,92; 6h capacitivas (0h–6h) e demais indutivas.
- **Bandeiras** (REN 479/2012): verde 0; amarela 0,01874; vermelha 1 = 0,03971; 2 = 0,09492; escassez 0,1420 (R$/kWh, sem tributos).
- **Tarifa Social B1:** 65%/40%/10% por faixa; 100% até 50 kWh (indígenas/quilombolas). Mínimo faturável B: 30/50/100 kWh.
- ⚠️ **Tributos (forma multiplicativa):** `Tarifa / [(1 − (PIS+COFINS)/100) × (1 − ICMS/100)]` — **divergente** da fonte oficial aditiva (ver conflitos).
