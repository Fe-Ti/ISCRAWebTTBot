# ISCRA Task Tracking Bot

Проект чат-бота для управления СУП Redmine.

### Текущий список целей:
 - [X] Поддержка управления СУП Redmine
 - [X] Поддержка мессенджера Telegram
 - [ ] FAQ по СУПу и остальным вещам

### Зависимости не из стандартной библиотеки Python 3
* `redmine-bot` - библиотека обеспечивающая исполнение сценария
* `origamibot` - библиотека для связи с Telegram API

### Установка и запуск

1. Склонируйте репозиторий
2. Исправьте конфигурацию. На данный момент она находится в переменной `config`.
Параметры указанные ниже отвечают за соединение с сервером.
```python
    "use_https"             : False, # При False будет использован простой http
    "redmine_root_url"      : "localhost/redmine",
    "bot_user_key"          : "8e7a355d7f58e4b209b91d9d1f76f2a85ec4b0b6", # ключ API Redmine
```
3. Установите библиотеки:
```
pip install --upgrade redmine-bot origamibot
```
4. Запустите bot.py
```
python3 bot.py [ключ бота в Telegram]
```

```
Copyright 2023 Fe-Ti aka T.Kravchenko, ISCRA
```
