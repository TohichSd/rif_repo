pipeline {
    agent { label 'docker' }

    options {
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
    }

    triggers {
        githubPush()
    }

    stages {
        stage('Lint') {
            steps {
                sh '''
                    docker run --rm -v "$PWD:/code:ro" -w /code python:3.12-slim-bookworm \
                      sh -ec 'python -m pip install --no-cache-dir -r requirements-ci.txt && python -m ruff check --no-cache src tests migrations'
                '''
            }
        }
        stage('Unit tests') {
            steps {
                sh '''
                    docker run --rm -e PYTHONPATH=/code/src -e PYTHONDONTWRITEBYTECODE=1 \
                      -v "$PWD:/code:ro" -w /code python:3.12-slim-bookworm \
                      python -m unittest discover -s tests -v
                '''
            }
        }
        stage('Build image') {
            steps {
                script {
                    env.APP_IMAGE = "rif-practice:${env.GIT_COMMIT}"
                }
                sh 'docker build --tag "$APP_IMAGE" .'
            }
        }
        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_TOKEN')]) {
                    sh '''
                        set +x
                        export DOCKER_CONFIG="$(mktemp -d)"
                        trap 'rm -rf "$DOCKER_CONFIG"' EXIT
                        printf '%s' "$DOCKERHUB_TOKEN" | docker login --username "$DOCKERHUB_USER" --password-stdin
                        docker tag "$APP_IMAGE" "$DOCKERHUB_USER/$APP_IMAGE"
                        docker push "$DOCKERHUB_USER/$APP_IMAGE"
                    '''
                }
            }
        }
        stage('Migrate database') {
            steps {
                sh '''
                    docker compose -p rif-practice up -d --wait --wait-timeout 90 db
                    docker compose -p rif-practice run --rm migrate
                    docker compose -p rif-practice exec -T db psql -U practice -d practice -c 'TABLE alembic_version;'
                '''
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                    docker compose -p rif-practice up -d --wait --wait-timeout 90 web
                    curl --fail --silent --show-error http://127.0.0.1:8088/health
                '''
            }
        }
    }
}
