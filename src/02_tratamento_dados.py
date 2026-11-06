"""
02_tratamento_dados.py
----------------------
Lê as tabelas brutas do SIDRA/IBGE (data/raw/), une tudo em uma linha por
município, cria as variáveis derivadas e salva a base final em
data/processed/base_saneamento_municipios_2022.csv (e .xlsx).

Execução (a partir da raiz do repositório):
    python src/02_tratamento_dados.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
PROC = RAIZ / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

COL_COD = "Município (Código)"
COL_NOME = "Município"
COL_VAR = "Variável (Código)"

REGIOES = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}


def ler(arquivo: str) -> pd.DataFrame:
    df = pd.read_csv(RAW / arquivo, dtype=str, encoding="utf-8")
    # No SIDRA, "-", "..", "...", "X" indicam valor inexistente ou sigiloso -> NaN
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    return df


def pivotar(df: pd.DataFrame, nomes: dict) -> pd.DataFrame:
    """Uma coluna por variável (código SIDRA -> nome amigável)."""
    p = df.pivot_table(index=COL_COD, columns=COL_VAR, values="Valor", aggfunc="first")
    p = p.rename(columns=nomes)
    return p[list(nomes.values())]


def serie(df: pd.DataFrame, nome: str) -> pd.Series:
    return df.set_index(COL_COD)["Valor"].rename(nome)


def main() -> None:
    pop = ler("sidra_4714_populacao_area_densidade_2022.csv")
    base = pivotar(pop, {"93": "populacao", "6318": "area_km2", "614": "densidade_hab_km2"})

    nomes = pop.drop_duplicates(COL_COD).set_index(COL_COD)[COL_NOME]
    base.insert(0, "municipio", nomes.str.rsplit(" - ", n=1).str[0])
    base.insert(1, "uf", nomes.str.rsplit(" - ", n=1).str[1])
    base.insert(2, "regiao", base.index.str[0].map(REGIOES))

    base = base.join(serie(ler("sidra_9923_populacao_situacao_domicilio_2022.csv"), "pct_pop_urbana"))
    base = base.join(serie(ler("sidra_6805_esgotamento_sanitario_2022.csv"), "pct_esgoto_rede"))
    base = base.join(serie(ler("sidra_6803_abastecimento_agua_2022.csv"), "pct_agua_rede"))
    base = base.join(serie(ler("sidra_6892_destino_lixo_2022.csv"), "pct_lixo_coletado"))
    base = base.join(serie(ler("sidra_9543_alfabetizacao_2022.csv"), "taxa_alfabetizacao"))

    pib = pivotar(ler("sidra_5938_pib_municipios_2021.csv"),
                  {"37": "pib_mil_reais", "498": "vab_total_mil_reais", "513": "vab_agro_mil_reais"})
    base = base.join(pib)

    # ---- variáveis derivadas -------------------------------------------------
    base["pib_per_capita"] = base["pib_mil_reais"] * 1000 / base["populacao"]
    base["pct_vab_agro"] = 100 * base["vab_agro_mil_reais"] / base["vab_total_mil_reais"]
    base["log_pib_per_capita"] = np.log10(base["pib_per_capita"])
    base["log_densidade"] = np.log10(base["densidade_hab_km2"])
    # variável binária (alvo da regressão logística):
    # 1 = pelo menos metade dos domicílios ligados à rede de esgoto
    base["esgoto_adequado"] = (base["pct_esgoto_rede"] >= 50).astype(int)

    base.index.name = "codigo_ibge"
    antes = len(base)
    base = base.dropna(subset=["populacao", "pct_esgoto_rede", "pct_agua_rede", "pct_lixo_coletado",
                               "taxa_alfabetizacao", "pct_pop_urbana", "pib_per_capita", "pct_vab_agro"])
    print(f"Municípios: {antes} -> {len(base)} após remover registros com dados ausentes")

    base = base.drop(columns=["vab_total_mil_reais", "vab_agro_mil_reais"])
    base = base.round(4)
    base.to_csv(PROC / "base_saneamento_municipios_2022.csv", encoding="utf-8")
    base.to_excel(PROC / "base_saneamento_municipios_2022.xlsx")
    print(base.describe().T.round(2).to_string())
    print("\nesgoto_adequado:", base["esgoto_adequado"].value_counts().to_dict())


if __name__ == "__main__":
    main()
