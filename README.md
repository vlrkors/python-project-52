### Статус тестов и линтера
[![Actions Status](https://github.com/vlrkors/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/vlrkors/python-project-52/actions)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=vlrkors_python-project-52&metric=coverage)](https://sonarcloud.io/summary/new_code?id=vlrkors_python-project-52)

# Менеджер задач

Django-приложение для создания, отслеживания и управления задачами со статусами и метками.

## Возможности

- Аутентификация и авторизация пользователей
- CRUD для задач
- Управление статусами задач
- Метки для категоризации
- Интернационализация (i18n)
- Адаптивный интерфейс на Bootstrap 5

## Технологии

- Python 3.11+
- Django 5.2
- PostgreSQL
- Bootstrap 5

## Установка

```bash
make install
make migrate
make run
```

## Использование

- Локально: выполните команды из раздела «Установка», затем откройте http://127.0.0.1:8000
- Онлайн: https://python-project-52-z358.onrender.com

## Разработка

- Тесты: `make test`
- Линтинг: `make lint`
