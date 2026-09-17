# PRORET 7 — Componentes e funções de custo (TUSD e TE)

> Fonte: PRORET 7.1 (Figuras 1/2 e §6/§8), complementado por 7.2 e 7.3.
> Classificação: *Regra explícita* / *Interpretação* / *Não determinado*.

## 1. Funções de custo que formam a tarifa *(7.1, pág. 2)*
- Custo regulatório decomposto nas funções: **Transporte, Perdas, Encargos e Energia comprada para revenda**. *(Regra explícita)*
- Estas agregam-se para formar **TUSD** e **TE**. *(Regra explícita)*

## 2. Composição da TUSD *(7.1, §6, pág. 7–8)*
TUSD = **TRANSPORTE + PERDAS + ENCARGOS + OUTROS**. *(Regra explícita — 7.1 pág. 7)*

### TUSD TRANSPORTE
- **FIO A** (ativos de terceiros):
  - Rede Básica, Fronteira, CUSD, CONEXÃO D, CONEXÃO T (compõem FIO A).
- **FIO B** (ativos próprios da Parcela B):
  - CAA (custo anual dos ativos) e CAOM (administração, operação e manutenção). *(Regra explícita — 7.1 pág. 7)*

### TUSD ENCARGOS
- P&D_EE, TFSEE, ONS, CDE, PROINFA, CDE CONTAS (COVID/Escassez Hídrica). *(Regra explícita — 7.1 pág. 7)*

### TUSD PERDAS
- Perdas técnicas; perdas não técnicas; perdas na Rede Básica (associadas às perdas regulatórias); **Receitas Irrecuperáveis**. *(Regra explícita — 7.1 pág. 7)*

### TUSD OUTROS
- Subvenção D < 350; Outros. *(Regra explícita — 7.1 pág. 7)*

## 3. Composição da TE *(7.1, §8, pág. 9–10)*
TE = **ENERGIA + TRANSPORTE + PERDAS + ENCARGOS + OUTROS**. *(Regra explícita — 7.1 pág. 9–10)*

- **TE ENERGIA**: compra para revenda (ACR, Itaipu, geração própria, supridor, GD). *(Regra explícita — pág. 9)*
- **TE TRANSPORTE**: Itaipu + Rede Básica de Itaipu. *(Regra explícita — pág. 10)*
- **TE PERDAS**: perdas na Rede Básica sobre o mercado de referência de energia. *(Regra explícita — pág. 10)*
- **TE ENCARGOS**: ESS/EER, P&D_EE, CFURH, TE CDE (COVID/Escassez), CDE ELET, CDE GD. *(Regra explícita — pág. 9–10)*
- **TE OUTROS**: Subvenção D < 350; Outros. *(Regra explícita — pág. 10)*

## 4. Figuras de referência (mapa visual)
- **Figura 1 (7.1 pág. 8)** — funções e componentes da TUSD: TUSD → TRANSPORTE (FIO A: Rede Básica/Fronteira/CUSD/CONEXÃO D/CONEXÃO T; FIO B), PERDAS (técnicas, não técnicas, perdas RB/D, receitas irrecuperáveis), ENCARGOS (TFSEE, ONS, P&D_EE, CDE, PROINFA, CDE CONTAS), OUTROS (Subvenção D<350, Outros).
- **Figura 2 (7.1 pág. 10)** — funções e componentes da TE: TE → ENERGIA, TRANSPORTE (Itaipu/RB Itaipu), PERDAS (RB sobre cativo), ENCARGOS (CFURH, ESS/EER, P&D_EE, TE CDE, CDE ELET, CDE GD), OUTROS (Subvenção D<350, Outros).

## 5. Incidências/exceções por componente *(7.1 §7/§9)*
- TUSD: exceções para distribuidoras, baixa renda, autoprodução, geradoras, Desconto Social ≤120 kWh. *(Regra explícita — 7.1 pág. 8)*
- TE: exceções para suprimento (CCE), Itaipu, baixa renda, SCEE (não incidem ENERGIA e TRANSPORTE), Desconto Social ≤120 kWh. *(Regra explícita — 7.1 pág. 10–11)*

## 6. Relação com nosso banco (dado real)
- Nosso banco armazena as tarifas **já publicadas** (`dsc_base_tarifaria`: `Tarifa de Aplicação` / `Base Econômica`), não os componentes individuais. *(Interpretação)*
- As funções de custo/componentes são a camada **inferior** da estrutura tarifária; para o MVP (usar TUSD/TE já publicadas), **não** precisamos decompor. *(Interpretação)*
- Componentes/incidências serão necessários **somente** se evoluirmos para SCEE/fatura detalhada. *(Não determinado para o MVP)*
