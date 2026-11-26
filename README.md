# rif_repo

Репозиторий для Д/З 1 по разработке информационных систем. Учебное HTTP-приложение возвращает имя сервиса на `/` и JSON `{"status": "ok"}` на `/health`. Оно собирается в исполняемый архив Python `app.pyz` и в Docker-образ.

## Карта заданий

| Кейс | Реализация | Что показать преподавателю |
| --- | --- | --- |
| 1. GitHub Actions | CI на каждый пуш в ветку, тесты и сборка `rif-app` | Успешный запуск CI и артефакт |
| 2. GitLab CI/CD | `unit-tests` на каждый пуш в ветку | Лог с пятью тестами в GitLab |
| 3. CircleCI → Heroku | Сборка и деплой при пуше в `main` | Успешный job и ответ Heroku на `/health` |
| 4. Docker → Docker Hub | `Dockerfile`, стадии Build image и Push to Docker Hub в Jenkins | Тег образа, совпадающий с SHA коммита |
| 5. Стадии Jenkins | Lint → Unit tests → Build image → Push to Docker Hub → Migrate database → Deploy | Статус всех стадий и ответ на `/health` |
| 6. Slack | GitHub Actions сообщает результат CI через Incoming Webhook | Сообщения о двух запусках, успешном и неуспешном |
| 7. Релизы | GitHub Actions создаёт релиз при пуше тега | Release notes, `app.pyz` и `SHA256SUMS` в релизе |
| 8. Kubernetes | GitLab Registry, GitLab Agent и Helm | Зелёный job `kubernetes`, готовый pod и ответ на `/health` |
| 9. Качество и безопасность | Ruff и Bandit в GitHub Actions на каждый пуш в ветку | Результат job **Ruff and Bandit** |
| 10. Миграции | Alembic перед выкладкой в Jenkins, Kubernetes и Heroku | Ревизия `0001` и таблица `practice_items` в PostgreSQL |

## Локальный запуск в PowerShell

```powershell
$env:PYTHONPATH = 'src'
$env:PYTHONDONTWRITEBYTECODE = '1'
python -m unittest discover -s tests -v
New-Item -ItemType Directory -Path dist -Force | Out-Null
python -m zipapp src -m app:main -o dist/app.pyz
python dist/app.pyz
```

