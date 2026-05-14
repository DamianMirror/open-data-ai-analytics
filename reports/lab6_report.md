# Лабораторна робота №6
## GitOps з використанням k3s та Argo CD

**Студент:** DamianMirror  
**Дата виконання:** 14 травня 2026  
**Репозиторій:** https://github.com/DamianMirror/open-data-ai-analytics

---

## Мета роботи

Налаштувати GitOps-підхід для автоматичного розгортання застосунку в Kubernetes-кластері з використанням Argo CD. Git-репозиторій виступає єдиним джерелом істини (single source of truth) — будь-яка зміна в репозиторії автоматично застосовується до кластера.

---

## Теоретична частина

### GitOps

GitOps — це методологія управління інфраструктурою та застосунками, де Git-репозиторій є декларативним описом бажаного стану системи. Основні принципи:

- **Декларативність** — стан системи описується YAML-маніфестами, а не скриптами
- **Версійність** — всі зміни фіксуються в git-історії з можливістю відкату
- **Автоматична синхронізація** — оператор (Argo CD) постійно звіряє реальний стан з описом у git
- **Self-healing** — при ручних змінах в кластері система автоматично відновлює стан з git

### Kubernetes та k3s

Kubernetes — система оркестрації контейнерів. k3s — легковагова дистрибуція Kubernetes від Rancher, оптимізована для edge-пристроїв та VM з обмеженими ресурсами. Встановлюється однією командою і займає менше 100MB пам'яті.

### Argo CD

Argo CD — декларативний GitOps-оператор для Kubernetes. Моніторить Git-репозиторій і автоматично синхронізує стан кластера з маніфестами у вказаній директорії.

---

## Практична частина

### 1. Структура GitOps-маніфестів

Маніфести для Kubernetes розміщені в директорії `gitops/app/`:

**`gitops/app/namespace.yaml`** — створення простору імен:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ukraine-app
```

**`gitops/app/deployment.yaml`** — конфігурація деплойменту:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ukraine-web
  namespace: ukraine-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ukraine-web
  template:
    metadata:
      labels:
        app: ukraine-web
    spec:
      containers:
        - name: ukraine-web
          image: nginx:alpine
          ports:
            - containerPort: 80
          env:
            - name: APP_VERSION
              value: "1.0"
```

**`gitops/app/service.yaml`** — сервіс типу NodePort:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: ukraine-web
  namespace: ukraine-app
spec:
  selector:
    app: ukraine-web
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
      nodePort: 30080
  type: NodePort
```

**`gitops/argocd/application.yaml`** — опис застосунку для Argo CD:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ukraine-analytics
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/DamianMirror/open-data-ai-analytics
    targetRevision: main
    path: gitops/app
  destination:
    server: https://kubernetes.default.svc
    namespace: ukraine-app
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### 2. Інфраструктура (Terraform + cloud-init)

k3s та Argo CD встановлюються автоматично через `cloud-init.yaml` при першому запуску Azure VM. Ключові кроки:

```bash
# Встановлення k3s без traefik (уникнення конфліктів портів)
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable=traefik" sh -

# Встановлення Argo CD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Зміна типу сервісу на NodePort (порт 30800)
kubectl patch svc argocd-server -n argocd -p '{"spec":{"type":"NodePort"}}'
kubectl patch svc argocd-server -n argocd --type=json \
  -p='[{"op":"replace","path":"/spec/ports/0/nodePort","value":30800}]'

# Розгортання Argo CD Application
kubectl apply -f /app/gitops/argocd/application.yaml
```

NSG Azure відкриває порти: **30800** (Argo CD UI) та **30080** (застосунок).

### 3. Перевірка готовності кластера

Після запуску VM перевіряємо статус подів Argo CD:

```bash
kubectl get pods -n argocd
```

**Скріншот 1 — Всі поди Argo CD запущені, отримання пароля адміністратора:**

![Argo CD pods running](lab6_report_images/Screenshot%202026-05-14%20172440.png)

Всі 7 подів Argo CD мають статус `Running`. Пароль адміністратора отримано командою:
```bash
kubectl get secret argocd-initial-admin-secret -n argocd \
  -o jsonpath="{.data.password}" | base64 -d
