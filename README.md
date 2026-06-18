# Diagnóstico de Turnover — Grupo Avelar

Projeto de **People Analytics** ponta a ponta: do tratamento dos dados em Python a um **dashboard interativo** em HTML/CSS/JavaScript, simulando uma consultoria real para a diretoria de uma rede varejista.

> ⚠️ **Cenário fictício.** O "Grupo Avelar" é uma rede varejista imaginária e a diretora "Patrícia Nogueira" não existe — é uma ambientação de portfólio. Os **dados são reais**, do dataset público [IBM HR Analytics Employee Attrition](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) (Kaggle), sem qualquer informação de empresa ou pessoa real.

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

## Decisões de engenharia de dados (o diferencial)

Em vez de "baixar um CSV e plotar", o projeto recria problemas de um cenário real:

- **Fragmentação simulada:** o CSV único foi **dividido em 3 fontes** (Cadastro/Folha, Avaliação de Desempenho, Pesquisa de Clima) e depois **re-unido por `EmployeeNumber`** — como acontece ao integrar sistemas diferentes de RH.
- **Honestidade com o dado:** o dataset é uma fotografia sem datas e não separa saída voluntária de involuntária. Em vez de inventar, os visuais que dependiam de dados inexistentes (evolução trimestral, tipo de saída) foram **substituídos por análises que o dado realmente sustenta** (turnover por faixa etária, por nível, custo por departamento), e o filtro de "ano" virou um **filtro de departamento** funcional.
- **De-para documentado:** o IBM HR é de uma empresa de tecnologia. Os rótulos foram renomeados para o contexto de varejo (mantendo as taxas reais), com o mapeamento registrado nas premissas.

## Stack

| Camada | Ferramenta |
|---|---|
| Tratamento de dados | Python + pandas |
| Saída de dados | JSON agregado (sem cálculo pesado no navegador) |
| Front-end | HTML + CSS + JavaScript puro |
| Gráficos | Chart.js (via CDN) |
| Documentação | Markdown → PDF (xhtml2pdf) |

## Como rodar

```bash
# 1. Processar os dados (gera dados/turnover.json)
pip install -r requirements.txt
python processar_dados.py

# 2. Subir o dashboard (o fetch do JSON é bloqueado em file://)
python -m http.server 8000
# abrir http://localhost:8000
```

Para regerar os PDFs da documentação: `python gerar_pdfs.py`.

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

## Documentação

- [`documentos/01-premissas-e-decisoes.md`](documentos/01-premissas-e-decisoes.md) — definição de turnover, tratamento, premissas e de-para.
- [`documentos/02-modelo-de-dados.md`](documentos/02-modelo-de-dados.md) — como as 3 fontes se relacionam.
- [`documentos/03-resumo-executivo.md`](documentos/03-resumo-executivo.md) — resposta de 1 página à diretoria.

---

**Créditos dos dados:** IBM HR Analytics Employee Attrition (dataset público, Kaggle). Projeto desenvolvido para fins de estudo e portfólio.
