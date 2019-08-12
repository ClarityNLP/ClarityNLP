#!/usr/bin/env groovy
pipeline{
    agent any

    environment {
      GTRI_IMAGE_REGISTRY = credentials('gtri-image-registry')
      GTRI_RANCHER_API_ENDPOINT = credentials('gtri-rancher-api-endpoint')
      GTRI_HDAP_ENV_ID = credentials('hdap-aws-rancher-env')
      CLARITYNLP_DOCKERHUB_CREDS = 'claritynlp-dockerhub'
      idpImage = ''
      identityAndAccessProxyImage = ''
      nlpApiImage = ''
      nlpSolrImage = ''
      nlpMongoImage = ''
      nlpPostgresImage = ''
      ingestApiImage = ''
      ingestMongoImage = ''
      ingestClientImage = ''
      viewerClientImage = ''
      dashboardClientImage = ''
    }

    //Define stages for the build process
    stages{
        stage('Building images') {
          steps{
            script {
              idpImage = docker.build("claritynlp/idp:1.0", "./identity-provider")
              identityAndAccessProxyImage = docker.build("claritynlp/identity-and-access-proxy:1.0", "./identity-and-access-proxy")
              nlpApiImage = docker.build("claritynlp/nlp-api:1.0", "./nlp")
              nlpSolrImage = docker.build("claritynlp/nlp-solr:1.0", "./utilities/nlp-solr")
              nlpMongoImage = docker.build("claritynlp/nlp-mongo:1.0", "-f ./utilities/nlp-mongo/Dockerfile.prod ./utilities/nlp-mongo")
              nlpPostgresImage = docker.build("claritynlp/nlp-postgres:1.0", "./utilities/nlp-postgres")
              ingestApiImage = docker.build("claritynlp/ingest-api:1.0", "./utilities/ingest-api")
              ingestMongoImage = docker.build("claritynlp/ingest-mongo:1.0", "-f ./utilities/ingest-mongo/Dockerfile.prod ./utilities/ingest-mongo")
              ingestClientImage = docker.build("claritynlp/ingest-client:1.0", "-f ./utilities/ingest-client/Dockerfile.prod ./utilities/ingest-client")
              viewerClientImage = docker.build("claritynlp/viewer-client:1.0", "-f ./utilities/results-client/Dockerfile.prod ./utilities/results-client")
              dashboardClientImage = docker.build("claritynlp/dashboard-client:1.0", "-f ./utilities/dashboard-client/client/Dockerfile.prod ./utilities/dashboard-client/client")
            }
          }
        }
        stage('Push images to private registry'){
          steps{
            script{
              docker.withRegistry("https://${GTRI_IMAGE_REGISTRY}"){
                idpImage.push("latest")
                identityAndAccessProxyImage.push("latest")
                nlpApiImage.push("latest")
                nlpSolrImage.push("latest")
                nlpMongoImage.push("latest")
                nlpPostgresImage.push("latest")
                ingestApiImage.push("latest")
                ingestMongoImage.push("latest")
                ingestClientImage.push("latest")
                viewerClientImage.push("latest")
                dashboardClientImage.push("latest")
              }
            }
          }
        }
        stage('Push images to public registry'){
          steps{
            script{
              docker.withRegistry('', CLARITYNLP_DOCKERHUB_CREDS){
                idpImage.push("latest")
                identityAndAccessProxyImage.push("latest")
                nlpApiImage.push("latest")
                nlpSolrImage.push("latest")
                nlpMongoImage.push("latest")
                nlpPostgresImage.push("latest")
                ingestApiImage.push("latest")
                ingestMongoImage.push("latest")
                ingestClientImage.push("latest")
                viewerClientImage.push("latest")
                dashboardClientImage.push("latest")
              }
            }
          }
        }

        //Define stage to notify rancher
        stage('Notify orchestrator'){
            steps{
                //Write a script that notifies the Rancher API that the Docker Image for the application has been updated.
                script{
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "microsoft/mssql-server-linux", ports: '', service: 'ClarityNLP/mssql', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/idp:latest", ports: '', service: 'ClarityNLP/identity-provider', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/identity-and-access-proxy:latest", ports: '', service: 'ClarityNLP/identity-and-access-proxy', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/nlp-api:latest", ports: '', service: 'ClarityNLP/nlp-api', timeout: 2700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: 'axiom/docker-luigi:2.7.1', ports: '', service: 'ClarityNLP/scheduler', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/nlp-solr:latest", ports: '', service: 'ClarityNLP/nlp-solr', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/nlp-mongo:latest", ports: '', service: 'ClarityNLP/nlp-mongo', timeout: 5000
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/nlp-postgres:latest", ports: '', service: 'ClarityNLP/nlp-postgres', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/ingest-api:latest", ports: '', service: 'ClarityNLP/ingest-api', timeout: 700
                    // rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/ingest-mongo:latest", ports: '', service: 'ClarityNLP/ingest-mongo', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/ingest-client:latest", ports: '', service: 'ClarityNLP/ingest-client', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "redis:4.0.10", ports: '', service: 'ClarityNLP/redis', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/viewer-client:latest", ports: '', service: 'ClarityNLP/results-client', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/dashboard-client:latest", ports: '', service: 'ClarityNLP/dashboard-client', timeout: 700
                }
            }
        }
    }
}
