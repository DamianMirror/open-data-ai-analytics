"""
Завантаження датасету:
Основні прогнозні показники економічного і соціального розвитку України на 2020-2021 роки.
"""

import pathlib
import requests
import pandas as pd

DATASET_URL = (
    "https://data.gov.ua/dataset/175386f8-fbce-4352-8ec9-44fc8c436aa9"
    "/resource/6c67d91d-6455-472f-aeb1-f81fadd2cb37"
    "/download/nabir-16-2020-2021-roki_03-12-2018.csv"
)

PROJECT_ROOT = pathlib.Path(__file__).parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "nabir-16-2020-2021.csv"


def download(url: str = DATASET_URL, dest: pathlib.Path = RAW_PATH) -> pathlib.Path:
    """Завантажує CSV з відкритих даних. Пропускає, якщо файл вже існує."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"[skip] Файл вже існує: {dest}")
        return dest

    print(f"[download] {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    dest.write_bytes(response.content)
    print(f"[ok] Збережено: {dest} ({dest.stat().st_size} байт)")
    return dest


def load(path: pathlib.Path = RAW_PATH) -> pd.DataFrame:
    """Читає CSV у DataFrame, автоматично визначає кодування."""
    for encoding in ("utf-8", "cp1251", "latin-1"):
        try:
            df = pd.read_csv(path, encoding=encoding, sep=None, engine="python")
            print(f"[ok] Завантажено {len(df)} рядків, {len(df.columns)} колонок (encoding={encoding})")
            return df
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Не вдалося визначити кодування файлу: {path}")


if __name__ == "__main__":
    path = download()
    df = load(path)
    print(df.head())