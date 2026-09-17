# Conceitos tarifários

> Fonte: `Base de Dados e Análise das Tarifas das Distribuidoras de Energia Elétrica.pdf` (Guia Básico ANEEL).
> Conclusão das regras: cada item abaixo indica a **classificação** — *Regra explícita* (apresentada no documento), *Interpretação* (leitura motivada, não citação literal) ou *Não determinado* (documento não define).

## 1. Painéis da ferramenta da ANEEL *(pág. 1)*
- **TUSD e TE** — apresenta os valores da Tarifa de Uso do Sistema de Distribuição (TUSD) e da Tarifa de Energia (TE). *(Regra explícita)*
- **Componentes Tarifárias** — apresenta os itens que compõem as tarifas; existem **40 componentes tarifários** (encargos, custos setoriais, itens de ajuste regulatório). *(Regra explícita)*
- **Histórico anterior a 2010** — tarifas antigas via links para PDFs das resoluções; mais antiga: Portaria nº 91 de 07/04/1997 (CPFL Paulista); mais recente do período: REH 1.092/2010 (Sulgipe). *(Regra explícita)*

## 2. TUSD (Tarifa de Uso do Sistema de Distribuição) e TE (Tarifa de Energia)
- São as duas tarifas principais no painel mais utilizado ("TUSD e TE"). *(Regra explícita — pág. 1)*
- Ambas podem ser apresentadas em `R$/MWh` (consumo/TE) e a TUSD também em `R$/kW` (demanda). *(Regra explícita — pág. 2, filtro "Unidade")*

## 3. Base tarifária *(pág. 2)*
- Dois valores: **Base Econômica** e **Tarifa de Aplicação**. *(Regra explícita)*
- **O valor que efetivamente chega ao consumidor é o da Tarifa de Aplicação.** *(Regra explícita — pág. 2)*
- Implicação de projeto: ao calcular o custo do consumidor, priorizar `dsc_base_tarifaria = 'Tarifa de Aplicação'`. *(Interpretação, não citação literal)*

## 4. Tipo de outorga *(pág. 2)*
- Filtro: **concessionária** ou **permissionária**. *(Regra explícita)*

## 5. Distribuidor (Sigla) *(pág. 2)*
- Filtro **Sigla** identifica a distribuidora (ex.: Amazonas Energia, Celesc-DIS, Cemig-D). *(Regra explícita)*
- Até 27/06/2025 constam **115 distribuidoras**. *(Regra explícita)*

## 6. REH (Resolução Homologatória) *(pág. 2)*
- Filtro REH = Resolução Homologatória correspondente à tarifa em vigor. *(Regra explícita)*

## 7. Subgrupo *(pág. 2)*
- A1, A2, A3, A4, A3a, AS, B1, B2, B3, B4. *(Regra explícita)*
- Observação do documento: **a classificação não é idêntica à tradicional da ANEEL** (peculiaridades adicionais). *(Regra explícita — pág. 2)*

## 8. Classe / Subclasse *(pág. 2)*
- Classe = categoria de consumo (Residencial, Rural, Iluminação Pública, ou "Não se aplica"). *(Regra explícita)*
- Grupo A → geralmente "Não se aplica"; Grupo B → geralmente "Residencial". *(Regra explícita)*
- Subclasse = detalhamento (Baixa Renda, Cooperativa de Eletrificação Rural, Serviço Público de Irrigação Rural, Iluminação Pública B4a/B4b). *(Regra explícita)*

## 9. Detalhe *(pág. 2)*
- Informações adicionais: APE, Tipo 01, Tipo 02, Cooperativas autorizadas, <500 GWh, SCEE. *(Regra explícita)*
- Normalmente usa-se "Não se aplica". *(Regra explícita)*

## 10. Acessante *(pág. 2)*
- Define quem acessa a rede (consumidor livre, autoprodutor, concessionária de distribuição, autorizada de geração, importação/exportação etc.). *(Regra explícita)*
- ~855 acessantes especiais cadastrados (no momento do documento). *(Regra explícita)*

## 11. Parcela A e Parcela B *(pág. 7–8)*
- **Parcela A**: custos não gerenciáveis (compra de energia, encargos setoriais, uso da transmissão).
- **Parcela B**: custos gerenciáveis (operação, manutenção e expansão da rede de distribuição). *(Regra explícita — pág. 7)*

## 12. Tributos *(pág. 8)*
- PIS/COFINS, ICMS e CIP incidem na fatura final, mas **a base de dados da ANEEL apresenta apenas os valores líquidos (sem tributos)**. *(Regra explícita)*
- Implicação: nossa ferramenta de cálculo no MVP deve tratar apenas os valores líquidos da base; tributos são fora do escopo. *(Interpretação — coerente com o fora-do-MVP já definido)*
