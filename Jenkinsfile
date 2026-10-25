pipeline {
    agent any

    triggers {
        pollSCM('* * * * *') 
    }

    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = 'noemisoluri/sentiment-service'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        CR_PAT_CREDENTIALS = credentials('ghcr-credentials')
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
                echo "Compilazione dell'immagine Docker (Tag: ${IMAGE_TAG} e latest)..."
                sh """
                    docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} -t ${REGISTRY}/${IMAGE_NAME}:latest .
                """
            }
        }

        stage('Test Automatici') {
            steps {
                echo 'Esecuzione dei test Pytest all\'interno del container...'
                sh """
                    docker run --rm ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} pytest tests/ -v
                """
            }
        }

        stage('Docker Push') {
            steps {
                echo "Autenticazione e push su GitHub Container Registry..."
                sh """
                    echo \$CR_PAT_CREDENTIALS_PSW | docker login ${REGISTRY} -u \$CR_PAT_CREDENTIALS_USR --password-stdin
                    docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${REGISTRY}/${IMAGE_NAME}:latest
                """
            }
        }
    }

    post {
        always {
            echo "Esecuzione logout dal registry Docker..."
            sh "docker logout ${REGISTRY} || true"
        }
        success {
            echo "Pipeline completata con successo! Nuova immagine rilasciata su GHCR: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "Build fallita. Controllare i log dello stage fallito per i dettagli dell'errore."
        }
    }
}