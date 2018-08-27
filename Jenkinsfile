#!/usr/bin/env groovy
pipeline{
    agent any

    environment {
      GTRI_BUILD_HOST = credentials('gtri-build-host')
      GTRI_RANCHER_API_ENDPOINT = credentials('gtri-rancher-api-endpoint')
      GTRI_CLARITY_ENV_ID = credentials('gtri-clarity-env-id')
      EMORY_CLARITY_ENV_ID = credentials('emory-clarity-env-id')
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
                    docker.withRegistry("https://${GTRI_BUILD_HOST}"){
                        def nlpApiImage = docker.build("nlp-api:1.0", "-f ./nlp/Dockerfile.prod ./nlp")
                        nlpApiImage.push('latest')
                        def nlpSolrImage = docker.build("nlp-solr:1.0", "-f ./utilities/nlp-solr/Dockerfile.prod ./utilities/nlp-solr")
                        nlpSolrImage.push('latest')
                        def nlpMongoImage = docker.build("nlp-mongo:1.0", "-f ./utilities/nlp-mongo/Dockerfile.prod ./utilities/nlp-mongo")
                        nlpMongoImage.push('latest')
                        def nlpPostgresImage = docker.build("nlp-postgres:1.0", "-f ./utilities/nlp-postgres/Dockerfile.prod ./utilities/nlp-postgres")
                        nlpPostgresImage.push('latest')
                        def rtmApiImage = docker.build("rtm-api:1.0", "-f ./utilities/mapper-api/Dockerfile ./utilities/mapper-api")
                        rtmApiImage.push('latest')
                        def rtmClientImage = docker.build("rtm-client:1.0", "-f ./utilities/mapper-client/Dockerfile.prod ./utilities/mapper-client")
                        rtmClientImage.push('latest')
                        def ingestApiImage = docker.build("ingest-api:1.0", "-f ./utilities/ingest-api/Dockerfile ./utilities/ingest-api")
                        ingestApiImage.push('latest')
                        def ingestClientImage_EmoryStaging = docker.build("ingest-client-emory-staging:1.0", "-f ./utilities/ingest-client/Dockerfile.emory ./utilities/ingest-client")
                        ingestClientImage_EmoryStaging.push('latest')
                        def ingestClientImage_GtriProd = docker.build("ingest-client-gtri-production:1.0", "-f ./utilities/ingest-client/Dockerfile.gtri ./utilities/ingest-client")
                        ingestClientImage_GtriProd.push('latest')
                        def ingestMongoImage = docker.build("ingest-mongo:1.0", "-f ./utilities/ingest-mongo/Dockerfile.prod ./utilities/ingest-mongo")
                        ingestMongoImage.push('latest')
                        def resultsClientImage_EmoryStaging = docker.build("results-client-emory-staging:1.0", "-f ./utilities/results-client/Dockerfile.emory ./utilities/results-client")
                        resultsClientImage_EmoryStaging.push('latest')
                        def resultsClientImage_GtriProd = docker.build("results-client-gtri-production:1.0", "-f ./utilities/results-client/Dockerfile.gtri ./utilities/results-client")
                        resultsClientImage_GtriProd.push('latest')
                    }
                }
            }
        }

        //Define stage to notify rancher
        stage('Notify'){
            steps{
                //Write a script that notifies the Rancher API that the Docker Image for the application has been updated.
                script{
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/nlp-api:latest", ports: '', service: 'ClarityNLP/nlp-api', timeout: 2700
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: 'axiom/docker-luigi:2.7.1', ports: '', service: 'ClarityNLP/scheduler', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/nlp-solr:latest", ports: '', service: 'ClarityNLP/nlp-solr', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/nlp-mongo:latest", ports: '', service: 'ClarityNLP/nlp-mongo', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/ingest-mongo:latest", ports: '', service: 'ClarityNLP/ingest-mongo', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/nlp-postgres:latest", ports: '', service: 'ClarityNLP/nlp-postgres', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/rtm-api:latest", ports: '', service: 'ClarityNLP/mapper-api', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/ingest-api:latest", ports: '', service: 'ClarityNLP/ingest-api', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: 'postgres', ports: '', service: 'ClarityNLP/mapper-pg', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/rtm-client:latest", ports: '', service: 'ClarityNLP/mapper-client', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/ingest-client-gtri-production:latest", ports: '', service: 'ClarityNLP/ingest-client', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/results-client-gtri-production:latest", ports: '', service: 'ClarityNLP/results-client', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${GTRI_CLARITY_ENV_ID}", environments: '', image: 'redis:3.2.0', ports: '', service: 'ClarityNLP/redis', timeout: 600
                    // --- next env ---
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/nlp-api:latest", ports: '', service: 'ClarityNLP/nlp-api', timeout: 2700
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: 'axiom/docker-luigi:2.7.1', ports: '', service: 'ClarityNLP/scheduler', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/nlp-solr:latest", ports: '', service: 'ClarityNLP/nlp-solr', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/nlp-mongo:latest", ports: '', service: 'ClarityNLP/nlp-mongo', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/ingest-mongo:latest", ports: '', service: 'ClarityNLP/ingest-mongo', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/nlp-postgres:latest", ports: '', service: 'ClarityNLP/nlp-postgres', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/rtm-api:latest", ports: '', service: 'ClarityNLP/mapper-api', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/ingest-api:latest", ports: '', service: 'ClarityNLP/ingest-api', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: 'postgres', ports: '', service: 'ClarityNLP/mapper-pg', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/rtm-client:latest", ports: '', service: 'ClarityNLP/mapper-client', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/ingest-client-emory-staging:latest", ports: '', service: 'ClarityNLP/ingest-client', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: "${GTRI_BUILD_HOST}/results-client-emory-staging:latest", ports: '', service: 'ClarityNLP/results-client', timeout: 600
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: "${GTRI_RANCHER_API_ENDPOINT}", environmentId: "${EMORY_CLARITY_ENV_ID}", environments: '', image: 'redis:4.0.10', ports: '', service: 'ClarityNLP/redis', timeout: 600
                }
            }
        }
    }
}
