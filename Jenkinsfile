pipeline {
    agent none   // לא נריץ stages על bare-metal בכלל

    environment {
        AWS_DEFAULT_REGION = "us-east-1"
        AWS_ACCOUNT_ID     = "992382545251"
        ECR_REPO           = "bar-calculator-app"
        PROD_HOST          = "ec2-user@52.90.77.114"
    }

    stages {
        stage('Checkout') {
            agent {
                docker {
                    image 'jenkins-docker-aws'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
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
                    def IMAGE_TAG = (env.CHANGE_ID) ? "pr-${env.CHANGE_ID}-${env.BUILD_NUMBER}" :
                                   (env.BRANCH_NAME == 'main') ? "latest" :
                                   "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

                    def IMAGE_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}"

                    sh """
                      aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | \
                        docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com
                      docker build -t ${IMAGE_URI} .
                    """
                    env.IMAGE_URI = IMAGE_URI
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
                sh "docker run --rm -e PYTHONPATH=/app ${env.IMAGE_URI} pytest"
            }
        }

        stage('Push to ECR') {
            when {
                anyOf {
                    expression { env.CHANGE_ID != null }
                    branch 'main'
                }
            }
            agent {
                docker {
                    image 'jenkins-docker-aws'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                sh "docker push ${env.IMAGE_URI}"
            }
        }

        stage('Deploy to Prod') {
            when { branch 'main' }
            agent {
                docker {
                    image 'jenkins-docker-aws'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                sshagent(['prod-ec2-ssh']) {
                    sh """
                      ssh -o StrictHostKeyChecking=no ${PROD_HOST} \\
                        "aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com && \\
                         docker pull ${env.IMAGE_URI} && \\
                         docker rm -f calculator || true && \\
                         docker run -d --name calculator -p 80:5000 ${env.IMAGE_URI}"
                    """
                }
            }
        }

        stage('Health Check') {
            when { branch 'main' }
            agent {
                docker {
                    image 'jenkins-docker-aws'
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    sh """
                      for i in {1..5}; do
                        if curl -s http://${PROD_HOST.split('@')[-1]}/health; then
                          echo "✅ App is healthy"
                          exit 0
                        fi
                        echo "❌ Health check failed, retrying..."
                        sleep 5
                      done
                      exit 1
                    """
                }
            }
        }
    }
}
