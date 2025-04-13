pipeline {
    agent any

    tools {
        git 'Git'
        python 'Python3'
    }

    environment {
        PROJECT_NAME = 'titans-manager'
        DJANGO_SETTINGS_MODULE = 'TitansManager.settings'
        REGISTRY = "wackopsprodacr.azurecr.io"
        IMAGE_NAME = "titans-manager"
        AKS_CLUSTER_NAME = "wackops-prod-cluster"
        AKS_RESOURCE_GROUP = "wackops-prod"
        AKS_NAMESPACE = "wackops"
        K8S_MANIFEST_DIR = "kubernetes"
    }

    options {
        timeout(time: 60, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    triggers {
        githubPush()
    }

    parameters {
        booleanParam(name: 'SKIP_TESTS', defaultValue: false, description: 'Skip running tests')
        booleanParam(name: 'DEPLOY_TO_AKS', defaultValue: false, description: 'Deploy to AKS after build')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    def pythonHome = tool name: 'Python3', type: 'python'
                    env.PYTHON_HOME = pythonHome
                    env.PATH = "${pythonHome}/bin:${env.PATH}"

                    sh '''
                        python --version
                        pip --version
                    '''
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            when {
                expression { return !params.SKIP_TESTS }
            }
            steps {
                sh '''
                    . venv/bin/activate
                    pytest --cov=core --cov-report=xml
                '''
            }
            post {
                always {
                    junit(testResults: '**/junit.xml', allowEmptyResults: true)
                    archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true
                }
            }
        }

        stage('Static Code Analysis') {
            steps {
                sh '''
                    . venv/bin/activate
                    flake8 core
                '''
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(credentialsId: env.AZURE_CREDENTIALS_ID,
                                     passwordVariable: 'ACR_PASSWORD',
                                     usernameVariable: 'ACR_USERNAME')
                ]) {
                    sh """
                        echo \${ACR_PASSWORD} | docker login ${REGISTRY} -u \${ACR_USERNAME} --password-stdin
                        docker build -t ${REGISTRY}/${IMAGE_NAME}:${env.BUILD_NUMBER} .
                        docker push ${REGISTRY}/${IMAGE_NAME}:${env.BUILD_NUMBER}
                        docker logout ${REGISTRY}
                    """
                }
            }
        }

        stage('Deploy to AKS') {
            when {
                expression { return params.DEPLOY_TO_AKS }
            }
            steps {
                withCredentials([
                    usernamePassword(credentialsId: env.AZURE_CREDENTIALS_ID,
                                     passwordVariable: 'AZURE_SP_PASSWORD',
                                     usernameVariable: 'AZURE_SP_ID'),
                    string(credentialsId: 'azure-tenant-id', variable: 'AZURE_TENANT_ID')
                ]) {
                    sh """
                        az login --service-principal \\
                            --username "\${AZURE_SP_ID}" \\
                            --password="\${AZURE_SP_PASSWORD}" \\
                            --tenant "\${AZURE_TENANT_ID}"

                        az aks get-credentials --resource-group ${AKS_RESOURCE_GROUP} --name ${AKS_CLUSTER_NAME}

                        kubectl get namespace ${AKS_NAMESPACE} || kubectl create namespace ${AKS_NAMESPACE}

                        sed -i "s|image: .*|image: ${REGISTRY}/${IMAGE_NAME}:${env.BUILD_NUMBER}|g" ${K8S_MANIFEST_DIR}/deployment.yaml

                        kubectl apply -f ${K8S_MANIFEST_DIR}/ -n ${AKS_NAMESPACE}

                        kubectl rollout status deployment/${IMAGE_NAME} -n ${AKS_NAMESPACE}
                    """
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout ${REGISTRY}'
            cleanWs()
        }
        success {
            echo "Build, Docker image push, and optional deployment completed successfully!"
        }
        failure {
            echo "Build, Docker image push, or deployment failed. See logs for details."
        }
    }
}
