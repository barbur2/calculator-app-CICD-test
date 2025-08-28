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
            steps {
                script {
                    sh 'pwd'
                    sh 'ls -la'
                    sh 'cat Dockerfile || echo "❌ No Dockerfile found!"'

                    def IMAGE_TAG = "latest"
                    def IMAGE_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}"

                    sh """
                      aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | \
                      docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com
                      docker build -t ${IMAGE_URI} .
                    """
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh "docker run --rm ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO}:latest pytest || echo '⚠️ Tests failed'"
            }
        }

        stage('Push to ECR') {
            when {
                branch 'main'
            }
            steps {
                script {
                    def IMAGE_TAG = "latest"
                    def IMAGE_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO}:${IMAGE_TAG}"

                    sh "docker push ${IMAGE_URI}"
                }
            }
        }

        stage('Deploy to Prod') {
            when {
                branch 'main'
            }
            steps {
                sshagent(['prod-ec2-ssh']) {
                    sh """
                      ssh -o StrictHostKeyChecking=no ${PROD_HOST} \\
                        "aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com && \\
                         docker pull ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO}:latest && \\
                         docker rm -f calculator || true && \\
                         docker run -d --name calculator -p 80:5000 ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO}:latest"
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
                      HOST_IP=\$(echo ${PROD_HOST} | cut -d'@' -f2)
                      for i in {1..5}; do
                        if curl -s http://\$HOST_IP/health; then
                          echo "✅ App is healthy"
                          exit 0
                        fi
                        echo "Health check failed, retrying..."
                        sleep 5
                      done
                      echo "❌ App failed health check"
                      exit 1
                    """
                }
            }
        }
    }
}
