pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = "us-east-1"
        AWS_ACCOUNT_ID     = "992382545251"
        ECR_REPO           = "bar-calculator-app"
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
                    image 'jenkins-docker-aws'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    def IMAGE_TAG = "build-${env.BUILD_NUMBER}"
                    def IMAGE_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}"

                    sh """
                      echo "Logging in to AWS ECR..."
                      aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | \
                        docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com

                      echo "Building Docker image: ${IMAGE_URI}"
                      docker build -t ${IMAGE_URI} .
                    """
                }
            }
        }

        stage('Run Tests') {
            agent {
                docker {
                    image 'jenkins-docker-aws'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                sh """
                  echo "Running tests..."
                  docker run --rm ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO}:build-${env.BUILD_NUMBER} pytest || true
                """
            }
        }

        stage('Push to ECR') {
            agent {
                docker {
                    image 'jenkins-docker-aws'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    def IMAGE_TAG = "build-${env.BUILD_NUMBER}"
                    def IMAGE_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}"

                    sh """
                      echo "Pushing image to ECR..."
                      docker push ${IMAGE_URI}
                    """
                }
            }
        }
    }
}
