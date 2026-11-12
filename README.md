# QA Hub: Единый репозиторий автоматизации тестирования

Централизованный тестовый фреймворк для сквозного контроля качества мобильных приложений (**Спортивный Гардероб**, **MaxFunFit**, **Матрешка**) и бэкенд-сервисов (**Парсер одежды**).

**Ответственный за QA:** Игорь  
**Стек:** Python 3.11, Pytest, Appium 2.x (UiAutomator2), Requests, Pydantic, Locust, GitHub Actions.

---

## 📁 Структура проекта

```text
├── .github/
│   └── workflows/
│       └── qa_pipeline.yml         # CI/CD: запуск по расписанию (cron) и вручную
├── core/
│   ├── __init__.py
│   └── config.py                   # Централизованная конфигурация и capabilities
├── tests/
│   ├── api/
│   │   ├── __init__.py
│   │   └── test_parser_api.py      # Интеграционные тесты API парсера
│   ├── e2e/
│   │   ├── __init__.py
│   │   └── test_wardrobe_flow.py   # Сквозной UI-тест мобильного приложения
│   └── performance/
│       ├── __init__.py
│       └── locustfile.py           # Шаблон нагрузочного тестирования API
├── .env.example                    # Шаблон переменных окружения
├── conftest.py                     # Глобальные фикстуры (Appium, API Session, отчеты)
├── pytest.ini                      # Настройки Pytest и маркеры
├── requirements.txt                # Зависимости проекта
└── README.md
```

---

## 🚀 Быстрый старт

### 1. Установка окружения

```bash
# Клонирование и переход в директорию
git clone <repo-url>
cd qa-hub

# Создание виртуального окружения Python 3.11
python -m venv .venv
source .venv/bin/activate  # Для Linux/macOS
# .venv\Scripts\activate   # Для Windows

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
```

### 2. Запуск API-тестов

Запуск проверки контрактов и эндпоинтов парсера с генерацией HTML-отчета:

```bash
pytest tests/api --html=reports/api_report.html --self-contained-html
```

### 3. Запуск мобильных E2E-тестов (Appium)

1. Запустите Appium Server:
   ```bash
   appium
   ```
2. Подключите Android устройство или запустите эмулятор (`adb devices`).
3. Запустите UI-тесты (по умолчанию для приложения *Спортивный Гардероб*):
   ```bash
   pytest tests/e2e --app=wardrobe --html=reports/e2e_report.html --self-contained-html
   ```

Для запуска тестов других приложений:
```bash
pytest tests/e2e --app=maxfunfit
pytest tests/e2e --app=matreshka
```

### 4. Запуск нагрузочного тестирования (Locust)

```bash
locust -f tests/performance/locustfile.py --host=https://api.staging.internal/parser
```

После запуска интерфейс Locust доступен по адресу: `http://localhost:8089`.

---

## 🔄 CI/CD (GitHub Actions)

Пайплайн настроен в [qa_pipeline.yml](file:///.github/workflows/qa_pipeline.yml):
* **Nightly Run:** Автоматический ежедневный прогон тестов в `02:00 UTC`.
* **Manual Dispatch:** Ручной запуск через вкладку Actions с параметрами выбора сьюта (`api`, `e2e`, `all`), целевого приложения (`wardrobe`, `maxfunfit`, `matreshka`) и окружения (`staging`, `production`).
* **Артефакты:** Все HTML-отчеты и скриншоты падений сохраняются в артефактах пайплайна на 14 дней.
