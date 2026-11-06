# Saneamento básico nos municípios brasileiros: urbanização, educação e renda

**Global Solution 2026.2 — MLAM (Desafio CitizenTech)**

Análise estatística, em Python, de dados **reais e oficiais do IBGE** (Censo Demográfico 2022 e PIB dos Municípios 2021) para investigar o que explica a desigualdade no acesso ao saneamento básico entre os 5.538 municípios brasileiros e identificar os municípios com maior risco de esgoto inadequado.

---

## 👥 Integrantes

| Nome completo | RM |
|---|---|
| [Nome completo do integrante 1] | RM000000 |
| [Nome completo do integrante 2] | RM000000 |
| [Nome completo do integrante 3] | RM000000 |

---

## 🎯 Problema e objetivo

Em 2022, a maioria dos municípios brasileiros ainda não tinha metade dos domicílios ligados à rede de esgoto, e o Novo Marco Legal do Saneamento (Lei 14.026/2020) exige 90% de cobertura de esgoto até 2033. O déficit é concentrado no **campo, nas comunidades dispersas e nas regiões Norte e Nordeste**.

**Objetivo:** medir quanto o acesso a esgoto, água e coleta de lixo está associado a fatores estruturais dos municípios (urbanização, alfabetização, densidade e renda) e construir um modelo simples para **priorizar os municípios com maior risco de saneamento inadequado**.

---

## 🗂️ Base de dados

