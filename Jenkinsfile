pipeline {
    agent { label 'docker && linux && local' }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
        skipDefaultCheckout()
        timestamps()
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

        JENKINS_HTTP_PORT = '8081'
        JENKINS_ADMIN_ID = 'admin'
        JENKINS_ADMIN_PASSWORD = 'change-me-jenkins'
        JENKINS_AGENT_NAME = 'docker-agent'
        JENKINS_AGENT_SECRET = ''
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh '''
                    set -euxo pipefail
                    git rev-parse --short HEAD
                    git status --short
                '''
            }
        }

        stage('Validate Environment') {
            steps {
                sh '''
                    set -euxo pipefail
                    echo "Running on node: $(hostname)"
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

        stage('Prepare CI Env File') {
            steps {
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

JENKINS_HTTP_PORT=${JENKINS_HTTP_PORT}
JENKINS_ADMIN_ID=${JENKINS_ADMIN_ID}
JENKINS_ADMIN_PASSWORD=${JENKINS_ADMIN_PASSWORD}
JENKINS_AGENT_NAME=${JENKINS_AGENT_NAME}
JENKINS_AGENT_SECRET=${JENKINS_AGENT_SECRET}
EOF
                '''
            }
        }

        stage('Validate Compose Configuration') {
            steps {
                sh '''
                    set -euxo pipefail
                    docker compose -p "${COMPOSE_PROJECT_NAME}" config >/dev/null
                '''
            }
        }

        stage('Prepare Python') {
            steps {
                sh '''
                    set -euxo pipefail
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt -r requirements-dev.txt
                '''
            }
        }

        stage('Prepare Test Database') {
            steps {
                sh '''
                    set -euxo pipefail

                    docker compose -p "${COMPOSE_PROJECT_NAME}" up -d postgres

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

        stage('Run Tests') {
            steps {
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

    post {
        always {
            junit testResults: 'validation/test-results/phase-08/junit.xml', allowEmptyResults: false
            archiveArtifacts artifacts: 'validation/test-results/phase-08/**', fingerprint: true, onlyIfSuccessful: false
        }
    }
}