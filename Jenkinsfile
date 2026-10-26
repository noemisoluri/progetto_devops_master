pipeline {
    agent any

    triggers {
        pollSCM('* * * * *') 
    }

    environment {
        IMAGE_NAME = 'sentiment-service'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = 'sentiment-service'
        DOCKER_NETWORK = 'progetto_devops_master_default'
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
                echo 'Avvio del container sentiment-service...'
                sh """
                    # Ferma e rimuove il vecchio container se già in esecuzione
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true

                    # Avvia il nuovo container collegandolo alla rete del compose e esponendo la porta 8000
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
            echo "Pipeline completata! Container ${CONTAINER_NAME} avviato e raggiungibile su porta 8000."
        }
        failure {
            echo "Pipeline fallita. Controllare i log dello stage interessato."
        }
    }
}