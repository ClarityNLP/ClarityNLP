#!/usr/bin/env groovy
pipeline{
    agent any

    environment {
      GTRI_IMAGE_REGISTRY = credentials('gtri-image-registry')
      GTRI_RANCHER_API_ENDPOINT = credentials('gtri-rancher-api-endpoint')
      GTRI_CLARITY_ENV_ID = credentials('gtri-clarity-env-id')
    }

    //Define stages for the build process
    stages{
        stage('Deploy'){
            steps{
                //The Jenkins Declarative Pipeline does not provide functionality to deploy to a private
                //Docker registry. In order to deploy to the HDAP Docker registry we must write a custom Groovy
                //script using the Jenkins Scripting Pipeline. This is done by placing Groovy code with in a "script"
                //element. The script below registers the HDAP Docker registry with the Docker instance used by
                //the Jenkins Pipeline, builds a Docker image using the project Dockerfile, and pushes it to the registry
                //as the latest version.
                script{
                    docker.withRegistry("https://${GTRI_IMAGE_REGISTRY}"){
                        def idpImage = docker.build("idp:1.0", "./identity-provider")
                        idpImage.push("latest")
                        def identityAndAccessProxyImage = docker.build("identity-and-access-proxy:1.0", "./identity-and-access-proxy")
                        identityAndAccessProxyImage.push("latest")
                        def nlpApiImage = docker.builid("nlp-api:1.0", "./nlp")
                        nlpApiImage.push("latest")
                        // def schedulerImage = docker.build
                        def nlpSolrImage = docker.build("nlp-solr:1.0", "./utilities/nlp-solr")
                        nlpSolrImage.push("latest")
                        def nlpMongoImage = docker.build("nlp-mongo:1.0", "-f ./utilities/nlp-mongo/Dockerfile.prod ./utilities/nlp-mongo")
                        nlpMongoImage.push("latest")
                        def nlpPostgresImage = docker.build("nlp-postgres:1.0", "./utilities/nlp-postgres")
                        nlpPostgresImage.push("latest")
                        def ingestApiImage = docker.build("ingest-api:1.0", "-f ./utilities/ingest-api/Dockerfile.prod ./utilities/ingest-api")
                        ingestApiImage.push("latest")
                        def ingestMongoImage = docker.build("ingest-mongo:1.0", "-f ./utilities/ingest-mongo/Dockerfile.prod ./utilities/ingest-mongo")
                        ingestMongoImage.push("latest")
                        def ingestClientImage = docker.build("ingest-client:1.0", "-f ./utilities/ingest-client/Dockerfile.prod ./utilities/ingest-client")
                        ingestClientImage.push("latest")
                        def viewerClientImage = docker.build("viewer-client:1.0", "-f ./utilities/results-client/Dockerfile.prod ./utilities/results-client")
                        viewerClientImage.push("latest")
                        def dashboardClientImage = docker.build("dashboard-client:1.0", "-f ./utilities/dashboard-client/client/Dockerfile.prod ./utilities/dashboard-client/client")
                        dashboardClientImage.push("latest")
                        def nginxProxyImage = docker.build("nginx-proxy:1.0", "./nginx-proxy")
                        nginxProxyImage.push("latest")
                    }
                }
            }
        }

        //Define stage to notify rancher
        stage('Notify'){
            steps{
                //Write a script that notifies the Rancher API that the Docker Image for the application has been updated.
                script{
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "microsoft/mssql-server-linux", ports: '', service: 'ClarityNLP-Internal-Stable/mssql', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/idp:latest", ports: '', service: 'ClarityNLP-Internal-Stable/identity-provider', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/identity-and-access-proxy:latest", ports: '', service: 'ClarityNLP-Internal-Stable/identity-and-access-proxy', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/nlp-api:latest", ports: '', service: 'ClarityNLP-Internal-Stable/nlp-api', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: 'axiom/docker-luigi:2.7.1', ports: '', service: 'ClarityNLP-Internal-Stable/scheduler', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/nlp-solr:latest", ports: '', service: 'ClarityNLP-Internal-Stable/nlp-solr', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/nlp-mongo:latest", ports: '', service: 'ClarityNLP-Internal-Stable/nlp-mongo', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/nlp-postgres:latest", ports: '', service: 'ClarityNLP-Internal-Stable/nlp-postgres', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/ingest-api:latest", ports: '', service: 'ClarityNLP-Internal-Stable/ingest-api', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/ingest-mongo:latest", ports: '', service: 'ClarityNLP-Internal-Stable/ingest-mongo', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/ingest-client:latest", ports: '', service: 'ClarityNLP-Internal-Stable/ingest-client', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "redis:4.0.10", ports: '', service: 'ClarityNLP-Internal-Stable/redis', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/viewer-client:latest", ports: '', service: 'ClarityNLP-Internal-Stable/results-client', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/dashboard-client:latest", ports: '', service: 'ClarityNLP-Internal-Stable/dashboard-client', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/nginx-proxy:latest", ports: '', service: 'ClarityNLP-Internal-Stable/nginx-proxy', timeout: 420
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "jrcs/letsencrypt-nginx-proxy-companion", ports: '', service: 'ClarityNLP-Internal-Stable/letsencrypt', timeout: 420
                }
            }
        }
    }
}
