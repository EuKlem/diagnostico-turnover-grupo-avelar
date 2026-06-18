# Projeto: Diagnóstico de Turnover - Grupo Avelar

## O cenário

O Grupo Avelar é uma rede varejista fictícia com lojas em sete estados, cerca de 4.200 funcionários entre operação de loja, centros de distribuição e administrativo. Nos últimos dois trimestres, o turnover voluntário subiu de forma perceptível e chegou à pauta da diretoria. A área de Pessoas e Cultura não tem hoje nenhum painel consolidado: os números de desligamento aparecem soltos em planilhas, cada gestor regional interpreta os dados de um jeito, e ninguém sabe com confiança em quais áreas o problema está concentrado nem por quê.

## O pedido

Patrícia Nogueira, Diretora de Pessoas e Cultura, encaminhou a seguinte mensagem para a área de dados:

"Preciso entender o que está acontecendo com o turnover antes da reunião de conselho do mês que vem. Hoje eu só tenho uma planilha com os desligamentos do mês, sem comparação histórica e sem cruzar com nada. Queria saber: em quais áreas e cargos a saída está concentrada, se tem relação com salário, distância de casa, hora extra ou avaliação de desempenho, e se dá pra estimar o impacto financeiro disso. Não precisa ser nada definitivo, mas precisa ser confiável pra eu levar pro conselho."

Essa mensagem é o seu ponto de partida. Tudo que você construir deve responder a ela.

## Perguntas de negócio que o dashboard precisa responder

1. Qual a taxa de turnover geral e por departamento/cargo, e como ela evoluiu nos últimos períodos?
2. Existe correlação entre saída e satisfação no trabalho, hora extra ou distância de casa?
3. Faixas salariais ou tempo de empresa influenciam a saída?
4. Quais cargos têm maior risco de saída e qual o custo estimado de reposição?
5. Os gestores regionais estão certos ao culpar "o mercado" ou existe um padrão interno mais específico?

## Base de dados

Use o dataset **IBM HR Analytics Employee Attrition** (Kaggle, gratuito, ~1.470 funcionários, sem dados sensíveis reais). Para que o projeto não pareça "baixei um CSV e fiz um gráfico", divida esse dataset único em três fontes simuladas antes de processar — assim você recria a fragmentação que existe em qualquer empresa real:

- **Fonte 1 - Cadastro/Folha**: idade, departamento, cargo, salário, tempo de empresa, distância de casa.
- **Fonte 2 - Avaliação de desempenho**: nota de performance, horas extras, nível de envolvimento.
- **Fonte 3 - Pesquisa de clima**: satisfação no trabalho, satisfação com o ambiente, equilíbrio vida-trabalho.

Mantenha uma chave (EmployeeNumber) comum às três. Isso te obriga a resolver o join entre fontes na etapa de tratamento em Python, que é exatamente o tipo de problema que aparece em projeto real.

## Arquitetura técnica (HTML, sem Fabric/Power BI)

- **Tratamento dos dados**: feito em Python (pandas), fora do navegador. É aqui que entra a junção das três fontes simuladas pela chave de funcionário, a limpeza, o tratamento de nulos e o cálculo prévio das métricas. O resultado final é exportado como um ou dois arquivos JSON já agregados — o dashboard não deve fazer cálculo pesado no navegador.
- **Front-end**: um único arquivo HTML com CSS e JavaScript, usando uma biblioteca de gráficos via CDN (Chart.js ou Plotly.js). Filtros (por departamento, cargo, período) podem ser feitos com JavaScript puro, sem framework, já que os dados já vêm prontos do JSON.
- **Organização**: pasta `dados/` com os JSONs processados, e `index.html` consumindo esses arquivos. Isso separa a camada de dados da camada de visualização, mesmo trabalhando fora de uma ferramenta de BI.

## Métricas a calcular em Python e exibir no dashboard

- Taxa de turnover (geral, por departamento, por cargo)
- Tempo médio de permanência
- Índice médio de satisfação
- % de funcionários em hora extra entre os que saíram vs. os que ficaram
- Custo estimado de turnover (assuma uma premissa simples, tipo 50% do salário anual por substituição, e documente essa premissa)
- Salário médio por faixa de tempo de empresa

## Estrutura do relatório

- Página 1 — Visão executiva: KPIs principais e tendência de turnover no período
- Página 2 — Quem está saindo: cruzamento por departamento, cargo e faixa salarial
- Página 3 — Por que estão saindo: satisfação, hora extra, distância de casa, equilíbrio vida-trabalho
- Página 4 — Impacto financeiro: custo estimado e cargos de maior risco

## Fluxo de design: do Claude Design ao código

O visual do dashboard será definido antes de qualquer linha de código, seguindo a separação entre exploração visual e produção:

1. **Sistema de design**: montar no Claude Design uma paleta de cores e tipografia com tom corporativo (o público final é a diretoria), além do padrão visual dos cards de KPI que vai se repetir nas quatro páginas.
2. **Wireframes das quatro páginas**: usando a estrutura já definida acima (visão executiva, quem está saindo, por que está saindo, impacto financeiro), montar cada página no Claude Design e refinar por comentário/chat até o layout fazer sentido.
3. **Handoff**: com o design pronto, exportar o pacote de handoff para o Claude Code, que usa esse material como referência para gerar o HTML, CSS e JavaScript reais. Alternativa, sem abrir o Claude Code separadamente: trazer os prints, a paleta de cores e a estrutura das páginas direto para a conversa de implementação.
4. **Regra a manter**: não desenhar e codar na mesma conversa — uma serve para explorar o visual, a outra para produzir o código final.

## Documentação de entrega

Para o portfólio ficar completo, produza também:

- Um documento curto de premissas e decisões (por que excluiu algum dado, como tratou nulos, qual a definição de turnover usada)
- Um print ou diagrama simples do modelo de dados explicando como as fontes se relacionam
- Um resumo de uma página como se fosse entregue para a Patrícia, com a resposta às perguntas de negócio dela

## Checklist de execução

1. Baixar o dataset e dividir em três arquivos simulando as três fontes
2. Tratar e juntar as três fontes em Python (pandas), calculando as métricas
3. Exportar o resultado como JSON agregado para o front-end
4. Organizar os dados tratados no formato de fato e dimensões dentro do próprio Python, antes de achatar para o JSON final
5. Calcular as métricas com pandas (equivalente às medidas) e exportar no JSON
6. Montar o sistema de design e os wireframes das quatro páginas no Claude Design
7. Exportar o handoff e implementar o HTML/CSS/JS no Claude Code (ou trazer os mockups para a conversa de implementação)
8. Escrever o documento de premissas e decisões
9. Escrever o resumo executivo de uma página
10. Revisar tudo como se fosse mostrar para um cliente real, não para você mesmo

## Como usar isso no Claude Projects

Crie um projeto chamado algo como "Portfólio - Análise de Turnover". Nas instruções do projeto, cole um resumo curto dizendo que você é analista de dados simulando um projeto de consultoria de People Analytics para uma rede varejista fictícia, e que quer ajuda técnica em tratamento de dados com Python e construção de um dashboard em HTML/CSS/JavaScript. Suba este arquivo inteiro como conhecimento do projeto. Assim, qualquer conversa nova dentro desse projeto já vai ter o contexto do cenário sem você precisar reexplicar.
