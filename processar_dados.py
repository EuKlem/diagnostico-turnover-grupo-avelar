# -*- coding: utf-8 -*-
"""
Diagnóstico de Turnover - Grupo Avelar
======================================
Pipeline de tratamento de dados (Python / pandas).

Fluxo:
  1. Lê o dataset bruto (IBM HR Analytics Employee Attrition).
  2. Divide em 3 fontes simuladas (Cadastro/Folha, Avaliação, Clima) ligadas
     pela chave EmployeeNumber — simula a fragmentação de sistemas reais.
  3. Re-junta as 3 fontes (join por EmployeeNumber) na base unificada.
  4. Aplica o de-para de rótulos (categorias técnicas do IBM -> nomes de varejo
     do cenário fictício Grupo Avelar). As TAXAS permanecem 100% reais.
  5. Calcula as métricas e exporta tudo agregado em dados/turnover.json,
     consumido pelo index.html (nenhum cálculo pesado no navegador).

Premissas documentadas no topo das constantes abaixo.
"""

import os
import json
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_BRUTO = os.path.join(BASE, "WA_Fn-UseC_-HR-Employee-Attrition.csv")
DIR_DADOS = os.path.join(BASE, "dados")
DIR_FONTES = os.path.join(DIR_DADOS, "fontes")

# --- Premissas do projeto ----------------------------------------------------
# Período de referência do recorte (o dataset é uma fotografia, sem datas).
PERIODO = "T2 2025"
# Custo de reposição por desligamento = 50% do salário ANUAL do colaborador.
# MonthlyIncome é tratado como salário mensal em R$.  => 0,5 * (mensal*12) = 6*mensal
FATOR_CUSTO = 6  # multiplica MonthlyIncome para obter o custo estimado por saída
# Meta de redução usada no cenário de economia potencial.
META_REDUCAO = 0.20

# De-para de DEPARTAMENTOS (IBM -> Grupo Avelar). Taxas reais preservadas.
MAP_DEPTO = {
    "Sales": "Operações de Loja",
    "Research & Development": "Logística & CD",
    "Human Resources": "Administrativo & Suporte",
}
# De-para de CARGOS (IBM -> Grupo Avelar), atribuído por nível/rotatividade plausível.
MAP_CARGO = {
    "Sales Representative": "Operador de Caixa",
    "Laboratory Technician": "Repositor",
    "Human Resources": "Auxiliar Administrativo",
    "Sales Executive": "Vendedor",
    "Research Scientist": "Auxiliar de Logística",
    "Healthcare Representative": "Supervisor de Loja",
    "Manufacturing Director": "Coordenador de CD",
    "Manager": "Gerente de Loja",
    "Research Director": "Gerente Regional",
}
# Rótulos de nível de cargo (JobLevel 1..5).
MAP_NIVEL = {1: "Operacional", 2: "Pleno", 3: "Especialista", 4: "Coordenação", 5: "Diretoria"}


def carregar_e_limpar():
    """Lê o CSV bruto, remove colunas constantes/sem valor analítico."""
    df = pd.read_csv(CSV_BRUTO)
    # Colunas constantes em todo o dataset -> descartadas (documentado nas premissas).
    constantes = ["EmployeeCount", "Over18", "StandardHours"]
    df = df.drop(columns=[c for c in constantes if c in df.columns])
    # Saída como booleano auxiliar.
    df["saiu"] = df["Attrition"].eq("Yes")
    return df


def dividir_em_fontes(df):
    """Quebra a base única em 3 fontes simuladas, salvas como CSV separados."""
    os.makedirs(DIR_FONTES, exist_ok=True)

    fonte_cadastro = df[[
        "EmployeeNumber", "Age", "Gender", "MaritalStatus", "Department",
        "JobRole", "JobLevel", "MonthlyIncome", "DistanceFromHome",
        "YearsAtCompany", "TotalWorkingYears", "Attrition",
    ]].copy()

    fonte_avaliacao = df[[
        "EmployeeNumber", "PerformanceRating", "OverTime", "JobInvolvement",
        "TrainingTimesLastYear", "PercentSalaryHike",
    ]].copy()

    fonte_clima = df[[
        "EmployeeNumber", "JobSatisfaction", "EnvironmentSatisfaction",
        "WorkLifeBalance", "RelationshipSatisfaction",
    ]].copy()

    fonte_cadastro.to_csv(os.path.join(DIR_FONTES, "fonte1_cadastro_folha.csv"), index=False)
    fonte_avaliacao.to_csv(os.path.join(DIR_FONTES, "fonte2_avaliacao_desempenho.csv"), index=False)
    fonte_clima.to_csv(os.path.join(DIR_FONTES, "fonte3_pesquisa_clima.csv"), index=False)
    return fonte_cadastro, fonte_avaliacao, fonte_clima


