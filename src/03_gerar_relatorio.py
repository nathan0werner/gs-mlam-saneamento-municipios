"""
03_gerar_relatorio.py
---------------------
Gera reports/relatorio_estatistico.pdf a partir dos resultados salvos pelo
notebook (reports/resultados.json) e das figuras em reports/figuras/.

Execução (depois de rodar o notebook):
    python src/03_gerar_relatorio.py
"""
import json
from pathlib import Path

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

RAIZ = Path(__file__).resolve().parents[1]
FIG = RAIZ / "reports" / "figuras"
R = json.loads((RAIZ / "reports" / "resultados.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- integrantes
INTEGRANTES = [
    ("[Nome completo do integrante 1]", "RM 000000"),
    ("[Nome completo do integrante 2]", "RM 000000"),
    ("[Nome completo do integrante 3]", "RM 000000"),
]

# ---------------------------------------------------------------- fontes (DejaVu vem com o matplotlib)
fdir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
pdfmetrics.registerFont(TTFont("DV", str(fdir / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DV-B", str(fdir / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DV-I", str(fdir / "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-B")

AZUL = colors.HexColor("#1f3b57")
CINZA = colors.HexColor("#f2f4f7")
ss = getSampleStyleSheet()
S = {
    "h1": ParagraphStyle("h1", parent=ss["Heading1"], fontName="DV-B", fontSize=15, textColor=AZUL, spaceBefore=10, spaceAfter=8),
    "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontName="DV-B", fontSize=11.5, textColor=AZUL, spaceBefore=8, spaceAfter=4),
    "p": ParagraphStyle("p", parent=ss["BodyText"], fontName="DV", fontSize=9.5, leading=13.5, alignment=TA_JUSTIFY, spaceAfter=5),
    "b": ParagraphStyle("b", parent=ss["BodyText"], fontName="DV", fontSize=9.5, leading=13.5, leftIndent=12, bulletIndent=2, spaceAfter=2),
    "cap": ParagraphStyle("cap", parent=ss["BodyText"], fontName="DV-I", fontSize=8, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=8),
    "eq": ParagraphStyle("eq", parent=ss["BodyText"], fontName="DV", fontSize=9.5, leading=13, alignment=TA_CENTER,
                         backColor=CINZA, borderPadding=6, spaceBefore=4, spaceAfter=8),
    "cell": ParagraphStyle("cell", fontName="DV", fontSize=8, leading=10),
    "cellb": ParagraphStyle("cellb", fontName="DV-B", fontSize=8, leading=10, textColor=colors.white),
}


def f(v, d=2):
    """Formata número no padrão brasileiro."""
    s = f"{v:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v, d=1):
    return f(100 * v, d) + "%"


def P(t, st="p"):
    return Paragraph(t, S[st])


def bullets(itens):
    return [Paragraph(t, S["b"], bulletText="•") for t in itens]


def fig(nome, legenda, largura=16):
    img = Image(str(FIG / nome))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth = largura * cm
    img.drawHeight = largura * cm * ratio
    return KeepTogether([img, P(legenda, "cap")])


def tabela(linhas, larguras=None):
    dados = [[Paragraph(str(c), S["cellb"] if i == 0 else S["cell"]) for c in linha] for i, linha in enumerate(linhas)]
    t = Table(dados, colWidths=[w * cm for w in larguras] if larguras else None, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CINZA]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#c8ced6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return KeepTogether([t, Spacer(1, 8)])


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, "Global Solution 2026.2 — MLAM | Saneamento básico nos municípios brasileiros")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


# =============================================================== conteúdo
N, TA, TB = R["normal"], R["teste_a"], R["teste_b"]
BV, SI, MU, LG = R["biv"], R["simples"], R["multipla"], R["logistica"]
REG = {r["regiao"]: r for r in R["regioes"]}
story = []

# ---------- capa
story += [Spacer(1, 4 * cm),
          Paragraph("GLOBAL SOLUTION 2026.2 — MLAM", ParagraphStyle("c0", fontName="DV-B", fontSize=11, textColor=colors.grey, alignment=TA_CENTER)),
          Spacer(1, 0.6 * cm),
          Paragraph("Relatório Estatístico", ParagraphStyle("c1", fontName="DV-B", fontSize=26, leading=30, textColor=AZUL, alignment=TA_CENTER)),
          Spacer(1, 0.4 * cm),
          Paragraph("Saneamento básico nos municípios brasileiros:<br/>urbanização, educação e renda (Censo 2022)",
                    ParagraphStyle("c2", fontName="DV", fontSize=14, leading=19, alignment=TA_CENTER)),
          Spacer(1, 0.4 * cm),
          Paragraph("Desafio CitizenTech — cidades, campo e comunidades",
                    ParagraphStyle("c3", fontName="DV-I", fontSize=10, textColor=colors.grey, alignment=TA_CENTER)),
          Spacer(1, 3 * cm)]
story.append(tabela([["Integrante", "RM"]] + [list(i) for i in INTEGRANTES], [11, 4]))
story += [Spacer(1, 2 * cm),
          Paragraph("Fonte dos dados: IBGE — Censo Demográfico 2022 e PIB dos Municípios 2021 (API SIDRA)",
                    ParagraphStyle("c4", fontName="DV", fontSize=8.5, textColor=colors.grey, alignment=TA_CENTER)),
          PageBreak()]

# ---------- 1. sumário executivo
e = REG
story += [P("1. Sumário executivo", "h1"),
          P(f"Este relatório analisa os <b>{f(R['n'], 0).replace(',00', '')} municípios brasileiros</b> com dados completos no Censo 2022 "
            "para responder a uma pergunta de política pública: <b>o que explica a desigualdade no acesso ao saneamento básico entre os "
            "municípios, e como identificar os municípios com maior risco de esgoto inadequado?</b>"),
          P("<b>Principais achados</b>", "h2")]
story += bullets([
    f"O esgoto é o serviço menos universalizado: em média, só <b>{f(R['media_esgoto'], 1)}%</b> dos domicílios de cada município estão "
    f"ligados à rede, contra cerca de 72% para água encanada e 80% para coleta de lixo. Em <b>{f(R['mun_esgoto_abaixo_10'], 1)}%</b> dos municípios, "
    "menos de 10% dos domicílios estão ligados à rede de esgoto.",
    f"A desigualdade regional é forte: a cobertura média de esgoto vai de <b>{f(e['Norte']['esgoto_rede'], 1)}%</b> no Norte a "
    f"<b>{f(e['Sudeste']['esgoto_rede'], 1)}%</b> no Sudeste. No Sudeste, {f(e['Sudeste']['pct_esgoto_adequado'], 1)}% dos municípios "
    f"têm esgoto adequado (≥ 50% dos domicílios ligados); no Norte, só {f(e['Norte']['pct_esgoto_adequado'], 1)}%.",
    f"A urbanização tem <b>correlação forte</b> com a coleta de lixo (r = {f(BV['r'], 3)}) e explica <b>{pct(SI['r2'])}</b> da sua variação.",
    f"Urbanização, alfabetização e densidade explicam juntas <b>{pct(MU['r2'])}</b> da variação da cobertura de esgoto, com efeitos "
    "positivos e significativos.",
    f"A regressão logística classifica corretamente <b>{pct(LG['acuracia'])}</b> dos municípios de teste (contra {pct(LG['baseline'])} "
    f"do modelo ingênuo) e identifica <b>{pct(LG['especificidade'])}</b> dos municípios com esgoto inadequado. Um <b>PIB per capita "
    "alto não aumenta, por si só, a chance de ter esgoto adequado</b>.",
])
story += [P("<b>Recomendação central:</b> priorizar investimentos e soluções descentralizadas de esgotamento (fossas sépticas adequadas, "
            "sistemas condominiais) em <b>municípios pequenos, rurais, pouco densos e com baixa alfabetização</b>, sobretudo no Norte e no "
            "Nordeste. O modelo logístico pode servir como <b>ferramenta de triagem</b> desses municípios.")]

# ---------- 2. contexto
story += [P("2. Contextualização do problema", "h1"),
          P("O saneamento básico (abastecimento de água, esgotamento sanitário e manejo de resíduos sólidos) é um direito previsto na "
            "Lei 11.445/2007, e o Novo Marco Legal do Saneamento (Lei 14.026/2020) estabeleceu a meta de 99% da população com água potável e "
            "90% com coleta e tratamento de esgoto até 2033. A falta de saneamento está ligada a doenças de veiculação hídrica, à "
            "poluição de rios e à perda de qualidade de vida, e atinge mais as comunidades rurais e periféricas."),
          P("No contexto do desafio <b>CitizenTech</b>, que busca soluções tecnológicas para cidades, campo e comunidades, entender "
            "<b>quais características dos municípios estão associadas ao déficit de saneamento</b> ajuda a direcionar recursos, "
            "escolher tecnologias adequadas a cada território e acompanhar o progresso rumo às metas de 2033."),
          P("<b>Objetivos das análises:</b> (i) descrever a cobertura de água, esgoto e lixo nos municípios; (ii) aplicar modelos de "
            "probabilidade e testes de hipóteses a indicadores de saneamento e educação; (iii) medir a relação entre urbanização e coleta de "
            "lixo; (iv) modelar a cobertura de esgoto a partir de fatores estruturais; e (v) classificar os municípios quanto ao risco de "
            "esgoto inadequado.")]

# ---------- 3. dados e metodologia
story += [P("3. Dados e procedimentos", "h1"),
          P("Todos os dados são <b>reais e oficiais</b>, obtidos pela API pública do Sistema IBGE de Recuperação Automática (SIDRA, "
            "https://apisidra.ibge.gov.br). A coleta é automatizada (<i>src/01_coleta_dados.py</i>) e cada tabela é salva sem alterações em "
            "<i>data/raw/</i>."),
          tabela([["Tabela SIDRA", "Conteúdo", "Variável derivada"],
                  ["4714 (Censo 2022)", "População, área e densidade", "populacao, densidade_hab_km2, log_densidade"],
                  ["9923 (Censo 2022)", "População por situação do domicílio", "pct_pop_urbana"],
                  ["6805 (Censo 2022)", "Domicílios por tipo de esgotamento", "pct_esgoto_rede, esgoto_adequado"],
                  ["6803 (Censo 2022)", "Domicílios por forma de abastecimento de água", "pct_agua_rede"],
                  ["6892 (Censo 2022)", "Domicílios por destino do lixo", "pct_lixo_coletado"],
                  ["9543 (Censo 2022)", "Taxa de alfabetização (15 anos ou mais)", "taxa_alfabetizacao"],
                  ["5938 (PIB Mun. 2021)", "PIB, VAB total e VAB agropecuário", "pib_per_capita, log_pib_per_capita, pct_vab_agro"]],
                 [3.3, 6.2, 6.5]),
          P("<b>Tratamento</b> (<i>src/02_tratamento_dados.py</i>): as tabelas foram unidas pelo código IBGE do município. Os símbolos do SIDRA "
            "para valor inexistente ('-', '...', 'X') foram convertidos em ausentes, e os registros incompletos foram removidos "
            f"(5.570 → {f(R['n'], 0).replace(',00', '')} municípios). Foram criadas as variáveis PIB per capita (PIB 2021 ÷ população 2022), "
            "participação da agropecuária no VAB, logaritmos da densidade e do PIB per capita (para reduzir a assimetria) e a variável binária "
            "<b>esgoto_adequado</b> = 1 quando ≥ 50% dos domicílios estão ligados à rede de esgoto."),
          P("<b>Ferramentas:</b> Python 3.12 com pandas, NumPy, SciPy, statsmodels, scikit-learn, matplotlib e seaborn. Todas as análises "
            "estão no notebook <i>notebooks/analise_estatistica.ipynb</i>, com as saídas preservadas. Sementes aleatórias fixas garantem "
            "a reprodutibilidade das amostras e da divisão treino/teste.")]

# ---------- 4. descritiva
linhas = [["Região", "Municípios", "Esgoto rede (%)", "Água rede (%)", "Lixo coletado (%)", "Pop. urbana (%)", "Alfabetização (%)", "Mun. com esgoto adequado (%)"]]
for r in R["regioes"]:
    linhas.append([r["regiao"], r["municipios"], f(r["esgoto_rede"], 1), f(r["agua_rede"], 1), f(r["lixo_coletado"], 1),
                   f(r["urbana"], 1), f(r["alfabetizacao"], 1), f(r["pct_esgoto_adequado"], 1)])
story += [PageBreak(), P("4. Análise descritiva", "h1"),
          fig("01_distribuicao_saneamento.png", "Figura 1 — Distribuição dos indicadores de saneamento entre os municípios (Censo 2022)."),
          P("A coleta de lixo e a água encanada têm distribuições concentradas em valores altos, ou seja, estão perto da universalização "
            f"na maioria dos municípios. O esgoto é o oposto: a distribuição é muito dispersa, com média de {f(R['media_esgoto'], 1)}% e "
            f"mediana de {f(R['mediana_esgoto'], 1)}%, e há um grande pico perto de zero. Um terço dos municípios praticamente não tem "
            "rede de esgoto."),
          tabela(linhas, [2.3, 1.7, 1.8, 1.8, 2.0, 1.9, 2.0, 2.5]),
          fig("02_esgoto_por_regiao.png", "Figura 2 — Domicílios ligados à rede de esgoto por grande região.", 13),
          P("A desigualdade regional é a característica mais marcante. O Norte tem a pior cobertura em todos os serviços. O Nordeste tem a "
            "menor alfabetização e baixa urbanização. O Sul, embora rico e alfabetizado, tem cobertura de esgoto em rede relativamente baixa, "
            "porque historicamente usa muitas fossas sépticas. O Sudeste concentra os municípios com esgoto adequado.")]

# ---------- 5. normal
story += [PageBreak(), P("5. Distribuição Normal de Probabilidade", "h1"),
          P(f"Variável: <b>taxa de alfabetização (15 anos ou mais)</b>, assumida como X ~ N(μ = {f(N['media'])}; σ = {f(N['sigma'])}). "
            f"A mediana observada é {f(N['mediana'])}%."),
          tabela([["Evento", "Cálculo", "Probabilidade", "Classificação"],
                  ["a) X < média", f"P(Z < 0)", f"{f(N['p_a'], 4)} ({pct(N['p_a'], 2)})", N["class_a"]],
                  ["b) X > mediana", f"P(Z > ({f(N['mediana'])} − {f(N['media'])}) / {f(N['sigma'])})",
                   f"{f(N['p_b'], 4)} ({pct(N['p_b'], 2)})", N["class_b"]]], [2.8, 5.8, 3.4, 4.0]),
          fig("03_distribuicao_normal.png", "Figura 3 — Curva normal ajustada à taxa de alfabetização e áreas das probabilidades calculadas."),
          P("<b>Interpretação.</b> (a) A média é o centro de simetria da normal, então a probabilidade de um município ter alfabetização abaixo "
            "da média é exatamente 50%: um <b>evento equiprovável</b>. (b) Como a mediana (90,7%) é maior que a média (88,2%), a probabilidade "
            f"de superar a mediana no modelo normal é de {pct(N['p_b'])}, um <b>evento improvável (pouco provável)</b>. Nos dados reais essa "
            "proporção é 50% por definição. A diferença mostra que a distribuição observada é <b>assimétrica à esquerda</b>: um grupo de "
            "municípios, concentrado no Nordeste, tem alfabetização muito abaixo do restante e puxa a média para baixo. A Figura 3 deixa "
            "isso claro, com dois 'picos' no histograma. A normal é útil como aproximação, mas subestima a concentração de municípios com "
            "alfabetização alta.")]

# ---------- 6. testes
story += [P("6. Testes de hipóteses para a média", "h1"),
          P(f"Variável: <b>% de domicílios com água da rede geral</b>. Média populacional de referência μ<sub>0</sub> = {f(TA['mu0'])}% e "
            f"desvio padrão populacional σ = {f(TA['sigma'])} p.p. (calculados sobre todos os municípios). Como σ é conhecido, aplicou-se o "
            "teste Z, Z = (x̄ − μ<sub>0</sub>) / (σ/√n), em amostras aleatórias simples sorteadas com semente fixa."),
          tabela([["", "Hipóteses", "α", "n", "x̄", "Z calc.", "Z crítico", "p-valor", "Decisão"],
                  ["a)", "H0: μ = μ0  ×  H1: μ < μ0", "6%", TA["n"], f(TA["xbar"]), f(TA["z"], 3), f(TA["z_critico"], 3),
                   f(TA["p_valor"], 4), "Rejeita H0" if TA["rejeita_h0"] else "Não rejeita H0"],
                  ["b)", "H0: μ = μ0  ×  H1: μ > μ0", "9%", TB["n"], f(TB["xbar"]), f(TB["z"], 3), f(TB["z_critico"], 3),
                   f(TB["p_valor"], 4), "Rejeita H0" if TB["rejeita_h0"] else "Não rejeita H0"]],
                 [0.8, 4.2, 1.0, 0.9, 1.4, 1.5, 1.6, 1.6, 2.3]),
          fig("04_testes_hipotese.png", "Figura 4 — Estatística Z calculada e regiões críticas dos testes unilaterais."),
          P(f"<b>Interpretação.</b> (a) A amostra de 20 municípios teve média de {f(TA['xbar'], 1)}%, <b>acima</b> da referência. Por isso a "
            "estatística Z ficou positiva, longe da região crítica à esquerda, e <b>não há evidência</b> de que a cobertura de água seja "
            f"menor que a média nacional. (b) A amostra de 25 municípios teve média de {f(TB['xbar'], 1)}%, com Z = {f(TB['z'], 2)} acima do "
            f"valor crítico ({f(TB['z_critico'], 3)}) e p-valor de {f(TB['p_valor'], 3)} &lt; 0,09, o que leva a <b>rejeitar H0</b> e a "
            "concluir, ao nível de 9%, que a média é maior que a referência."),
          P("<b>Leitura crítica:</b> como μ<sub>0</sub> é a própria média de todos os municípios, a rejeição em (b) é um exemplo de "
            "<b>erro tipo I</b>, cuja probabilidade é α = 9%. Para quem toma decisões, a lição é que conclusões tiradas de amostras pequenas "
            "dependem da amostra sorteada e do nível de significância. Com uma base censitária completa disponível, ela deve ser preferida.")]

# ---------- 7. bivariada
prev_s = SI["previsoes"]
story += [PageBreak(), P("7. Análise bivariada: urbanização × coleta de lixo", "h1"),
          P("X = população urbana (%) e Y = domicílios com lixo coletado (%)."),
          fig("05_dispersao_bivariada.png", "Figura 5 — Gráfico de dispersão entre urbanização e coleta de lixo.", 12),
          P("<b>(a) Dispersão.</b> A nuvem de pontos é ascendente, o que indica <b>associação positiva</b>. A variabilidade da coleta é grande "
            "entre os municípios pouco urbanizados e diminui perto de 100% de urbanização, onde a coleta tende a ser universal. Esse padrão "
            "de variância desigual é chamado de heterocedasticidade."),
          tabela([["Medida", "Valor", "Interpretação"],
                  ["Covariância amostral", f(BV["cov"]), "Positiva: as variáveis crescem juntas (valor em %², não mede a força da relação)"],
                  ["Correlação de Pearson (r)", f(BV["r"], 4), "Correlação linear positiva forte (r > 0,7)"],
                  ["p-valor de r", "< 0,0001", "Correlação estatisticamente significativa"]], [4.2, 2.3, 9.5]),
          fig("06_correlacao_bivariada.png", "Figura 6 — Gráfico (mapa de calor) da correlação linear de Pearson.", 7),
          P("<b>(b, c) Correlação.</b> A covariância só indica a direção da relação. O coeficiente de Pearson, que é padronizado, mostra que a "
            f"relação é <b>positiva e forte</b> (r = {f(BV['r'], 3)}), como se vê na cor intensa do mapa de calor."),
          fig("07_regressao_simples.png", "Figura 7 — Reta de regressão linear simples sobre o gráfico de dispersão.", 12),
          P(f"<b>(d) Equação:</b>", "p"), P(f"Ŷ = {f(SI['b0'], 4)} + {f(SI['b1'], 4)} · X", "eq"),
          P(f"Cada ponto percentual a mais de população urbana aumenta a coleta de lixo esperada em <b>{f(SI['b1'], 2)} p.p.</b> Um "
            f"município hipotético totalmente rural teria {f(SI['b0'], 1)}% de coleta."),
          P(f"<b>(e) Adequação do modelo.</b> R² = {f(SI['r2'], 4)}: a urbanização explica <b>{pct(SI['r2'])}</b> da variação da coleta de lixo "
            f"entre os municípios. O teste F (F = {f(SI['F'], 1)}; p-valor &lt; 0,0001) rejeita H0: β<sub>1</sub> = 0, então o modelo é "
            "<b>significativo</b>. Os outros 45% da variação dependem de fatores fora do modelo, como renda, gestão municipal e relevo."),
          tabela([["Pop. urbana (%)", "Coleta de lixo prevista (%)"]] +
                 [[f(p["pct_pop_urbana"], 0), f(p["lixo_coletado_previsto"], 1)] for p in prev_s], [5, 5]),
          P("<b>(f) Previsão.</b> Um município 40% urbano teria cerca de 62% dos domicílios com coleta e um 90% urbano chegaria a cerca de "
            "94%. As previsões são médias condicionais e só devem ser feitas dentro da faixa observada de X.")]

# ---------- 8. múltipla
pm = MU["params"]
corr = MU.get("vif", {})
story += [PageBreak(), P("8. Regressão linear múltipla: o que explica a cobertura de esgoto", "h1"),
          P("Y = % de domicílios ligados à rede de esgoto; X<sub>1</sub> = população urbana (%); X<sub>2</sub> = taxa de alfabetização (%); "
            "X<sub>3</sub> = log<sub>10</sub>(densidade demográfica)."),
          fig("08_dispersao_multipla.png", "Figura 8 — Matriz de gráficos de dispersão (amostra aleatória de 2.000 municípios).", 10.5),
          P("<b>(a) Dispersão.</b> A cobertura de esgoto cresce com as três variáveis explicativas, de forma mais nítida com a urbanização e a "
            "densidade. Há muitos municípios com cobertura próxima de 0% em todas as faixas, até entre os urbanizados, o que mostra que a "
            "rede de esgoto também depende de decisões de investimento.")]
cm_ = R["corr_mult"]
nomes = {"pct_esgoto_rede": "Esgoto rede", "pct_pop_urbana": "Pop. urbana", "taxa_alfabetizacao": "Alfabetização", "log_densidade": "log Densidade"}
ordem = list(nomes)
story += [tabela([["Correlação"] + [nomes[c] for c in ordem]] +
                 [[nomes[l]] + [f(cm_[c][l], 3) for c in ordem] for l in ordem], [3.5, 3, 3, 3, 3]),
          fig("09_correlacao_multipla.png", "Figura 9 — Matriz de correlação de Pearson.", 8.5),
          P("<b>(b, c) Covariância e correlação.</b> Todas as covariâncias e correlações são positivas. A cobertura de esgoto tem correlação "
            f"<b>moderada</b> com a urbanização ({f(cm_['pct_esgoto_rede']['pct_pop_urbana'], 2)}), a densidade "
            f"({f(cm_['pct_esgoto_rede']['log_densidade'], 2)}) e a alfabetização ({f(cm_['pct_esgoto_rede']['taxa_alfabetizacao'], 2)}). "
            "Entre as explicativas, as correlações são de no máximo 0,46 e os VIF ficam entre 1,2 e 1,5, bem abaixo de 5, o que indica "
            "<b>ausência de multicolinearidade preocupante</b>. A matriz de covariância completa está no notebook."),
          P("<b>(d) Equação da regressão linear múltipla:</b>"),
          P(f"Ŷ = {f(pm['const'], 4)} + {f(pm['pct_pop_urbana'], 4)}·PopUrbana + {f(pm['taxa_alfabetizacao'], 4)}·Alfabetização + "
            f"{f(pm['log_densidade'], 4)}·log<sub>10</sub>(Densidade)", "eq"),
          tabela([["Variável", "Coeficiente", "p-valor", "Interpretação (mantidas as demais constantes)"],
                  ["Pop. urbana (%)", f(pm["pct_pop_urbana"], 4), "< 0,0001", f"+1 p.p. urbano → +{f(pm['pct_pop_urbana'], 2)} p.p. de esgoto"],
                  ["Alfabetização (%)", f(pm["taxa_alfabetizacao"], 4), "< 0,0001", f"+1 p.p. alfabetização → +{f(pm['taxa_alfabetizacao'], 2)} p.p. de esgoto"],
                  ["log10(Densidade)", f(pm["log_densidade"], 4), "< 0,0001", f"densidade 10× maior → +{f(pm['log_densidade'], 1)} p.p. de esgoto"]],
                 [3.3, 2.3, 2, 8.4]),
          P(f"<b>(e) Adequação.</b> R² = {f(MU['r2'], 4)} (R² ajustado = {f(MU['r2_adj'], 4)}): o modelo explica <b>{pct(MU['r2'])}</b> da "
            f"variação da cobertura de esgoto. O teste F (F = {f(MU['F'], 1)}; p-valor &lt; 0,0001) rejeita a hipótese de que todos os "
            "coeficientes sejam nulos, e cada coeficiente é individualmente significativo. O ajuste é moderado, o que é esperado: a existência "
            "de rede depende também do histórico de investimento das companhias estaduais e municipais, de fatores geográficos e de "
            "capacidade de gestão, que não estão no modelo.")]
linhas = [["Perfil", "Pop. urbana (%)", "Alfabetização (%)", "Densidade (hab/km²)", "Esgoto previsto (%)"]]
for p in MU["previsoes"]:
    linhas.append([p["index"], f(p["pct_pop_urbana"], 0), f(p["taxa_alfabetizacao"], 0), f(10 ** p["log_densidade"], 0), f(p["esgoto_previsto_%"], 1)])
story += [tabela(linhas, [6.5, 2.2, 2.4, 2.6, 2.3]),
          P("<b>(f) Previsão.</b> Um município rural, com baixa alfabetização e pouco denso teria cobertura prevista de cerca de 16%, menos "
            "da metade da média nacional. Com urbanização e alfabetização altas, a previsão sobe para cerca de 52%, e com densidade de "
            "300 hab/km² chega a cerca de 66%. O efeito da densidade reflete a <b>economia de escala da rede</b>: em áreas dispersas, o custo "
            "por domicílio ligado é muito maior.")]

# ---------- 9. logística
pl, od = LG["params"], LG["odds"]
cmx = LG["cm"]
story += [PageBreak(), P("9. Regressão logística binária: classificação do risco de esgoto inadequado", "h1"),
          P("Y = esgoto_adequado (1 se ≥ 50% dos domicílios estão ligados à rede; 0 caso contrário). Explicativas: população urbana, "
            "alfabetização, log<sub>10</sub>(densidade) e log<sub>10</sub>(PIB per capita). A base foi dividida em "
            f"{LG['n_treino']} municípios para treino (70%) e {LG['n_teste']} para teste (30%), de forma estratificada."),
          P("<b>(a) Equação:</b>"),
          P(f"logit(p) = {f(pl['const'], 4)} + {f(pl['pct_pop_urbana'], 4)}·PopUrbana + {f(pl['taxa_alfabetizacao'], 4)}·Alfabetização + "
            f"{f(pl['log_densidade'], 4)}·log<sub>10</sub>(Densidade) − {f(abs(pl['log_pib_per_capita']), 4)}·log<sub>10</sub>(PIBpc)"
            "<br/>p = 1 / (1 + e<super>−logit(p)</super>)", "eq"),
          tabela([["Variável", "Coeficiente", "Razão de chances", "Leitura"],
                  ["Pop. urbana (%)", f(pl["pct_pop_urbana"], 4), f(od["pct_pop_urbana"], 3), "+1 p.p. → chances +7,1%"],
                  ["Alfabetização (%)", f(pl["taxa_alfabetizacao"], 4), f(od["taxa_alfabetizacao"], 3), "+1 p.p. → chances +10,2%"],
                  ["log10(Densidade)", f(pl["log_densidade"], 4), f(od["log_densidade"], 3), "densidade 10× → chances × 1,69"],
                  ["log10(PIB per capita)", f(pl["log_pib_per_capita"], 4), f(od["log_pib_per_capita"], 3), "PIBpc 10× → chances × 0,35"]],
                 [3.8, 2.4, 2.8, 7]),
          P(f"Todos os coeficientes são significativos (p &lt; 0,001; pseudo-R² de McFadden = {f(LG['pseudo_r2'], 3)}). O resultado mais "
            "relevante para a política pública é o <b>sinal negativo do PIB per capita</b>: com urbanização, alfabetização e densidade fixas, "
            "municípios com PIB per capita alto, típicos do agronegócio, da mineração e da geração de energia, têm <b>menor</b> chance de "
            "esgoto adequado. Riqueza produzida no território não se converte automaticamente em infraestrutura de saneamento."),
          fig("10_matriz_confusao.png", "Figura 10 — Matriz de confusão na base de teste (ponto de corte = 0,5).", 9),
          tabela([["Métrica", "Valor", "Significado"],
                  ["Acurácia", pct(LG["acuracia"]), "Proporção total de acertos"],
                  ["Acurácia do modelo ingênuo", pct(LG["baseline"]), "Prever sempre 'inadequado' (classe majoritária)"],
                  ["Especificidade", pct(LG["especificidade"]), "Acertos entre os municípios com esgoto inadequado"],
                  ["Sensibilidade", pct(LG["sensibilidade"]), "Acertos entre os municípios com esgoto adequado"],
                  ["Precisão", pct(LG["precisao"]), "Dos previstos como adequados, quantos realmente são"]], [4.5, 2.5, 9]),
          P(f"<b>(b) Interpretação.</b> O modelo acertou {cmx[0][0]} municípios com esgoto inadequado e {cmx[1][1]} com esgoto adequado, "
            f"errando {cmx[0][1] + cmx[1][0]} de {LG['n_teste']}. A acurácia de {pct(LG['acuracia'])} supera em "
            f"{f(100 * (LG['acuracia'] - LG['baseline']), 1)} p.p. o modelo ingênuo. A especificidade alta mostra que o modelo é bom para "
            "<b>encontrar municípios com déficit</b>. A sensibilidade menor indica que alguns municípios com perfil desfavorável superaram a "
            "expectativa e têm boa cobertura, e esses casos podem servir de exemplo de boas práticas.")]
linhas = [["Perfil", "Urbana (%)", "Alfab. (%)", "Dens. (hab/km²)", "PIBpc (R$)", "P(adequado)", "Classe"]]
for p in LG["perfis"]:
    linhas.append([p["index"], f(p["pct_pop_urbana"], 0), f(p["taxa_alfabetizacao"], 0), f(10 ** p["log_densidade"], 0),
                   f(10 ** p["log_pib_per_capita"], 0), pct(p["prob_esgoto_adequado"]), p["classificacao"]])
story += [tabela(linhas, [5.2, 1.6, 1.6, 2.0, 1.9, 1.9, 2.3]),
          P("<b>(c) Classificação.</b> O perfil rural, de baixa alfabetização e baixa renda tem probabilidade de cerca de 4% de esgoto adequado "
            "(classe 0). O perfil intermediário fica em cerca de 38% (ainda classe 0). O perfil urbano, denso e alfabetizado chega a cerca "
            "de 87% (classe 1). Na prática, isso mostra que um município típico brasileiro, de porte e urbanização médios, ainda tende a "
            "não ter esgoto adequado.")]

# ---------- 10. conclusões
story += [PageBreak(), P("10. Conclusões e recomendações", "h1")]
story += bullets([
    "<b>O déficit de esgoto é o principal gargalo do saneamento municipal</b> e é muito desigual entre as regiões. Atingir a meta de 90% "
    "até 2033 exige um esforço concentrado no Norte, no Nordeste e nos municípios pequenos de todas as regiões.",
    "<b>Urbanização e densidade</b> são os fatores com maior associação com o acesso à rede, o que reflete a economia de escala das redes. "
    "Para o campo e as comunidades dispersas, a recomendação é investir em <b>soluções descentralizadas</b> (fossas sépticas adequadas, "
    "biodigestores, sistemas condominiais), em vez de tentar replicar a rede convencional.",
    "<b>A educação</b> aparece associada ao saneamento mesmo controlando pela urbanização. Isso é coerente com a ideia de que populações "
    "mais escolarizadas cobram mais e se mobilizam por infraestrutura, mas não prova causalidade.",
    "<b>PIB alto não garante saneamento:</b> municípios ricos em produção (agro, mineração, energia) devem ser alvo de mecanismos que "
    "convertam receita em infraestrutura, como contrapartidas e uso de royalties.",
    "<b>Ferramenta CitizenTech:</b> o modelo logístico, com apenas quatro indicadores públicos do IBGE, pode alimentar um painel de "
    "triagem que aponte municípios com alto risco de esgoto inadequado para fiscalização, financiamento ou apoio técnico.",
])
story += [P("11. Limitações", "h1")]
story += bullets([
    "Estudo <b>observacional e transversal</b>: as associações não provam relações de causa e efeito.",
    "O PIB é de 2021 e a população é de 2022 (o último PIB municipal com VAB por atividade disponível no SIDRA na coleta), uma pequena "
    "defasagem temporal no PIB per capita.",
    "A normalidade assumida nos itens de probabilidade e testes de hipóteses é uma <b>aproximação</b>: a alfabetização é assimétrica e "
    "bimodal.",
    "Os testes de hipóteses usam amostras pequenas sorteadas com semente fixa. Outras amostras podem levar a decisões diferentes, "
    "como discutido sobre o erro tipo I.",
    "As regressões lineares têm heterocedasticidade e resíduos não normais (a resposta é limitada entre 0% e 100%). Os coeficientes "
    "descrevem bem as tendências médias, mas os intervalos de confiança devem ser lidos com cautela. Modelos beta ou com erros robustos "
    "seriam extensões naturais.",
    "O limiar de 50% para 'esgoto adequado' é uma escolha analítica. A variável do Censo mede ligação à rede, não o <b>tratamento</b> do esgoto.",
    "A unidade de análise é o município: as conclusões não valem automaticamente para domicílios ou pessoas (falácia ecológica).",
])
story += [P("12. Referências", "h1")]
story += bullets([
    "IBGE. Censo Demográfico 2022 — tabelas 4714, 6803, 6805, 6892, 9543 e 9923. SIDRA. https://sidra.ibge.gov.br",
    "IBGE. Produto Interno Bruto dos Municípios 2021 — tabela 5938. SIDRA. https://sidra.ibge.gov.br",
    "BRASIL. Lei nº 11.445/2007 e Lei nº 14.026/2020 (Novo Marco Legal do Saneamento Básico).",
    "Repositório do trabalho: códigos, base de dados e notebook com saídas — ver README.md.",
])

doc = SimpleDocTemplate(str(RAIZ / "reports" / "relatorio_estatistico.pdf"), pagesize=A4,
                        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2 * cm,
                        title="Relatório Estatístico — Saneamento nos municípios brasileiros", author="Grupo GS MLAM")
doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=rodape)
print("PDF gerado em reports/relatorio_estatistico.pdf")
