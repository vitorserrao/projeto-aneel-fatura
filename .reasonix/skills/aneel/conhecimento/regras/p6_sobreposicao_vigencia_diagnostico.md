# P6 — Diagnóstico da sobreposição de vigências (dados reais)

> Análise executada no banco real (504.337 componentes, carga `carga_aneel` id=1)
> para subsidiar a definição da **regra de desempate** (P6) antes de implementar
> o cálculo de fatura do Grupo A.
> **Status:** diagnóstico concluído; **regra a aprovar**.

## 1. O que é a sobreposição

Quando agrupamos por **contexto tarifário completo** — distribuidora + subgrupo +
modalidade + base tarifária + componente + unidade + posto + início/fim de vigência —
há grupos com **mais de uma linha**, distinguidos apenas pelo campo `detalhe`.

## 2. Magnitude (números reais)

- **135.905 grupos** com mais de uma linha no mesmo contexto.
- Natureza (pares de `detalhe`), por quantidade de grupos:

| Detalhes no grupo | Grupos |
|---|---|
| `Não se aplica` + `SCEE` | 45.346 |
| `Não se aplica` (duplicado exato) | 41.295 |
| `APE` + `Não se aplica` | 38.552 |
| `APE` + `Não se aplica` + `SCEE` | 7.860 |
| `TIPO 01` + `TIPO 02` | 2.342 |
| `Cooperativas autorizadas` + `Não se aplica` | 416 |
| `APE` + `Cooperativas autorizadas` + `Não se aplica` | 82 |
| `<500GWh` + `Não se aplica` | 12 |

- Valores dentro do grupo: **91.113 grupos com valores DIFERENTES** e
  **44.792 com valores IGUAIS**.

## 3. Casos concretos analisados

### 3.1 `APE` vs `Não se aplica` (23.019 grupos comparáveis)
| Situação | Grupos |
|---|---|
| Valores **iguais** | 23.019 |
| `Não se aplica` **maior** | 14.533 |
| `APE` maior | **2** |

→ Predomina: **`Não se aplica` é o valor maior**; `APE` raramente difere.

### 3.2 `SCEE` vs `Não se aplica` (26.714 grupos comparáveis)
| Situação | Grupos |
|---|---|
| `Não se aplica` **maior** | 17.030 |
| Valores iguais | 9.684 |

→ Mesmo padrão: **`Não se aplica` é o valor maior**.

### 3.3 Exemplo concreto (CPFL JAGUARI, A2, Azul, TUSD kW Ponta, 2010-02-03)
```
detalhe='APE'            valor=20,64
detalhe='Não se aplica'  valor=20,64   (iguais)
```

## 4. Por que isso importa no cálculo

O motor hoje **soma todas as linhas vigentes**. Quando há duas linhas no mesmo
contexto, a parcela é **somada duas vezes**:

```
TUSD DEMANDA PONTA  qtd=1000  tarifa=20,64  custo=20.640   ← linha "Não se aplica"
TUSD DEMANDA PONTA  qtd=1000  tarifa=20,64  custo=20.640   ← linha "APE" (duplicada)
                                          TOTAL DA PARCELA = 41.280  (DOBRO)
```

Impacto observado no teste real: fatura de CPFL JAGUARI A2 Azul (2010-06-01)
deu **R$ 80.160,00** com parcelas duplicadas — o valor correto seria cerca de
**metade**, se as duplicatas forem o mesmo conceito.

## 5. O que o `detalhe` significa (domínio ANEEL)

- `Não se aplica` — tarifa geral (sem detalhe específico).
- `APE` — **A**gente **P**róprio/**E**special (autoprodutor/APE) — detalhamento de
  um caso específico.
- `SCEE` — Sistema de Compensação de Energia Elétrica (geração distribuída).
- `TIPO 01` / `TIPO 02`, `Cooperativas autorizadas`, `<500GWh` — recortes específicos.

**São recortes distintos**, não necessariamente duplicatas exatas. A escolha de
qual usar é uma **decisão de domínio** (qual detalhe corresponde ao perfil do
consumidor simulado).

## 6. Propostas de regra de desempate (a escolher)

### Opção A — Filtrar por `detalhe = 'Não se aplica'` por padrão
Para um consumidor "típico" (sem APE/SCEE), usar **apenas** a linha
`detalhe = 'Não se aplica'`.
- **A favor:** reflete o consumidor comum; coincide com a maioria dos casos;
  elimina o dobro.
- **Contra:** ignora os recortes APE/SCEE (que ficam fora do MVP de qualquer forma).

### Opção B — Parametrizar o `detalhe` no perfil
O perfil informa o `detalhe` desejado (`Não se aplica` por padrão).
- **A favor:** flexível; permite simular APE/SCEE no futuro.
- **Contra:** mais um campo no contrato; exige o usuário saber o detalhe.

### Opção C — Preferir a linha específica (`APE`/`SCEE`) quando existir
- **Contra:** os dados mostram que `Não se aplica` costuma ser o valor maior/geral;
  essa regra inverteria a maioria.

### Opção D — Recusar quando houver ambiguidade não resolvida
Manter o comportamento atual (`AmbiguidadeTarifaria`), obrigando o filtro explícito.
- **A favor:** nunca inventa.
- **Contra:** o cálculo de fatura simplesmente falha nesses casos.

## 7. Recomendação

**Opção A + B combinadas:** filtrar por `detalhe` no perfil, com **padrão
`'Não se aplica'`** — resolve o dobro nos casos comuns e deixa a porta aberta
para APE/SCEE depois. Requer:
1. adicionar `detalhe` ao contrato do perfil (schema + core + filtro da query);
2. filtrar `dsc_detalhe = :detalhe` no repositório;
3. teste garantindo que a fatura **não** soma duplicatas.

## 8. Fontes
- Banco real do projeto (tabela `tarifa_aplicacao_componente`).
- Guia da Base de Dados ANEEL (significado de `DscDetalhe`).
