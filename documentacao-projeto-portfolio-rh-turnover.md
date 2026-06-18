# Projeto: Diagnóstico de Turnover - Grupo Avelar

## O cenário

O Grupo Avelar é uma rede varejista fictícia com lojas em sete estados, cerca de 4.200 funcionários entre operação de loja, centros de distribuição e administrativo. Nos últimos dois trimestres, o turnover voluntário subiu de forma perceptível e chegou à pauta da diretoria. A área de Pessoas e Cultura não tem hoje nenhum painel consolidado: os números de desligamento aparecem soltos em planilhas, cada gestor regional interpreta os dados de um jeito, e ninguém sabe com confiança em quais áreas o problema está concentrado nem por quê.

## O pedido

Patrícia Nogueira, Diretora de Pessoas e Cultura, encaminhou a seguinte mensagem para a área de dados:

"Preciso entender o que está acontecendo com o turnover antes da reunião de conselho do mês que vem. Hoje eu só tenho uma planilha com os desligamentos do mês, sem comparação histórica e sem cruzar com nada. Queria saber: em quais áreas e cargos a saída está concentrada, se tem relação com salário, distância de casa, hora extra ou avaliação de desempenho, e se dá pra estimar o impacto financeiro disso. Não precisa ser nada definitivo, mas precisa ser confiável pra eu levar pro conselho."

## Perguntas de negócio que o dashboard precisa responder

1. Qual a taxa de turnover geral e por departamento/cargo, e como ela evoluiu nos últimos períodos?
2. Existe correlação entre saída e satisfação no trabalho, hora extra ou distância de casa?
3. Faixas salariais ou tempo de empresa influenciam a saída?
4. Quais cargos têm maior risco de saída e qual o custo estimado de reposição?
5. Os gestores regionais estão certos ao culpar "o mercado" ou existe um padrão interno mais específico?

## Base de dados

Dataset **IBM HR Analytics Employee Attrition** (Kaggle, gratuito, ~1.470 funcionários):

- **Fonte 1 : Cadastro/Folha**: idade, departamento, cargo, salário, tempo de empresa, distância de casa.
- **Fonte 2 : Avaliação de desempenho**: nota de performance, horas extras, nível de envolvimento.
- **Fonte 3 : Pesquisa de clima**: satisfação no trabalho, satisfação com o ambiente, equilíbrio vida-trabalho.

## Arquitetura técnica (HTML, sem Fabric/Power BI)

- **Tratamento dos dados**: feito em Python (pandas), junção das três fontes simuladas pela chave de funcionário, a limpeza, o tratamento de nulos e o cálculo prévio das métricas. O resultado final é exportado como um ou dois arquivos JSON já agregados.
- **Front-end**: um único arquivo HTML com CSS e JavaScript, usando uma biblioteca de gráficos via CDN (Chart.js ou Plotly.js). Filtros (por departamento, cargo, período) feitos com JavaScript puro, sem framework.
- **Organização**: pasta `dados/` com os JSONs processados, e `index.html` consumindo esses arquivos.
  
## Métricas a calcular em Python e exibir no dashboard

- Taxa de turnover (geral, por departamento, por cargo)
- Tempo médio de permanência
- Índice médio de satisfação
- % de funcionários em hora extra entre os que saíram vs. os que ficaram
- Custo estimado de turnover (assuma uma premissa simples, tipo 50% do salário anual por substituição, e documente essa premissa)
- Salário médio por faixa de tempo de empresa

## Estrutura do relatório

- Página 1 : Visão executiva: KPIs principais e tendência de turnover no período
- Página 2 : Quem está saindo: cruzamento por departamento, cargo e faixa salarial
- Página 3 : Por que estão saindo: satisfação, hora extra, distância de casa, equilíbrio vida-trabalho
- Página 4 : Impacto financeiro: custo estimado e cargos de maior risco
