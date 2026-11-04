# Submissão XXIX SNPTEE — Resumo (NGN)

> Destino: GCR — Grupo de Estudo de Comercialização, Economia e Regulação
> (tema de regulação / revisão tarifária) · **Submeter para o NGN: Sim**
> Prazo da chamada: 11/10/2026 · Faixa exigida: 500 a 700 palavras.

## Opções de título

1. Análise e reenquadramento tarifário de consumidores potencialmente livres:
   ferramenta computacional validada em faturas reais
2. Do regulamento ao centavo: sistema computacional de análise de enquadramento
   tarifário e apoio à decisão entre modalidades e entre ACR e ACL
3. Enquadramento tarifário no Grupo A: ferramenta computacional para análise de
   modalidades e decisão ACR × ACL validada contra faturas reais

## Palavras-chave (sugestão)

Enquadramento tarifário; modalidades tarifárias; ACR e ACL; REN 1.000/2021;
validação com faturas reais

## Resumo (texto para copiar no sistema)

<!-- INICIO_RESUMO -->

O enquadramento tarifário é uma decisão de efeito financeiro direto e duradouro para consumidores do Grupo A: identificar as modalidades horárias a que tem direito, comparar seus custos e, quando elegível, avaliar a migração para o Ambiente de Contratação Livre (ACL). Erros nessa análise, como um componente de demanda mal tratado, uma modalidade inadequada ao perfil de carga ou uma premissa tributária incorreta, podem levar a uma decisão equivocada, cujo efeito só se revela ao longo de vários ciclos. Este trabalho apresenta uma ferramenta computacional de apoio à análise e ao reenquadramento tarifário de consumidores potencialmente livres, com foco na reprodução fiel da fatura atual e na comparação objetiva das modalidades aplicáveis.

A ferramenta foi estruturada em camadas independentes, decisão que organiza o desenvolvimento e a validação. O núcleo concentra as regras de cálculo e é estritamente determinístico: não depende de banco de dados, rede ou interface, recebe as tarifas como dados e devolve sempre o mesmo resultado, o que o torna diretamente testável. A camada de dados ingere e mantém as tarifas de aplicação da ANEEL, com controle de vigência, subgrupo e modalidade. Acima dela, os serviços orquestram os casos de uso e uma API REST expõe o cálculo para uma interface web própria, que reconstrói a fatura linha a linha, compara modalidades e apresenta o resultado ao usuário. A implementação usa Python e PostgreSQL, com testes automatizados unitários e de integração.

As regras adotadas seguem a Resolução Normativa ANEEL nº 1.000/2021 e a documentação técnica oficial, e nenhuma fórmula é admitida por suposição: quando uma vigência é ambígua ou um posto não pode ser mapeado, o sistema devolve erro explícito em vez de arbitrar uma solução. O sistema calcula e compara as modalidades do Grupo A — Azul e Verde, com elegibilidade da Verde restrita aos subgrupos A3a, A4 e AS e demanda única — e também a opção pela tarifa do Grupo B, quando aplicável ao perfil. A comparação considera a demanda faturável como o maior valor entre contratada e medida, a ultrapassagem, o consumo de energia em ponta e fora de ponta, os reativos excedentes e a recomposição tributária, produzindo um ranking determinístico de custo que indica a modalidade mais econômica para o perfil analisado.

A validação teve duas frentes. A primeira é um conjunto de mais de 130 testes automatizados, que cobre as regras de elegibilidade, os componentes de custo e a independência do núcleo. A segunda é o confronto com faturas reais de consumidores do Grupo A — Copel, CEMIG e Equatorial —, com critério de aceite de R$ 0,05 por linha e R$ 1,00 no total; as linhas de energia, demanda, ultrapassagem e reativos excedentes foram reproduzidas com desvios de centavos e, no caso Copel, o total de R$ 9.854,93 foi reconstruído em R$ 9.854,96. Depois de ajustar as regras uma única vez, faturas de outras unidades e competências foram reproduzidas na mesma tolerância, sem calibração por caso. O processo expôs duas práticas que o regulamento não evidencia de forma isolada: a parcela de demanda contratada e não utilizada é isenta de ICMS em parte das distribuidoras, e a tributação do reativo excedente varia entre elas; um caso com PIS e COFINS destacados em linhas separadas (Enel) permanece documentado como pendência.

Como resultados, a ferramenta entrega a fatura auditável linha a linha, a identificação da modalidade de menor custo e uma base reprodutível para responder à questão central do projeto: como o enquadramento tarifário e a evolução das tarifas do ACR afetam a atratividade da migração para o ACL. As limitações são declaradas no próprio resultado, como a aproximação mensal na cobrança de reativos sem medição horária. A continuidade prevista é a execução do motor sobre uma amostra ampliada de perfis, para estimar o percentual de consumidores mal enquadrados e a economia potencial, seguida do cálculo do preço de indiferença e de sua versão probabilística por simulação de Monte Carlo, que informe não apenas quanto se economizaria, mas com que probabilidade. Conclui-se que rastrear cada regra em fonte oficial e validar o resultado contra a fatura efetivamente paga produz um instrumento confiável para o reenquadramento tarifário e para a decisão de migração.

<!-- FIM_RESUMO -->

## Observações

- O texto acima é a versão para colar no campo "Resumo" do sistema.
- Coautores precisam estar cadastrados no evento para serem vinculados por e-mail;
  coautores não cadastrados são excluídos na submissão.
- Após o prazo de alteração dos resumos, o título não poderá ser modificado na
  fase de Informes Técnicos — escolher o título com cuidado agora.
