### Hexlet tests and linter status:
[![Actions Status](https://github.com/vlrkors/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/vlrkors/python-project-52/actions)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=vlrkors_python-project-52&metric=coverage)](https://sonarcloud.io/summary/new_code?id=vlrkors_python-project-52)

# Task Manager

A Django-based task management system that allows users to create, track, and manage tasks with statuses and labels.

## Features

- User authentication and authorization
- Task management (create, read, update, delete)
- Status management for tasks
- Label management for task categorization
- Internationalization support (i18n)
- Responsive design with Bootstrap 5

## Tech Stack

- Python 3.11+
- Django 5.2
- PostgreSQL
- Bootstrap 5

## Setup and Installation

```bash
make install
make migrate
make run
```

## Development

- Run tests: `make test`
- Check code style: `make lint`
