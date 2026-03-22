# Lab 2 Report: CI/CD Implementation

**Project:** Open Data AI Analytics
**Course:** Data Engineering / MLOps
**Date:** 2026-03-22

## Overview

This report documents the implementation of a complete CI/CD pipeline using GitHub Actions for automated testing, building, and deployment of data analytics modules.

## Огляд workflows

### 1. `ci.yml` - Основний CI pipeline (GitHub-hosted)

**Тригери:**
- Push у гілку `main`
- Pull requests до `main`
- Ручний запуск (workflow_dispatch) з вибором модуля

**Функціонал:**
- Паралельний запуск усіх модулів через matrix strategy
- Модулі: `data_load`, `data_quality_analysis`, `analysis_and_models`, `data_visualization`
- Виконання Python скриптів та Jupyter notebooks
- Конвертація notebooks у HTML формат
- Збереження артефактів (логи, звіти, графіки)
- **CD**: Автоматична публікація результатів у GitHub Pages після успішного CI на main

**Як запустити вручну:**
1. Перейдіть до вкладки "Actions" у репозиторії
2. Оберіть workflow "CI (modules)"
3. Натисніть "Run workflow"
4. Оберіть модуль для запуску (або "all" для всіх)

### 2. `ci-selfhosted.yml` - Self-hosted runner

**Тригери:**
- Тільки ручний запуск (workflow_dispatch)

**Функціонал:**
- Запуск на локальному runner (ваш ПК/сервер)
- Вибір конкретного модуля для запуску
- Збір метрик продуктивності (CPU, RAM, disk)
- Доступ до локальних ресурсів

**Переваги self-hosted:**
- Доступ до локальних великих датасетів
- Контроль над оточенням (GPU, спеціальні бібліотеки)
- Швидкість (залежить від вашого обладнання)
- Можливість використання приватних ресурсів

**Недоліки:**
- Потрібно підтримувати runner онлайн
- Безпека (runner має доступ до вашої машини)
- Необхідність самостійно оновлювати залежності

### 3. `ci-paths.yml` - Path-based filtering (Bonus)

**Тригери:**
- Push/PR з змінами у `src/`, `notebooks/`, або `requirements.txt`

**Функціонал:**
- Запускає тільки ті модулі, файли яких змінились
- Економить ресурси CI
- Використовує `dorny/paths-filter@v3` для детекції змін

## Налаштування GitHub Pages (для публікації результатів)

1. Перейдіть до **Settings** → **Pages**
2. У розділі "Source" оберіть **GitHub Actions**
3. Workflow `ci.yml` автоматично опублікує результати після push у main

Ваші результати будуть доступні за адресою:
```
https://<username>.github.io/<repository-name>/
```

## Налаштування Self-hosted Runner

### Крок 1: Додавання runner

1. Перейдіть до **Settings** → **Actions** → **Runners**
2. Натисніть **New self-hosted runner**
3. Оберіть вашу ОС (Linux/Windows/macOS)
4. Виконайте команди для завантаження та конфігурації

### Крок 2: Запуск runner (Linux/WSL)

```bash
# Завантаження
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Конфігурація (використайте токен з GitHub)
./config.sh --url https://github.com/<username>/<repo> --token <YOUR_TOKEN>

# Запуск
./run.sh
```

### Крок 3: Додавання labels (опціонально)

Під час конфігурації додайте labels, наприклад: `self-hosted,linux,local,wsl`

### Крок 4: Запуск як сервіс (для постійної роботи)

```bash
# Linux/WSL
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
```

### Для Windows:

```powershell
# Запуск як сервіс
.\svc.sh install
.\svc.sh start
```

## Артефакти

Після кожного запуску CI, результати зберігаються як артефакти:

- **Логи виконання**: `run.log`
- **HTML звіти**: Конвертовані Jupyter notebooks
- **Графіки**: Файли з `reports/figures/`
- **Статус**: Інформація про успішність виконання

**Де знайти артефакти:**
1. Перейдіть до вкладки **Actions**
2. Оберіть конкретний workflow run
3. Внизу сторінки в розділі **Artifacts** знайдете всі згенеровані файли

## Локальне тестування

Перед push можна протестувати локально:

```bash
# Встановити залежності
pip install -r requirements.txt

# Запустити data_load модуль
python -m src.data_load

# Виконати notebook
jupyter nbconvert --to html --execute notebooks/data_quality_analysis.ipynb
```

## Matrix Strategy

Workflow використовує matrix strategy для паралельного запуску модулів:

```yaml
strategy:
  fail-fast: false
  matrix:
    module: [data_load, data_quality_analysis, analysis_and_models, data_visualization]
```

Це створює 4 паралельні job-и, кожен для свого модуля.

## Секрети та змінні

Якщо потрібно додати секрети (API ключі, токени):

1. Перейдіть до **Settings** → **Secrets and variables** → **Actions**
2. Натисніть **New repository secret**
3. Використовуйте у workflow:

```yaml
env:
  API_KEY: ${{ secrets.MY_API_KEY }}
```

## Порівняння: GitHub-hosted vs Self-hosted

| Характеристика | GitHub-hosted | Self-hosted |
|----------------|---------------|-------------|
| Швидкість запуску | Швидко | Залежить від вашого ПК |
| Доступ до даних | Тільки з інтернету | Локальні датасети |
| Безпека | Ізольоване середовище | Ваша відповідальність |
| Вартість | Безкоштовно (ліміти) | Безкоштовно (ваше залізо) |
| Підтримка | GitHub | Ви самі |
| Offline робота | Ні | Можливо (з обмеженнями) |

## Виконання лабораторної роботи

### Частина A - CI
- Створено `ci.yml` з matrix strategy
- Тригери: push, pull_request, workflow_dispatch
- Паралельний запуск модулів
- Генерація артефактів

### Частина B - CD
- Варіант 1: GitHub Actions artifacts
- Варіант 2: GitHub Pages deployment

### Частина C - Self-hosted
- Створено `ci-selfhosted.yml`
- Інструкції з підключення runner
- Збір метрик продуктивності

### Bonus
- Path-based filtering (`ci-paths.yml`)
- Оптимізація запуску тільки змінених модулів

## Додаткові ресурси

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners)
- [GitHub Pages](https://docs.github.com/en/pages)