def juntar_fontes(cadastro, avaliacao, clima):
    """Recria a base unificada via join por EmployeeNumber (como num ETL real)."""
    base = (
        cadastro
        .merge(avaliacao, on="EmployeeNumber", how="inner", validate="one_to_one")
        .merge(clima, on="EmployeeNumber", how="inner", validate="one_to_one")
    )
    base["saiu"] = base["Attrition"].eq("Yes")
    # De-para de rótulos.
    base["dep_avelar"] = base["Department"].map(MAP_DEPTO)
    base["cargo_avelar"] = base["JobRole"].map(MAP_CARGO)
    base["nivel_avelar"] = base["JobLevel"].map(MAP_NIVEL)
    base.to_csv(os.path.join(DIR_DADOS, "base_unificada.csv"), index=False)
    return base


def taxa(grupo):
    """Taxa de turnover (% que saiu) de um subconjunto."""
    return round(grupo["saiu"].mean() * 100, 1)


def calcular_metricas(base):
    n_total = int(len(base))
    saiu = base[base["saiu"]]
    ficou = base[~base["saiu"]]
    n_saidas = int(len(saiu))

    # ---- KPIs (Visão Executiva) --------------------------------------------
    turnover_geral = taxa(base)
    tempo_medio_casa = round(base["YearsAtCompany"].mean(), 1)
    # Índice de satisfação: média de JobSatisfaction (1-4) normalizada para 0-10.
    indice_satisfacao = round(base["JobSatisfaction"].mean() / 4 * 10, 1)
    custo_total = int((saiu["MonthlyIncome"] * FATOR_CUSTO).sum())

    # ---- Turnover por faixa etária (substitui evolução trimestral) ----------
    faixas_idade = [(0, 25, "Até 25"), (26, 35, "26–35"), (36, 45, "36–45"),
                    (46, 55, "46–55"), (56, 200, "56+")]
    turnover_faixa_etaria = []
    for lo, hi, rot in faixas_idade:
        g = base[(base["Age"] >= lo) & (base["Age"] <= hi)]
        if len(g):
            turnover_faixa_etaria.append({"faixa": rot, "n": int(len(g)), "taxa": taxa(g)})

    # ---- Desligados por nível de cargo (substitui "tipo de saída") ----------
    desligados_por_nivel = []
    for nivel in sorted(base["JobLevel"].unique()):
        g_saiu = saiu[saiu["JobLevel"] == nivel]
        desligados_por_nivel.append({
            "nivel": MAP_NIVEL.get(int(nivel), str(nivel)),
            "n": int(len(g_saiu)),
            "pct": round(len(g_saiu) / n_saidas * 100, 1),
        })

    # ---- Tempo de casa ao sair (real, entre os que saíram) ------------------
    buckets_casa = [(0, 1, "Menos de 2 anos"), (2, 5, "2 a 5 anos"), (6, 200, "Mais de 5 anos")]
    tempo_casa_saida = []
    for lo, hi, rot in buckets_casa:
        g = saiu[(saiu["YearsAtCompany"] >= lo) & (saiu["YearsAtCompany"] <= hi)]
        tempo_casa_saida.append({"faixa": rot, "pct": round(len(g) / n_saidas * 100, 1)})

    # ---- Quem está saindo: departamento -------------------------------------
    por_departamento = []
    for dep, g in base.groupby("dep_avelar"):
        g_saiu = g[g["saiu"]]
        por_departamento.append({
            "departamento": dep,
            "headcount": int(len(g)),
            "n_saidas": int(len(g_saiu)),
            "share_saidas": round(len(g_saiu) / n_saidas * 100, 1),
            "taxa": taxa(g),
        })
    por_departamento.sort(key=lambda x: x["n_saidas"], reverse=True)

    # ---- Ranking de cargos por taxa de turnover -----------------------------
    ranking_cargos = []
    for cargo, g in base.groupby("cargo_avelar"):
        ranking_cargos.append({"cargo": cargo, "headcount": int(len(g)), "taxa": taxa(g)})
    ranking_cargos.sort(key=lambda x: x["taxa"], reverse=True)

    # ---- Turnover por faixa salarial ----------------------------------------
    faixas_sal = [(0, 3000, "Até R$ 3 mil"), (3001, 5000, "R$ 3 – 5 mil"),
                  (5001, 8000, "R$ 5 – 8 mil"), (8001, 12000, "R$ 8 – 12 mil"),
                  (12001, 10**9, "Acima de R$ 12 mil")]
    por_faixa_salarial = []
    for lo, hi, rot in faixas_sal:
        g = base[(base["MonthlyIncome"] >= lo) & (base["MonthlyIncome"] <= hi)]
        if len(g):
            por_faixa_salarial.append({"faixa": rot, "n": int(len(g)), "taxa": taxa(g)})

    # ---- Status dos departamentos (crítico/atenção/estável) -----------------
    def status_de(t):
        return "Crítico" if t >= 18 else ("Atenção" if t >= 14 else "Estável")
    departamentos_status = [{
        "departamento": d["departamento"], "headcount": d["headcount"],
        "turnover": d["taxa"], "status": status_de(d["taxa"]),
    } for d in por_departamento]

    # ---- Por que estão saindo: comparativo saíram x ficaram -----------------
    comparativos = {
        "satisfacao": {  # JobSatisfaction 1-4 -> escala 0-10
            "saiu": round(saiu["JobSatisfaction"].mean() / 4 * 10, 1),
            "ficou": round(ficou["JobSatisfaction"].mean() / 4 * 10, 1),
            "escala": 10, "unidade": "/10", "pior": "menor",
        },
        "hora_extra": {  # % que faz hora extra frequente
            "saiu": round(saiu["OverTime"].eq("Yes").mean() * 100, 1),
            "ficou": round(ficou["OverTime"].eq("Yes").mean() * 100, 1),
            "escala": 100, "unidade": "%", "pior": "maior",
        },
        "distancia": {  # distância média até o trabalho (km)
            "saiu": round(saiu["DistanceFromHome"].mean(), 1),
            "ficou": round(ficou["DistanceFromHome"].mean(), 1),
            "escala": round(base["DistanceFromHome"].max()), "unidade": " km", "pior": "maior",
        },
        "equilibrio": {  # WorkLifeBalance 1-5
            "saiu": round(saiu["WorkLifeBalance"].mean(), 1),
            "ficou": round(ficou["WorkLifeBalance"].mean(), 1),
            "escala": 5, "unidade": "/5", "pior": "menor",
        },
    }
    # Insight: razão de hora extra saíram / ficaram.
    razao_he = round(comparativos["hora_extra"]["saiu"] / comparativos["hora_extra"]["ficou"], 1)

    # ---- Impacto financeiro -------------------------------------------------
    custo_medio = int(round(custo_total / n_saidas)) if n_saidas else 0
    economia = int(round(custo_total * META_REDUCAO))
    saidas_evitadas = int(round(n_saidas * META_REDUCAO))

    # Cargos com maior risco: impacto anual projetado = headcount * taxa * custo/saída do cargo.
    cargos_risco = []
    for cargo, g in base.groupby("cargo_avelar"):
        t = g["saiu"].mean()
        custo_saida_cargo = int(round(g["MonthlyIncome"].mean() * FATOR_CUSTO))
        impacto = int(round(len(g) * t * custo_saida_cargo))
        risco = "Alto" if t * 100 >= 20 else ("Médio" if t * 100 >= 12 else "Baixo")
        cargos_risco.append({
            "cargo": cargo, "headcount": int(len(g)),
            "custo_saida": custo_saida_cargo, "risco": risco, "impacto_anual": impacto,
        })
    cargos_risco.sort(key=lambda x: x["impacto_anual"], reverse=True)

    # Custo de turnover por departamento (substitui "composição do custo").
    custo_por_departamento = []
    for dep, g in base.groupby("dep_avelar"):
        c = int((g[g["saiu"]]["MonthlyIncome"] * FATOR_CUSTO).sum())
        custo_por_departamento.append({
            "departamento": dep, "custo": c,
            "pct": round(c / custo_total * 100, 1) if custo_total else 0,
        })
    custo_por_departamento.sort(key=lambda x: x["custo"], reverse=True)

    return {
        "meta": {
            "dataset": "IBM HR Analytics Employee Attrition",
            "empresa_ficticia": "Grupo Avelar",
            "periodo": PERIODO,
            "n_total": n_total,
            "n_saidas": n_saidas,
            "premissas": {
                "custo_por_saida": "50% do salário anual (6 × salário mensal)",
                "indice_satisfacao": "média de JobSatisfaction (1–4) normalizada para 0–10",
                "rotulos": "de-para documentado de categorias técnicas para nomes de varejo",
                "colunas_descartadas": ["EmployeeCount", "Over18", "StandardHours"],
            },
        },
        "kpis": {
            "turnover_geral": turnover_geral,
            "tempo_medio_casa": tempo_medio_casa,
            "indice_satisfacao": indice_satisfacao,
            "custo_total": custo_total,
        },
        "exec": {
            "turnover_faixa_etaria": turnover_faixa_etaria,
            "desligados_por_nivel": desligados_por_nivel,
            "tempo_casa_saida": tempo_casa_saida,
        },
        "quem": {
            "por_departamento": por_departamento,
            "ranking_cargos": ranking_cargos,
            "por_faixa_salarial": por_faixa_salarial,
            "departamentos_status": departamentos_status,
        },
        "porque": {
            "comparativos": comparativos,
            "razao_hora_extra": razao_he,
        },
        "financeiro": {
            "custo_total": custo_total,
            "custo_medio": custo_medio,
            "economia_potencial": economia,
            "saidas_evitadas": saidas_evitadas,
            "meta_reducao_pct": int(META_REDUCAO * 100),
            "cargos_risco": cargos_risco,
            "custo_por_departamento": custo_por_departamento,
        },
    }