- **Fonte:** IBGE — API SIDRA (<https://apisidra.ibge.gov.br>), dados públicos e oficiais
- **Unidade de análise:** município (5.570 → 5.538 após remover registros incompletos)
- **Arquivo final:** [`data/processed/base_saneamento_municipios_2022.csv`](data/processed/base_saneamento_municipios_2022.csv) (também em `.xlsx`)
- **Dados brutos (sem alteração):** [`data/raw/`](data/raw)

| Tabela SIDRA | Conteúdo | Link de acesso |
|---|---|---|
| 4714 | Censo 2022 — população, área e densidade | <https://sidra.ibge.gov.br/tabela/4714> |
| 9923 | Censo 2022 — população por situação do domicílio (urbana/rural) | <https://sidra.ibge.gov.br/tabela/9923> |
| 6805 | Censo 2022 — domicílios por tipo de esgotamento sanitário | <https://sidra.ibge.gov.br/tabela/6805> |
| 6803 | Censo 2022 — domicílios por forma de abastecimento de água | <https://sidra.ibge.gov.br/tabela/6803> |
| 6892 | Censo 2022 — domicílios por destino do lixo | <https://sidra.ibge.gov.br/tabela/6892> |
| 9543 | Censo 2022 — taxa de alfabetização (15 anos ou mais) | <https://sidra.ibge.gov.br/tabela/9543> |
| 5938 | PIB dos Municípios 2021 — PIB, VAB total e VAB agropecuário | <https://sidra.ibge.gov.br/tabela/5938> |

### Dicionário de variáveis

| Variável | Descrição |
|---|---|
| `codigo_ibge`, `municipio`, `uf`, `regiao` | Identificação do município |
| `populacao`, `area_km2`, `densidade_hab_km2` | População residente (2022), área e densidade |
| `pct_pop_urbana` | % da população em situação urbana |
| `pct_esgoto_rede` | % de domicílios com esgoto na rede geral/pluvial ou fossa ligada à rede |
| `pct_agua_rede` | % de domicílios ligados à rede geral de água e que a usam como forma principal |
| `pct_lixo_coletado` | % de domicílios com lixo coletado |
| `taxa_alfabetizacao` | Taxa de alfabetização das pessoas com 15 anos ou mais (%) |
| `pib_mil_reais`, `pib_per_capita` | PIB 2021 (mil R$) e PIB per capita (R$; PIB 2021 / população 2022) |
| `pct_vab_agro` | Participação da agropecuária no valor adicionado bruto (%) |
| `log_pib_per_capita`, `log_densidade` | Logaritmo base 10 das variáveis (reduz a assimetria) |
| `esgoto_adequado` | **1** se ≥ 50% dos domicílios estão ligados à rede de esgoto, **0** caso contrário |

### Limpeza e transformação (reprodutíveis)

1. `src/01_coleta_dados.py` baixa cada tabela da API SIDRA e salva o CSV bruto em `data/raw/`.
2. `src/02_tratamento_dados.py` une as tabelas pelo código IBGE, converte os símbolos do SIDRA (`-`, `...`, `X`) em valores ausentes, remove os municípios incompletos, cria as variáveis derivadas e salva a base final em `data/processed/`.

---

## 📁 Estrutura do repositório

```
├── data/
│   ├── raw/                                  # tabelas brutas do SIDRA (sem alteração)
│   └── processed/
│       ├── base_saneamento_municipios_2022.csv   # base usada nas análises
│       └── base_saneamento_municipios_2022.xlsx
├── notebooks/
│   └── analise_estatistica.ipynb             # TODAS as análises (itens 02 a 06), com saídas
├── reports/
│   ├── relatorio_estatistico.pdf             # relatório estatístico (item 07)
│   ├── resultados.json                       # números gerados pelo notebook
│   └── figuras/                              # gráficos em PNG
├── src/
│   ├── 01_coleta_dados.py                    # coleta via API SIDRA/IBGE
│   ├── 02_tratamento_dados.py                # limpeza e montagem da base
│   └── 03_gerar_relatorio.py                 # gera o PDF a partir dos resultados
├── requirements.txt
└── README.md
```

### Onde está cada item do enunciado

| Item | Conteúdo | Onde |
|---|---|---|
| 01 | Escolha e justificativa da base | README, seção 1 do notebook, seção 3 do relatório |
| 02 | Distribuição normal — P(X < média) e P(X > mediana) | Notebook, seção 2 · Relatório, seção 5 |
| 03 | Testes de hipóteses para a média (α = 6%, n = 20 e α = 9%, n = 25) | Notebook, seção 3 · Relatório, seção 6 |
| 04 | Análise bivariada (dispersão, covariância, Pearson, regressão simples, R², F, previsão) | Notebook, seção 4 · Relatório, seção 7 |
| 05 | Regressão linear múltipla (dispersão, matrizes, equação, R², F, previsão) | Notebook, seção 5 · Relatório, seção 8 |
| 06 | Regressão logística binária (equação, matriz de confusão, acurácia, classificação) | Notebook, seção 6 · Relatório, seção 9 |
| 07 | Relatório estatístico | [`reports/relatorio_estatistico.pdf`](reports/relatorio_estatistico.pdf) |

---

## ▶️ Como executar

Requisitos: **Python 3.10+**.

```bash
# 1. instalar as dependências
pip install -r requirements.txt

# 2. (opcional) baixar novamente os dados do IBGE e reconstruir a base
python src/01_coleta_dados.py
python src/02_tratamento_dados.py

# 3. executar o notebook com todas as análises
jupyter notebook notebooks/analise_estatistica.ipynb
#    ou, sem abrir o Jupyter:
jupyter nbconvert --to notebook --execute --inplace notebooks/analise_estatistica.ipynb

# 4. (opcional) gerar novamente o relatório em PDF
python src/03_gerar_relatorio.py
```

Os dados brutos e processados já estão no repositório, então o notebook roda direto, sem internet.

### Bibliotecas

`pandas`, `numpy`, `scipy`, `statsmodels`, `scikit-learn`, `matplotlib`, `seaborn`, `requests` (coleta), `openpyxl` (exportação .xlsx), `reportlab` (PDF) e `jupyter`/`nbconvert` (execução do notebook). As versões estão em [`requirements.txt`](requirements.txt).

---

## 📊 Síntese dos resultados

| Análise | Resultado principal |
|---|---|
| Descritiva | Em média, só **37,9%** dos domicílios de cada município estão ligados à rede de esgoto, contra **71,9%** para água e **80,4%** para coleta de lixo. A cobertura média de esgoto vai de **7,5% no Norte** a **70,6% no Sudeste**. |
| Normal (alfabetização) | P(X < média) = **0,50** (evento equiprovável). P(X > mediana) = **0,374** (evento improvável), o que revela uma distribuição assimétrica à esquerda. |
| Testes de hipóteses (água) | a) Z = 1,54 > −1,555, **não rejeita H0**. b) Z = 1,92 > 1,341 (p = 0,027), **rejeita H0**, um caso possível de erro tipo I discutido no relatório. |
| Bivariada | Urbanização × coleta de lixo: **r = 0,740**, Ŷ = 36,22 + 0,638·X, **R² = 0,547**, teste F significativo. |
| Regressão múltipla | Esgoto = −91,36 + 0,72·Urbana + 0,73·Alfabetização + 10,74·log(Densidade); **R² = 0,420**, todos os coeficientes significativos e VIF < 1,6. |
| Regressão logística | **Acurácia de 77,1%** no teste (modelo ingênuo: 62,1%), especificidade de 83,4%. Um **PIB per capita alto não aumenta** a chance de esgoto adequado (razão de chances de 0,35). |

**Insight para o CitizenTech:** o déficit de esgoto se concentra em municípios **rurais, pouco densos e menos escolarizados**, onde a rede convencional é cara. As políticas e tecnologias devem priorizar **soluções descentralizadas** nesses territórios, e o modelo logístico pode funcionar como **ferramenta de triagem** com apenas quatro indicadores públicos.

## ⚠️ Limitações

- Estudo observacional e transversal: **associação não é causalidade**.
- O PIB é de 2021 e a população é de 2022 (o último PIB municipal com VAB por atividade disponível no SIDRA), uma pequena defasagem.
- A normalidade assumida nos itens 02 e 03 é uma aproximação (a alfabetização é assimétrica).
- As regressões lineares têm heterocedasticidade (a resposta é limitada entre 0% e 100%).
- O limiar de 50% para "esgoto adequado" é uma escolha analítica, e o Censo mede **ligação à rede**, não o tratamento do esgoto.
- As conclusões valem para municípios, não para indivíduos (falácia ecológica).
