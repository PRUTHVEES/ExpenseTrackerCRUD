pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                // Add your dependency installation command here
            }
        }

        stage('Build') {
            steps {
                echo 'Building the project...'
                // Add your build command here
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                // Add your test command here
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed!'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}