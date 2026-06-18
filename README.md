# Diagnóstico de Turnover - Grupo Avelar

Projeto **People Analytics**: do tratamento dos dados em Python a um **dashboard interativo** em HTML/CSS/JavaScript, simulando uma consultoria real para a diretoria de uma rede varejista.

> ⚠️ **Cenário fictício.** O "Grupo Avelar" é uma rede varejista imaginária e a diretora "Patrícia Nogueira". Os **dados são reais**, do dataset público [IBM HR Analytics Employee Attrition](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) (Kaggle), sem qualquer informação de empresa ou pessoa real.

---

## O problema

A diretora de Pessoas & Cultura precisa entender o turnover da rede antes de uma reunião de conselho. Hoje ela só tem planilhas soltas de desligamento, sem comparação nem cruzamento. O dashboard responde a cinco perguntas:

1. Qual a taxa de turnover, e onde ela se concentra (departamento, cargo, faixa salarial)?
2. A saída tem relação com satisfação, hora extra ou distância de casa?
3. Salário e tempo de empresa influenciam?
4. Quais cargos têm maior risco e qual o custo de reposição?
5. É "o mercado" ou existe um padrão interno?

## O que o diagnóstico mostra

- **Turnover de 16,1%** (237 de 1.470 colaboradores), concentrado em **cargos operacionais de baixa faixa salarial**.
- O fator mais associado à saída é **hora extra**: quem saiu fazia hora extra frequente **2,3× mais** do que quem ficou.
- A saída é **precoce** — 31,6% desliga com menos de 2 anos de casa.
- Custo estimado de **R$ 6,8 mi/ano**; reduzir o turnover em 20% economizaria **R$ 1,4 mi/ano**.

## Stack

| Camada | Ferramenta |
|---|---|
| Tratamento de dados | Python + pandas |
| Saída de dados | JSON agregado |
| Front-end | HTML + CSS + JavaScript puro |
| Gráficos | Chart.js (via CDN) |
| Documentação | Markdown → PDF (xhtml2pdf) |

## Estrutura

```
processar_dados.py          Pipeline pandas: 3 fontes → join → métricas → JSON
gerar_pdfs.py               Converte os .md de documentos/ em PDF
index.html                  Dashboard (4 páginas, filtro por departamento)
dados/
  turnover.json             Métricas agregadas (geral + por departamento)
  base_unificada.csv        Fato após o join
  fontes/                   As 3 fontes simuladas
documentos/                 Premissas, modelo de dados e resumo executivo (.md + .pdf)
capturas/                   Screenshots do dashboard
```

**Créditos dos dados:** IBM HR Analytics Employee Attrition (dataset público, Kaggle). Projeto desenvolvido para fins de estudo e portfólio.
