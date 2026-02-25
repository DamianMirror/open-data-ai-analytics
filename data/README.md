# Дані

## Джерело

**Назва:** Основні прогнозні показники економічного і соціального розвитку України на 2020–2021 роки

**URL:** https://data.gov.ua/dataset/175386f8-fbce-4352-8ec9-44fc8c436aa9/resource/6c67d91d-6455-472f-aeb1-f81fadd2cb37/download/nabir-16-2020-2021-roki_03-12-2018.csv

**Формат:** CSV (кодування UTF-8)

## Зміст датасету

Файл містить прогнозні макроекономічні та соціальні показники України:

- Валовий внутрішній продукт (ВВП), млрд грн / % зміни
- Індекс інфляції (ІСЦ), %
- Рівень безробіття, %
- Реальна заробітна плата, % зміни
- Реальні наявні доходи населення, % зміни
- Експорт / імпорт товарів і послуг, млн дол. США

## Завантаження

Скрипт автоматичного завантаження:

```python
import requests, pathlib

URL = (
    "https://data.gov.ua/dataset/175386f8-fbce-4352-8ec9-44fc8c436aa9"
    "/resource/6c67d91d-6455-472f-aeb1-f81fadd2cb37"
    "/download/nabir-16-2020-2021-roki_03-12-2018.csv"
)

dest = pathlib.Path("data/raw/nabir-16-2020-2021.csv")
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_bytes(requests.get(URL).content)
print(f"Збережено: {dest}")
```

## Структура теки

```
data/
├── README.md          <- цей файл
└── raw/               <- завантажені оригінальні файли (у .gitignore)
```