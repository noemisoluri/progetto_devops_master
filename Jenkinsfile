pipeline {
    agent any

    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_NAME = 'noemisoluri/sentiment-service'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        CR_PAT_CREDENTIALS = credentials('ghcr-credentials')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scms
            }
        }

        stage('Test Automatici') {
            steps {
                echo 'Esecuzione dei test Pytest...'
                sh '''
                    python3 -m venv venv || python -m venv venv
                    . venv/bin/activate || ./venv/Scripts/activate
                    pip install --no-cache-dir -r requirements.txt
                    pytest tests/ -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo "Compilazione immagine Docker..."
                sh """
                    docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} -t ${REGISTRY}/${IMAGE_NAME}:latest .
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
            echo "Pulizia dell'ambiente di build..."
            sh "docker logout ${REGISTRY} || true"
        }
        success {
            echo "Pipeline completata con successo! Nuova immagine pubblicata: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "Errore durante l'esecuzione della pipeline. Controllare i log dello stage fallito."
        }
    }
}