pipeline {
    agent { label 'docker && linux && local' }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
        skipDefaultCheckout()
        timestamps()
    }

    parameters {
        booleanParam(name: 'RUN_DEPLOY', defaultValue: true, description: 'Run local blue/green deployment after CI')
    }

    environment {
        COMPOSE_PROJECT_NAME = 'opsledger-platform'

        APP_NAME = 'opsledger-platform'
        APP_ENV = 'local'
        APP_VERSION = '0.1.0'

        APP_PORT = '8000'
        NGINX_PORT = '8080'

        POSTGRES_DB = 'opsledger'
        POSTGRES_USER = 'opsledger'
        POSTGRES_PASSWORD = 'change-me'
        POSTGRES_PORT = '5433'

        DATABASE_URL = 'postgresql+psycopg://opsledger:change-me@postgres:5432/opsledger'
        TEST_DATABASE_URL = 'postgresql+psycopg://opsledger:change-me@postgres:5432/opsledger_test'
    }

    stages {
        stage('Validate Host CI Workspace') {
            steps {
                sh '''
                    set -euxo pipefail
                    test -n "${HOST_CI_ROOT:-}"
                    mkdir -p "${HOST_CI_ROOT}"
                    test -d "${HOST_CI_ROOT}"
                '''
            }
        }

        stage('Checkout') {
            steps {
                dir("${env.HOST_CI_ROOT}/opsledger-ci-workspace") {
                    deleteDir()
                    checkout scm
                    sh '''
                        set -euxo pipefail
                        git rev-parse --short HEAD
                        git status --short
                    '''
                }
            }
        }

        stage('Validate Environment') {
            steps {
                dir("${env.HOST_CI_ROOT}/opsledger-ci-workspace") {
                    sh '''
                        set -euxo pipefail
                        echo "Running on node: $(hostname)"
                        echo "CI workspace: ${PWD}"
                        python3 --version
                        pip3 --version
                        git --version
                        docker --version
                        docker compose version
                        make --version | head -n 1
                        jq --version
                    '''
                }
            }
        }

        stage('Prepare CI Env File') {
            steps {
                dir("${env.HOST_CI_ROOT}/opsledger-ci-workspace") {
                    sh '''
                        set -euxo pipefail
                        cat > .env <<EOF
APP_NAME=${APP_NAME}
APP_ENV=${APP_ENV}
APP_VERSION=${APP_VERSION}

APP_PORT=${APP_PORT}
NGINX_PORT=${NGINX_PORT}

POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_PORT=${POSTGRES_PORT}

DATABASE_URL=${DATABASE_URL}

ACTIVE_COLOR=blue
HOST_CI_ROOT=/home/angelsediez/jenkins-workspaces
EOF
                    '''
                }
            }
        }

        stage('Validate Compose Configuration') {
            steps {
                dir("${env.HOST_CI_ROOT}/opsledger-ci-workspace") {
                    sh '''
                        set -euxo pipefail
                        docker compose -p "${COMPOSE_PROJECT_NAME}" config >/dev/null
                    '''
                }
            }
        }

        stage('Prepare Python') {
            steps {
                dir("${env.HOST_CI_ROOT}/opsledger-ci-workspace") {
                    sh '''
                        set -euxo pipefail
                        python3 -m venv .venv
                        . .venv/bin/activate
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt -r requirements-dev.txt
                    '''
                }
            }
        }

        stage('Prepare Test Database') {
            steps {
                dir("${env.HOST_CI_ROOT}/opsledger-ci-workspace") {
                    sh '''
                        set -euxo pipefail

                        docker compose -p "${COMPOSE_PROJECT_NAME}" up -d postgres --remove-orphans

                        POSTGRES_CID="$(docker compose -p "${COMPOSE_PROJECT_NAME}" ps -q postgres)"

                        until [ "$(docker inspect --format='{{.State.Health.Status}}' "${POSTGRES_CID}")" = "healthy" ]; do
                          echo "Waiting for postgres to become healthy..."
                          sleep 2
                        done

                        docker compose -p "${COMPOSE_PROJECT_NAME}" exec -T postgres \
                          psql -U "${POSTGRES_USER}" -d postgres \
                          -c "DROP DATABASE IF EXISTS opsledger_test WITH (FORCE);"

                        docker compose -p "${COMPOSE_PROJECT_NAME}" exec -T postgres \
                          psql -U "${POSTGRES_USER}" -d postgres \
                          -c "CREATE DATABASE opsledger_test;"
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                dir("${env.HOST_CI_ROOT}/opsledger-ci-workspace") {
                    sh '''
                        set -euxo pipefail

                        mkdir -p validation/test-results/phase-08

                        . .venv/bin/activate
                        export TEST_DATABASE_URL="${TEST_DATABASE_URL}"

                        pytest \
                          --cov=app \
                          --cov-report=term-missing \
                          --cov-report=html:validation/test-results/phase-08/htmlcov \
                          --junit-xml=validation/test-results/phase-08/junit.xml \
                          tests | tee validation/test-results/phase-08/pytest-output.txt
                    '''
                }
            }
        }

        stage('Deploy Inactive Color') {
            when {
                expression { return params.RUN_DEPLOY }
            }
            steps {
                dir("${env.HOST_CI_ROOT}/opsledger-ci-workspace") {
                    sh '''
                        set -euxo pipefail
                        chmod +x scripts/*.sh

                        docker compose -p "${COMPOSE_PROJECT_NAME}" up -d --build --remove-orphans postgres app_blue app_green nginx
                        docker compose -p "${COMPOSE_PROJECT_NAME}" exec -T app_blue alembic upgrade head

                        ./scripts/deploy-blue-green.sh
                    '''
                }
            }
        }

        stage('Verify Switched Traffic') {
            when {
                expression { return params.RUN_DEPLOY }
            }
            steps {
                dir("${env.HOST_CI_ROOT}/opsledger-ci-workspace") {
                    sh '''
                        set -euxo pipefail
                        ACTIVE_COLOR="$(./scripts/get-active-color.sh)"
                        echo "Active color after deployment: ${ACTIVE_COLOR}"

                        curl -fsS http://nginx/health/ready | jq .

                        HEADER_COLOR=""
                        for i in $(seq 1 15); do
                          HEADER_COLOR="$(curl -fsS -D - -o /dev/null http://nginx/health/live | tr -d '\\r' | awk -F': ' '/^X-OpsLedger-Active-Color:/{print $2}')"
                          echo "try ${i}: active=${ACTIVE_COLOR}, header=${HEADER_COLOR}"

                          if [ "${HEADER_COLOR}" = "${ACTIVE_COLOR}" ]; then
                            echo "Nginx header matches active color"
                            break
                          fi

                          sleep 1
                        done

                        test "${HEADER_COLOR}" = "${ACTIVE_COLOR}"
                    '''
                }
            }
        }
    }

    post {
        always {
            dir("${env.HOST_CI_ROOT}/opsledger-ci-workspace") {
                junit testResults: 'validation/test-results/phase-08/junit.xml', allowEmptyResults: false
                archiveArtifacts artifacts: 'validation/test-results/phase-08/**,validation/healthcheck-logs/phase-09/**', fingerprint: true, onlyIfSuccessful: false
            }
        }
    }
}