Откройте [локальный /health](http://127.0.0.1:8080/health). Для запуска Docker-версии с PostgreSQL остановите процесс Python и выполните:

```powershell
$env:APP_IMAGE = 'rif-practice:local'
docker build -t $env:APP_IMAGE .
docker compose up -d --wait db
docker compose run --rm migrate
docker compose up -d --wait web
Invoke-RestMethod http://127.0.0.1:8088/health
docker compose exec -T db psql -U practice -d practice -c 'TABLE alembic_version;'
docker compose down
```

Учебная база Compose доступна внутри сети проекта. У неё отдельный Docker volume. Учётные данные в `compose.yaml` предназначены для локальной демонстрации.

## GitHub Actions, Slack и релизы

1. В **Actions** откройте запуск **CI**. Job **Container and PostgreSQL** собирает Docker-образ, поднимает PostgreSQL, дважды выполняет миграцию, проверяет таблицу и запрашивает `/health`.
2. В Slack включите [Incoming Webhooks](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/) для приложения и выберите учебный канал. В GitHub откройте **Settings → Secrets and variables → Actions** и сохраните URL в **Repository secret** под именем `SLACK_WEBHOOK_URL`. Запустите CI имеющейся кнопкой **Run workflow**. Пока секрета нет, в сводке job **Notify Slack** появляется подсказка о подключении.
3. Чтобы проверить уведомление об ошибке, запушьте в отдельную учебную ветку коммит с заведомо неверным ожидаемым значением в одном юнит-тесте. После проверки верните тест в этой ветке. Рабочая ветка для деплоя — `main`.
4. Для следующего релиза поставьте тег на проверенный коммит. GitHub сформирует changelog в описании релиза и приложит два файла:

```sh
git switch main
git pull --ff-only
git tag -a v0.1.1 -m "CI/CD practice v0.1.1"
git push origin v0.1.1
```

## GitLab и Kubernetes

1. Импортируйте GitHub-репозиторий в GitLab или создайте пустой проект и отправьте в него `main`. Включите Container Registry и убедитесь, что для проекта доступен runner с Docker executor. После пуша проверьте задания **unit-tests** и **container-image** в **Build → Pipelines**. [BuildKit в GitLab](https://docs.gitlab.com/ci/docker/using_buildkit/)
2. В GitLab зарегистрируйте [Kubernetes Agent](https://docs.gitlab.com/user/clusters/agent/ci_cd_workflow/) `rif-practice` в этом проекте и установите его в кластер по команде из GitLab. Задайте CI/CD variable `KUBE_CONTEXT` со значением `<группа>/<проект>:rif-practice`. Для доступа агенту нужны права в namespace на Helm release Secrets, Deployments, Services, Jobs и чтение Pods.
3. Создайте namespace `rif-practice`. В этом namespace создайте Secret `rif-database` с ключом `DATABASE_URL`, указывающим на доступный из кластера PostgreSQL. Создайте Secret `rif-registry` типа `kubernetes.io/dockerconfigjson` с GitLab Deploy Token, у которого есть `read_registry`. Значения передавайте из менеджера секретов и сохраняйте только в Kubernetes.
4. Следующий пуш в основную ветку GitLab запустит **kubernetes**. Helm сначала выполняет Job с Alembic, затем обновляет Deployment и ждёт готовности. [Helm chart hooks](https://helm.sh/docs/v3/topics/charts_hooks/)

```sh
kubectl -n rif-practice get deployment,pods,jobs
kubectl -n rif-practice logs job/rif-practice-migration
kubectl -n rif-practice port-forward svc/rif-practice 8080:80
```

С другого терминала запросите `http://127.0.0.1:8080/health`. Запуск повторного деплоя использует ту же базу. Ревизия останется в `alembic_version`.

## CircleCI и Heroku

1. Подключите этот GitHub-репозиторий в CircleCI и создайте триггер **Push** для конфигурации `.circleci/config.yml`. Фильтр в ней запускает деплой на `main`.
2. Используйте Heroku-приложение поколения **Cedar** со стеком **container** и доступной базой PostgreSQL. В Heroku должна быть задана `DATABASE_URL`; подключённый Heroku Postgres устанавливает её автоматически. Для публичной проверки у приложения должен быть запущен web dyno. План Heroku и использование базы могут быть платными. [Container Registry](https://devcenter.heroku.com/articles/container-registry-and-runtime)
3. В **CircleCI → Project Settings → Environment Variables** задайте `HEROKU_APP_NAME` и `HEROKU_API_KEY`. Новый пуш в `main` соберёт образы `web` и `release`, отправит их в Heroku и дождётся статуса релиза. Alembic работает в [Heroku Release Phase](https://devcenter.heroku.com/articles/release-phase). Откройте `/health` на URL из Heroku.

## Jenkins и Docker Hub

1. Подготовьте Linux-агент Jenkins с меткой `docker`, Docker Engine, Docker Compose v2, Git и curl. Учетная запись агента должна иметь доступ к Docker.
2. Создайте в своём аккаунте Docker Hub репозиторий `rif-practice`. В Jenkins добавьте credential типа **Username with password** с ID `dockerhub`. Укажите имя пользователя и Docker Hub access token с правом записи.
3. Создайте **Pipeline** с **Pipeline script from SCM**, Git URL этого репозитория, branch specifier `*/main` и script path `Jenkinsfile`. Установите GitHub plugin и настройте GitHub webhook на `https://<jenkins>/github-webhook/` для события **Push**. Один раз выполните **Build Now**, чтобы Jenkins загрузил скрипт и зарегистрировал триггер. [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/)
4. Проверьте стадии pipeline и тег образа в Docker Hub. На агенте Jenkins запросите `http://127.0.0.1:8088/health`. Версию схемы можно увидеть в логе стадии **Migrate database**.
