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
      ingestClientImageVhost = ''
      viewerClientImageVhost = ''
      dashboardClientImageVhost = ''
    }

    //Define stages for the build process
    stages{
        stage('Building images') {
          steps{
            script {
              idpImage = docker.build("claritynlp/identity-provider:1.0", "./identity-provider")
              identityAndAccessProxyImage = docker.build("claritynlp/identity-and-access-proxy:1.0", "./identity-and-access-proxy")
              nlpApiImage = docker.build("claritynlp/nlp-api:1.0", "./nlp")
              nlpSolrImage = docker.build("claritynlp/nlp-solr:1.0", "./utilities/nlp-solr")
              nlpMongoImage = docker.build("claritynlp/nlp-mongo:1.0", "-f ./utilities/nlp-mongo/Dockerfile.prod ./utilities/nlp-mongo")
              nlpPostgresImage = docker.build("claritynlp/nlp-postgres:1.0", "./utilities/nlp-postgres")
              ingestApiImage = docker.build("claritynlp/ingest-api:1.0", "./utilities/ingest-api")
              ingestMongoImage = docker.build("claritynlp/ingest-mongo:1.0", "-f ./utilities/ingest-mongo/Dockerfile.prod ./utilities/ingest-mongo")
              frontCtrlImage = docker.build("claritynlp/front-ctrl:1.0", "./front-ctrl")
              ingestClientImage = docker.build("claritynlp/ingest-client:1.0", "--build-arg PUBLIC_URL=/ingest -f ./utilities/ingest-client/Dockerfile.prod ./utilities/ingest-client")
              viewerClientImage = docker.build("claritynlp/viewer-client:1.0", "--build-arg PUBLIC_URL=/results -f ./utilities/results-client/Dockerfile.prod ./utilities/results-client")
              dashboardClientImage = docker.build("claritynlp/dashboard-client:1.0", "--build-arg PUBLIC_URL=/dashboard -f ./utilities/dashboard-client/client/Dockerfile.prod ./utilities/dashboard-client/client")
              ingestClientImageVhost = docker.build("claritynlp/ingest-client:1.0-vhost", "--build-arg PUBLIC_URL=/ -f ./utilities/ingest-client/Dockerfile.prod ./utilities/ingest-client")
              viewerClientImageVhost = docker.build("claritynlp/viewer-client:1.0-vhost", "--build-arg PUBLIC_URL=/ -f ./utilities/results-client/Dockerfile.prod ./utilities/results-client")
              dashboardClientImageVhost = docker.build("claritynlp/dashboard-client:1.0-vhost", "--build-arg PUBLIC_URL=/ -f ./utilities/dashboard-client/client/Dockerfile.prod ./utilities/dashboard-client/client")
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
                frontCtrlImage.push("latest")
                ingestClientImage.push("latest")
                viewerClientImage.push("latest")
                dashboardClientImage.push("latest")
                ingestClientImageVhost.push("latest-vhost")
                viewerClientImageVhost.push("latest-vhost")
                dashboardClientImageVhost.push("latest-vhost")
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
                frontCtrlImage.push("latest")
                ingestClientImage.push("latest")
                viewerClientImage.push("latest")
                dashboardClientImage.push("latest")
                ingestClientImageVhost.push("latest-vhost")
                viewerClientImageVhost.push("latest-vhost")
                dashboardClientImageVhost.push("latest-vhost")
              }
            }
          }
        }

        //Define stage to notify rancher
        stage('Notify orchestrator (Rancher v1)'){
            steps{
                //Write a script that notifies the Rancher API that the Docker Image for the application has been updated.
                script{
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "microsoft/mssql-server-linux", ports: '', service: 'ClarityNLP/mssql', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/claritynlp/identity-provider:latest", ports: '', service: 'ClarityNLP/identity-provider', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/claritynlp/identity-and-access-proxy:latest", ports: '', service: 'ClarityNLP/identity-and-access-proxy', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/claritynlp/nlp-api:latest", ports: '', service: 'ClarityNLP/nlp-api', timeout: 2700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: 'axiom/docker-luigi:2.7.1', ports: '', service: 'ClarityNLP/scheduler', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/claritynlp/nlp-solr:latest", ports: '', service: 'ClarityNLP/nlp-solr', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/claritynlp/nlp-mongo:latest", ports: '', service: 'ClarityNLP/nlp-mongo', timeout: 5000
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/claritynlp/nlp-postgres:latest", ports: '', service: 'ClarityNLP/nlp-postgres', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/claritynlp/ingest-api:latest", ports: '', service: 'ClarityNLP/ingest-api', timeout: 700
                    // rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/claritynlp/ingest-mongo:latest", ports: '', service: 'ClarityNLP/ingest-mongo', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/claritynlp/ingest-client:latest-vhost", ports: '', service: 'ClarityNLP/ingest-client', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "redis:4.0.10", ports: '', service: 'ClarityNLP/redis', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/claritynlp/viewer-client:latest-vhost", ports: '', service: 'ClarityNLP/results-client', timeout: 700
                    rancher confirm: true, credentialId: 'gt-rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_HDAP_ENV_ID}", environments: '', image: "${GTRI_IMAGE_REGISTRY}/claritynlp/dashboard-client:latest-vhost", ports: '', service: 'ClarityNLP/dashboard-client', timeout: 700
                }
            }
        }
    }
}
