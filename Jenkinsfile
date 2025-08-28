pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = "us-east-1"
        AWS_ACCOUNT_ID    = "992382545251"
        ECR_REPO          = "bar-calculator-app"
    }

    stages {
        stage('Checkout') {
    steps {
        git branch: "${env.BRANCH_NAME}",
            url: 'https://github.com/barbur2/calculator-app-CICD-test.git',
            credentialsId: 'GitHub-user'
    }
}

        stage('Build Docker Image') {
            agent {
                docker {
                    image 'docker:20.10.16'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    IMAGE_TAG = "pr-${env.CHANGE_ID ?: 'local'}-${env.BUILD_NUMBER}"
                    IMAGE_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}"
                    sh """
                      aws ecr get-login-password --region $AWS_DEFAULT_REGION \
                        | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com
                      docker build -t $IMAGE_URI .
                    """
                }
            }
        }

        stage('Run Tests') {
            agent {
                docker {
                    image 'python:3.9-slim'
                }
            }
            steps {
                sh 'pip install --no-cache-dir -r requirements.txt'
                sh 'pytest --junitxml=results.xml'
            }
            post {
                always {
                    junit 'results.xml'
                }
            }
        }

        stage('Push to ECR') {
            agent {
                docker {
                    image 'docker:20.10.16'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                sh "docker push $IMAGE_URI"
                echo "✅ Pushed image: $IMAGE_URI"
            }
        }
    }
}
