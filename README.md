# rif_repo

Репозиторий для Д/З 1 по разработке информационных систем.

## Кейс 4. Jenkins и Docker Hub

Jenkins собирает Docker-образ после пуша в ветку `main3`, проверяет `/health` в контейнере и публикует образ в Docker Hub с тегом, равным SHA коммита.

### Настройка Jenkins

1. Подготовьте Linux-агент Jenkins с меткой `docker`, доступом к Docker Engine, Git и установленными плагинами **Pipeline**, **Git**, **GitHub** и **Credentials Binding**.
2. В своём аккаунте Docker Hub создайте репозиторий `rif-practice-case4` и токен с правом записи. В Jenkins добавьте credential типа **Username with password** с ID `dockerhub`. Укажите имя пользователя Docker Hub и токен в поле пароля.
3. Создайте задачу типа **Pipeline**. В **Pipeline script from SCM → Git** укажите `https://github.com/TohichSd/rif_repo.git`, в **Branch Specifier** — `*/main3`, в **Script Path** — `Jenkinsfile`. Один раз нажмите **Build Now**, чтобы Jenkins загрузил Jenkinsfile и зарегистрировал триггер.
4. В GitHub добавьте webhook на `https://<адрес-jenkins>/github-webhook/`. Выберите **application/json** и событие **Just the push event**. Jenkins должен быть доступен GitHub по этому адресу. После нового пуша в `main3` проверьте автоматический запуск. [Jenkins и GitHub](https://www.jenkins.io/solutions/github/)

### Проверка образа на своём компьютере

```powershell
docker build -t rif-practice-case4:local .
docker run --rm -p 127.0.0.1:8080:8080 rif-practice-case4:local
```

Откройте [локальный /health](http://127.0.0.1:8080/health). Контейнер должен вернуть `{"status": "ok"}`.

Для сдачи покажите в Jenkins автоматический запуск с успешными стадиями сборки и публикации, а в Docker Hub — тег образа с SHA этого коммита.
