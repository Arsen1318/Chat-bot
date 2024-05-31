# Тест на дружбу

## Описание проекта

"Тест на дружбу" — это Telegram бот, который позволяет пользователям пройти интересные опросы и узнать, насколько хорошо они знают своих друзей. Бот предоставляет разнообразные вопросы на различные темы и позволяет пользователям делиться своими результатами.

## Установка и запуск

### Требования

- Python 3.7+
- pip (Python package installer)
- Telegram Bot API Token

### Установка

1. Клонируйте репозиторий:

```bash
https://github.com/Arsen1318/Chat-bot
cd Chat-bot
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

### Настройка

1. Создайте нового бота в Telegram и получите токен API. Подробности можно найти в [официальной документации Telegram](https://core.telegram.org/bots#6-botfather).

2. Вставьте ваш токен API в файл `main.py`, заменив строку `TOKEN = 'your_telegram_bot_token'` на ваш фактический токен:

```python
# main.py
if __name__ == "__main__":
    TOKEN = 'your_telegram_bot_token'
    survey_bot = SurveyBot(TOKEN)
    survey_bot.run()
```

### Запуск

Запустите бота с помощью следующей команды:

```bash
python main.py
```

## Структура проекта

- `main.py`: основной файл проекта, содержащий логику работы бота.
- `opros.py`: файл с классами и данными для проведения опросов.
- `requirements.txt`: файл с зависимостями проекта.

## Зависимости

Проект использует следующие основные библиотеки:

- `pyTelegramBotAPI`: для взаимодействия с Telegram API.

Полный список зависимостей находится в файле `requirements.txt`.

## Вклад в проект

1. Форкните репозиторий.
2. Создайте новую ветку (`git checkout -b feature/amazing-feature`).
3. Внесите изменения и закоммитьте их (`git commit -am 'Add some amazing feature'`).
4. Отправьте изменения в удаленный репозиторий (`git push origin feature/amazing-feature`).
5. Создайте новый Pull Request.