def main():
    os.makedirs(DIR_DADOS, exist_ok=True)
    print("1/4  Lendo e limpando o dataset bruto...")
    df = carregar_e_limpar()
    print(f"     {len(df)} colaboradores, {int(df['saiu'].sum())} desligamentos.")

    print("2/4  Dividindo em 3 fontes simuladas...")
    cadastro, avaliacao, clima = dividir_em_fontes(df)

    print("3/4  Re-juntando as fontes por EmployeeNumber...")
    base = juntar_fontes(cadastro, avaliacao, clima)
    assert len(base) == len(df), "join perdeu/duplicou linhas!"

    print("4/4  Calculando métricas (geral + por departamento) e exportando JSON...")
    # Pré-calcula o conjunto completo de métricas para "Todos" e para cada
    # departamento, para que o filtro do dashboard apenas troque o recorte
    # já pronto (nenhum cálculo pesado no navegador).
    dados = {"Todos": calcular_metricas(base)}
    ordem = ["Todos"]
    for dep in base["dep_avelar"].value_counts().index.tolist():
        dados[dep] = calcular_metricas(base[base["dep_avelar"] == dep].copy())
        ordem.append(dep)

    payload = {"departamentos": ordem, "dados": dados}
    saida_json = os.path.join(DIR_DADOS, "turnover.json")
    with open(saida_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    g = dados["Todos"]
    print(f"\nOK -> {saida_json}")
    print(f"     Recortes: {', '.join(ordem)}")
    print(f"     Turnover geral: {g['kpis']['turnover_geral']}%  |  "
          f"Custo estimado: R$ {g['kpis']['custo_total']:,}".replace(",", "."))


if __name__ == "__main__":
    main()
