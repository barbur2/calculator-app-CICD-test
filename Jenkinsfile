pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = "us-east-1"
        AWS_ACCOUNT_ID     = "992382545251"
        ECR_REPO           = "bar-calculator-app"
        PROD_HOST          = "ec2-user@52.90.77.114"   
    }

    options {
        skipDefaultCheckout(true)
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${env.BRANCH_NAME}",
                    url: 'https://github.com/barbur2/calculator-app-CICD-test.git',
                    credentialsId: 'GitHub-user'
            }
        }

        stage('Build Image') {
            agent {
                docker {
                    image 'jenkins-docker-aws'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    if (env.CHANGE_ID) {
                        IMAGE_TAG = "pr-${env.CHANGE_ID}-${env.BUILD_NUMBER}"
                    } else if (env.BRANCH_NAME == 'main') {
                        IMAGE_TAG = "latest"
                    } else {
                        IMAGE_TAG = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
                    }
                    IMAGE_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}"

                    sh """
                      aws ecr get-login-password --region ${AWS_DEFAULT_REGION} \
                        | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com

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
                sh "docker run --rm ${IMAGE_URI} pytest"
            }
        }

        stage('Push to ECR') {
            when {
                anyOf {
                    expression { env.CHANGE_ID != null }  // PR builds
                    branch 'main'                        // main branch
                }
            }
            agent {
                docker {
                    image 'jenkins-docker-aws'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                sh "docker push ${IMAGE_URI}"
            }
        }

        stage('Deploy to Prod') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh """
                      ssh -o StrictHostKeyChecking=no ${PROD_HOST} \\
                        "docker login -u AWS -p \$(aws ecr get-login-password --region ${AWS_DEFAULT_REGION}) ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com && \\
                         docker pull ${IMAGE_URI} && \\
                         docker rm -f calculator || true && \\
                         docker run -d --name calculator -p 80:5000 ${IMAGE_URI}"
                    """
                }
            }
        }

        stage('Health Check') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh """
                      for i in {1..5}; do
                        if curl -s http://<PROD-EC2-IP>/health; then
                          echo "App is healthy"
                          exit 0
                        fi
                        echo "Health check failed, retrying..."
                        sleep 5
                      done
                      echo "App failed health check"
                      exit 1
                    """
                }
            }
        }
    }
}
