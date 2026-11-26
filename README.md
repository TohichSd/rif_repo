# rif_repo

Репозиторий для Д/З 1 по разработке информационных систем.

## Автоматическая сборка

GitHub Actions запускает CI при каждом пуше в ветку. Job **Test and build** выполняет пять юнит-тестов, собирает исполняемый архив Python `app.pyz` и прикрепляет его к запуску как артефакт `rif-app`.

## Локальный запуск в PowerShell

Нужен Python 3.12.

```powershell
$env:PYTHONPATH = 'src'
$env:PYTHONDONTWRITEBYTECODE = '1'
python -m unittest discover -s tests -v
New-Item -ItemType Directory -Path dist -Force | Out-Null
python -m zipapp src -m app:main -o dist/app.pyz
python dist/app.pyz
```

Проверьте [локальный /health](http://127.0.0.1:8080/health). Приложение вернёт `{"status": "ok"}`.
