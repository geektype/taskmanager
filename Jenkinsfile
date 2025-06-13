pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'task-manager-test'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                // Clean workspace before checkout
                cleanWs()
                // Checkout code from GitHub
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build Docker image
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run tests in Docker container
                    docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").inside {
                        // Start Xvfb for Chrome
                        sh 'Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &'
                        // Run tests
                        sh 'python -m unittest tests/test_task_manager.py'
                    }
                }
            }
            post {
                always {
                    // Clean up Docker image
                    sh "docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true"
                }
            }
        }
    }

    post {
        always {
            // Clean up workspace
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
} 