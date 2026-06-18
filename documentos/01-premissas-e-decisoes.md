# Premissas e Decisões — Diagnóstico de Turnover Grupo Avelar

> Documento técnico que registra as escolhas de tratamento de dados e as premissas
> de negócio por trás dos números do dashboard. Objetivo: tornar o diagnóstico
> auditável e reproduzível.

---

## 1. Origem dos dados

- **Fonte:** dataset público **IBM HR Analytics Employee Attrition** (Kaggle), 1.470 colaboradores, 35 colunas, sem dados pessoais reais.
- **Cenário:** o **Grupo Avelar** é uma rede varejista **fictícia**. Os dados são reais (do dataset IBM), mas a narrativa de varejo é simulada para fins de portfólio.
- **Qualidade da base:** verificado **0 valores nulos** e **0 chaves `EmployeeNumber` duplicadas**. Não foi necessário imputar ou descartar registros por ausência de dados.

## 2. Definição de turnover

- Turnover é medido pela coluna **`Attrition`** (`Yes`/`No`): **237 desligamentos** em 1.470 colaboradores = **16,1%**.
- **Limitação documentada:** o dataset **não distingue saída voluntária de involuntária**. Embora o pedido da diretoria fale em "turnover voluntário", a base só traz o desligamento de forma binária. Todos os desligamentos são tratados como uma população única, e isso está explicitado para não superinterpretar o número.

## 3. Tratamento aplicado (Python / pandas)

| Decisão | O que foi feito | Por quê |
|---|---|---|
| **Colunas constantes** | Descartadas `EmployeeCount` (=1), `Over18` (=Y) e `StandardHours` (=80) | Não têm variação nem valor analítico |
| **Fragmentação em 3 fontes** | A base única foi dividida em Cadastro/Folha, Avaliação e Clima, ligadas por `EmployeeNumber`, e depois re-unida via *join* | Simula a integração de sistemas reais de uma empresa (ver `02-modelo-de-dados.md`) |
| **Validação do join** | `merge(..., validate="one_to_one")` | Garante que nenhuma linha foi perdida ou duplicada na reunião das fontes |
| **Nulos** | Nenhum tratamento necessário | A base não possui valores ausentes |

## 4. Premissas de cálculo das métricas

- **Custo de turnover:** premissa de **50% do salário anual por reposição** (recrutamento + treinamento + produtividade perdida). Operacionalmente: `custo = 0,5 × (salário mensal × 12) = 6 × MonthlyIncome`. `MonthlyIncome` é tratado como salário mensal em R$.
  - Custo total estimado: **R$ 6,8 mi** · Custo médio por desligamento: **R$ 28,7 mil**.
- **Índice de satisfação:** média de `JobSatisfaction` (escala 1–4) **normalizada para 0–10**: `(média / 4) × 10`. Resultado geral: **6,8/10**.
- **Tempo médio de permanência:** média de `YearsAtCompany` = **7,0 anos**.
- **Faixas salariais:** Até R$ 3 mil · R$ 3–5 mil · R$ 5–8 mil · R$ 8–12 mil · Acima de R$ 12 mil.
- **Faixas etárias:** Até 25 · 26–35 · 36–45 · 46–55 · 56+.
- **Classificação de status do departamento:** Crítico ≥ 18% · Atenção ≥ 14% · Estável < 14% de turnover.
- **Classificação de risco do cargo:** Alto ≥ 20% · Médio ≥ 12% · Baixo < 12% de turnover.
- **Cenário de economia:** redução hipotética de **20%** no turnover → economia de **R$ 1,4 mi/ano** (~47 desligamentos evitados).

## 5. De-para de rótulos (categorias técnicas → varejo)

O dataset IBM é de uma empresa de tecnologia/pesquisa. Para manter a narrativa do Grupo Avelar (varejo), as categorias foram **renomeadas de forma documentada**. **As taxas e valores permanecem 100% reais** — apenas os rótulos mudam.

**Departamentos**

| IBM (original) | Grupo Avelar |
|---|---|
| Sales | Operações de Loja |
| Research & Development | Logística & CD |
| Human Resources | Administrativo & Suporte |

**Cargos** (atribuídos por nível e rotatividade plausíveis)

| IBM (original) | Grupo Avelar |
|---|---|
| Sales Representative | Operador de Caixa |
| Laboratory Technician | Repositor |
| Human Resources | Auxiliar Administrativo |
| Sales Executive | Vendedor |
| Research Scientist | Auxiliar de Logística |
| Healthcare Representative | Supervisor de Loja |
| Manufacturing Director | Coordenador de CD |
| Manager | Gerente de Loja |
| Research Director | Gerente Regional |

## 6. Elementos do design ajustados por limitação dos dados

O layout de design previa três visuais que o dataset **não suporta**. Em vez de inventar dados, eles foram **substituídos por alternativas 100% reais**:

| Visual original (design) | Por que não dá | Substituído por |
|---|---|---|
| Evolução do turnover por trimestre | O dataset é uma **fotografia única, sem datas** | Turnover por **faixa etária** |
| Saída voluntária × involuntária | `Attrition` é binário, sem tipo | Desligamentos por **nível de cargo** |
| Composição do custo (recrut./trein./…) | Não há dado de composição | **Custo de turnover por departamento** |

Pelo mesmo motivo, o seletor de período do design (filtro de ano) foi substituído por um **filtro de Departamento**, que é uma dimensão real e funcional na base.

---

*Próximos documentos: `02-modelo-de-dados.md` (como as fontes se relacionam) e `03-resumo-executivo.md` (resposta de 1 página à diretoria).*
