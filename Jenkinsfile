pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'task-manager-test'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }

    stages {
        // stage('Checkout') {
        //     steps {
        //         cleanWs()
        //         checkout scm
        //     }
        // }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    try {
                        // Run the Docker container and display logs in real-time
                        sh "docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    } catch (err) {
                        currentBuild.result = 'FAILURE'
                        error("Tests failed: ${err}")
                    }
                }
            }
        }
    }

    post {
        always {
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
