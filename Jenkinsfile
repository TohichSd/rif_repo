pipeline {
    agent { label 'docker' }

    options {
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
    }

    triggers {
        githubPush()
    }

    stages {
        stage('Build Docker image') {
            steps {
                sh 'docker build --tag "rif-practice-case4:$GIT_COMMIT" .'
            }
        }

        stage('Check /health') {
            steps {
                sh '''
                    container_id=$(docker run --detach "rif-practice-case4:$GIT_COMMIT")
                    trap 'docker rm -f "$container_id" >/dev/null' EXIT
                    if ! docker exec -i "$container_id" python - <<'PYTHON'
import json
import time
from urllib.error import URLError
from urllib.request import urlopen

for attempt in range(15):
    try:
        with urlopen("http://127.0.0.1:8080/health", timeout=2) as response:
            result = json.load(response)
        if result != {"status": "ok"}:
            raise SystemExit(f"Unexpected response: {result!r}")
        print(result)
        break
    except URLError:
        if attempt == 14:
            raise
        time.sleep(1)
PYTHON
                    then
                        docker logs "$container_id"
                        exit 1
                    fi
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    sh '''
                        set +x
                        export DOCKER_CONFIG="$(mktemp -d)"
                        trap 'rm -rf "$DOCKER_CONFIG"' EXIT
                        printf '%s\n' "$DOCKERHUB_TOKEN" |
                            docker login --username "$DOCKERHUB_USER" --password-stdin
                        local_image="rif-practice-case4:$GIT_COMMIT"
                        remote_image="docker.io/$DOCKERHUB_USER/$local_image"
                        docker tag "$local_image" "$remote_image"
                        docker push "$remote_image"
                    '''
                }
            }
        }
    }
}
