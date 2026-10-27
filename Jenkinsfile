pipeline {
    agent any

    triggers {
        pollSCM('* * * * *')
    }

    environment {
        IMAGE_NAME = 'sentiment-service'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = 'sentiment-service'
        DOCKER_NETWORK = 'progetto_modulo_deploy_default'
        NOTIFICATION_EMAIL = 'noemi.soluri@ifm.it'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Download del codice sorgente dal repository GitHub...'
                checkout scm
            }
        }

        stage('Docker Build') {
            steps {
                echo "Compilazione dell'immagine Docker in locale (${IMAGE_NAME}:latest)..."
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                """
            }
        }

        stage('Test Automatici') {
            steps {
                echo 'Esecuzione dei test Pytest nel container...'
                sh """
                    docker run --rm -e PYTHONPATH=/app ${IMAGE_NAME}:latest pytest tests/ -v
                """
            }
        }

        stage('Deploy') {
            steps {
                echo 'Avvio e aggiornamento del container sentiment-service...'
                sh """
                    # Ferma e rimuove il container precedente se già presente
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true

                    # Avvio del container collegato alla rete di Prometheus e cAdvisor
                    docker run -d \
                      --name ${CONTAINER_NAME} \
                      --network ${DOCKER_NETWORK} \
                      -p 8000:8000 \
                      --restart unless-stopped \
                      ${IMAGE_NAME}:latest
                """
            }
        }
    }

post {
        success {
            echo "Pipeline completata con successo! Container ${CONTAINER_NAME} avviato."
            script {
                try {
                    mail to: "${env.NOTIFICATION_EMAIL}",
                         subject: "OK: Pipeline Jenkins #${env.BUILD_NUMBER} - ${env.JOB_NAME}",
                         body: "Build #${env.BUILD_NUMBER} completata con successo sul container ${CONTAINER_NAME}."
                } catch (Exception e) {
                    echo "Notifica e-mail non inviata (server SMTP non configurato): ${e.message}"
                }
            }
        }

        failure {
            echo "Pipeline fallita. Controllare i log dello stage interessato."
            script {
                try {
                    mail to: "${env.NOTIFICATION_EMAIL}",
                         subject: "KO: Pipeline Jenkins #${env.BUILD_NUMBER} - ${env.JOB_NAME}",
                         body: "Build #${env.BUILD_NUMBER} fallita. Verificare la console: ${env.BUILD_URL}console"
                } catch (Exception e) {
                    echo "Notifica e-mail non inviata (server SMTP non configurato): ${e.message}"
                }
            }
        }
    }
}