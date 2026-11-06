"""
01_coleta_dados.py
------------------
Baixa, da API SIDRA do IBGE (https://apisidra.ibge.gov.br), os dados municipais
brutos usados no trabalho e salva cada tabela em data/raw/ sem nenhuma alteração.

Execução (a partir da raiz do repositório):
    python src/01_coleta_dados.py
"""
from pathlib import Path
import time

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
PASTA_RAW = RAIZ / "data" / "raw"
PASTA_RAW.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://apisidra.ibge.gov.br/values"

# nome do arquivo -> (consulta SIDRA, descrição)
CONSULTAS = {
    "sidra_4714_populacao_area_densidade_2022.csv": (
        "/t/4714/n6/all/v/93,6318,614/p/2022",
        "Censo 2022 - População residente, área territorial e densidade demográfica",
    ),
    "sidra_9923_populacao_situacao_domicilio_2022.csv": (
        "/t/9923/n6/all/v/1000093/p/2022/c1/1",
        "Censo 2022 - % da população residente em situação urbana",
    ),
    "sidra_6805_esgotamento_sanitario_2022.csv": (
        "/t/6805/n6/all/v/1000381/p/2022/c11558/46290",
        "Censo 2022 - % de domicílios com esgoto ligado à rede geral, pluvial ou fossa ligada à rede",
    ),
    "sidra_6803_abastecimento_agua_2022.csv": (
        "/t/6803/n6/all/v/1000381/p/2022/c1821/72144",
        "Censo 2022 - % de domicílios ligados à rede geral de água e que a usam como forma principal",
    ),
    "sidra_6892_destino_lixo_2022.csv": (
        "/t/6892/n6/all/v/1000381/p/2022/c67/2520",
        "Censo 2022 - % de domicílios com lixo coletado",
    ),
    "sidra_9543_alfabetizacao_2022.csv": (
        "/t/9543/n6/all/v/2513/p/2022/c2/6794/c86/95251/c287/100362",
        "Censo 2022 - Taxa de alfabetização das pessoas de 15 anos ou mais",
    ),
    "sidra_5938_pib_municipios_2021.csv": (
        "/t/5938/n6/all/v/37,498,513/p/2021",
        "PIB dos Municípios 2021 (último ano com VAB por atividade disponível no SIDRA) - PIB, VAB total e VAB da agropecuária (mil R$)",
    ),
}


def baixar(consulta: str, tentativas: int = 4) -> pd.DataFrame:
    url = BASE_URL + consulta
    for i in range(1, tentativas + 1):
        try:
            resp = requests.get(url, timeout=300)
            resp.raise_for_status()
            dados = resp.json()
            # a primeira linha da resposta do SIDRA é o cabeçalho descritivo
            cabecalho, linhas = dados[0], dados[1:]
            df = pd.DataFrame(linhas)
            df = df.rename(columns=cabecalho)
            return df
        except Exception as erro:  # noqa: BLE001
            print(f"  tentativa {i} falhou: {erro}")
            time.sleep(5 * i)
    raise RuntimeError(f"Não foi possível baixar {url}")


def main() -> None:
    for arquivo, (consulta, descricao) in CONSULTAS.items():
        print(f"Baixando {descricao} ...")
        df = baixar(consulta)
        df.to_csv(PASTA_RAW / arquivo, index=False, encoding="utf-8")
        print(f"  -> {arquivo}: {len(df)} linhas  ({BASE_URL + consulta})")
    print("Coleta concluída.")


if __name__ == "__main__":
    main()
