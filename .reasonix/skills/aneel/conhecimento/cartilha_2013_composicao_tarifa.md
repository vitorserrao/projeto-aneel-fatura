# Cartilha 2013 — Composição da tarifa

> Fonte: `PorDentrodaContadeLuz_2013.pdf` (ANEEL, 6ª edição, março 2013).
> Classificação: *Regra explícita* / *Interpretação* / *Não determinado*.

## 1. Os três custos que a tarifa embute *(pág. 9)*
- **Energia gerada** (compra de energia).
- **Transporte** da energia até as unidades consumidoras (transmissão + distribuição).
- **Encargos setoriais**. *(Regra explícita — pág. 9)*

## 2. Além da tarifa: tributos *(pág. 9)*
- Incidem na conta de luz: **PIS/COFINS** (federal), **ICMS** (estadual) e **CIP** (municipal). *(Regra explícita — pág. 9)*
- A base de dados tarifária representa os valores **líquidos** (sem tributos na fatura final). *(Interpretação — consistente com o outro documento)*

## 3. Exemplo de composição em R$ 100 de conta *(pág. 10)*
Antes da Lei nº 12.783/2013 (revisão extraordinária):
- Compra de energia: **35,80**
- Transmissão: **6,70**
- Distribuição (Parcela B): **23,60**
- Encargos: **9,50**
- Tributos (ICMS, PIS, COFINS): **24,50** *(Regra explícita — pág. 10)*

Depois da redução média de 20,2% (efeito da Lei 12.783/2013):
- Compra de energia: **30,20**
- Transmissão: **2,60**
- Distribuição: **23,60**
- Encargos: **3,90**
- Tributos: **19,50** *(Regra explícita — pág. 10–11)*

## 4. Quando a conta chega ao consumidor *(pág. 10)*
- O consumidor paga pela: compra da energia (gerador), transmissão (transmissora), distribuição (distribuidora), **encargos setoriais e tributos**. *(Regra explícita — pág. 10)*

## 5. Relevância para o projeto
- Nos cálculos ACR/ACL do MVP, a tarifa que temos disponível na base **não inclui tributos** — portanto a comparação de custo é sobre os valores regulatórios líquidos de TUSD/TE, sem PIS/COFINS/ICMS/CIP. *(Interpretação — alinhada ao fora-do-MVP definido em docs/premissas.md)*
