# rif_repo

Репозиторий для Д/З 1 по разработке информационных систем.

## Кейс 3. CircleCI и Heroku

Пуш в ветку `main2` запускает workflow **build-and-deploy**. Стадия **build** запускает тесты и собирает `app.pyz`. Стадия **deploy** отправляет проверенный коммит в Heroku и проверяет ответ `/health`.

1. В Heroku подготовьте отдельное приложение поколения **Cedar** с поддержкой Heroku Git и запущенным процессом **web**. Возьмите имя приложения и его точный HTTPS-адрес из Dashboard. Условия использования dyno зависят от выбранного плана. [Heroku Git](https://devcenter.heroku.com/articles/git)
2. В [CircleCI](https://app.circleci.com/) подключите этот GitHub-репозиторий. Выберите `.circleci/config.yml` как конфигурацию и **All pushes** как событие запуска. Фильтр в конфигурации оставляет сборку и деплой для ветки `main2`. [Настройка проекта CircleCI](https://circleci.com/docs/guides/getting-started/create-project/)
3. В **Project Settings → Environment Variables** сохраните `HEROKU_APP_NAME`, `HEROKU_APP_URL` и `HEROKU_API_KEY`. Сохраните API-ключ только в настройках CircleCI.
4. После подключения сделайте новый коммит в `main2` и отправьте его в GitHub. Проверьте зелёные задания **build** и **deploy**, затем откройте `/health` на адресе Heroku. Приложение вернёт `{"status": "ok"}`.

Для сдачи приложите скриншот успешного workflow в CircleCI и скриншот ответа `/health` с адресом приложения.

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