```

### 4. Вхід в Argo CD UI

Відкриваємо веб-інтерфейс за адресою `http://<PUBLIC_IP>:30800` та входимо з логіном `admin`.

**Скріншот 2 — Сторінка входу Argo CD:**

![Argo CD login page](lab6_report_images/Screenshot%202026-05-14%20172510.png)

### 5. Застосунок успішно синхронізовано

Argo CD автоматично виявив Application-маніфест і синхронізував стан кластера з Git-репозиторієм.

**Скріншот 3 — Картка застосунку ukraine-analytics:**

![Argo CD app card](lab6_report_images/Screenshot%202026-05-14%20172525.png)

Застосунок `ukraine-analytics` має статус **Healthy** і **Synced**. Argo CD відстежує гілку `main` репозиторію `github.com/DamianMirror/open-data-ai-analytics`, шлях `gitops/app`, простір імен `ukraine-app`.

**Скріншот 4 — Детальний вигляд з деревом ресурсів:**

![Argo CD app details](lab6_report_images/Screenshot%202026-05-14%20172541.png)

Дерево ресурсів показує повну ієрархію: `ukraine-analytics` → Namespace `ukraine-app` + Service `ukraine-web` + Deployment `ukraine-web` → ReplicaSet → Pod (1/1 Running). Автоматична синхронізація включена (`Auto sync is enabled`). Останній коміт: `743c68f`, коментар `fix: Argo`.

### 6. Демонстрація GitOps: зміна кількості реплік

Для демонстрації GitOps-підходу змінюємо `replicas: 1` на `replicas: 2` у файлі `gitops/app/deployment.yaml` та пушимо зміни до GitHub.

**Скріншот 5 — Diff у VS Code (replicas: 1 → 2):**

![Deployment diff in VS Code](lab6_report_images/Screenshot%202026-05-14%20173526.png)

VS Code показує порівняння версій файлу: зліва стара версія з `replicas: 1` (виділено червоним), справа нова версія з `replicas: 2` (виділено зеленим). Commit `f3b2b20`, коментар `feat: change replica count`.

**Скріншот 6 — Argo CD після автоматичної синхронізації:**

![Argo CD after scale to 2 replicas](lab6_report_images/Screenshot%202026-05-14%20173536.png)

Argo CD виявив зміну в Git та автоматично застосував її до кластера. Стан оновлено до коміту `f3b2b20`. Дерево ресурсів тепер відображає **2 поди** (`ukraine-web-6749b4dcb6-6cq...` та `ukraine-web-6749b4dcb6-249...`), обидва зі статусом `Running 1/1`. Один под запустився щойно (`a few seconds`), другий — 14 хвилин тому.

---

## Висновки

В ході лабораторної роботи:

1. **Налаштовано k3s** — легковагий Kubernetes-кластер на Azure VM, який автоматично розгортається через cloud-init при першому запуску інфраструктури.

2. **Встановлено та налаштовано Argo CD** — GitOps-оператор, що безперервно моніторить Git-репозиторій і синхронізує стан кластера з маніфестами.

3. **Реалізовано GitOps-пайплайн**: зміна в YAML-файлі → git push → автоматичне застосування змін до Kubernetes без ручного втручання.

4. **Продемонстровано auto-sync**: збільшення `replicas` з 1 до 2 у Git автоматично призвело до масштабування деплойменту в кластері протягом кількох хвилин.

5. **Основна перевага GitOps**: вся конфігурація версійована в Git, що забезпечує аудит змін, можливість відкату (History and Rollback у Argo CD) та відтворюваність інфраструктури.

---

## Використані технології

| Технологія | Версія | Призначення |
|---|---|---|
| k3s | stable | Легковагий Kubernetes |
| Argo CD | stable | GitOps-оператор |
| Terraform | ~3.0 (azurerm) | IaC для Azure |
| Azure VM | Standard_D2s_v6 | Хмарна інфраструктура |
| nginx:alpine | latest | Тестовий застосунок |
