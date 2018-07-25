#!/usr/bin/env groovy
pipeline{
    agent any

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
                    docker.withRegistry('https://build.hdap.gatech.edu'){
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
                        def ingestClientImage = docker.build("ingest-client:1.0", "-f ./utilities/ingest-client/Dockerfile.prod ./utilities/ingest-client")
                        ingestClientImage.push('latest')
                        def ingestMongoImage = docker.build("ingest-mongo:1.0", "-f ./utilities/ingest-mongo/Dockerfile.prod ./utilities/ingest-mongo")
                        ingestClientImage.push('latest')
                    }
                }
            }
        }

        //Define stage to notify rancher
        stage('Notify'){
            steps{
                //Write a script that notifies the Rancher API that the Docker Image for the application has been updated.
                script{
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/nlp-api:latest', ports: '', service: 'ClarityNLP/nlp-api', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a616', environments: '', image: 'axiom/docker-luigi:2.7.1', ports: '', service: 'ClarityNLP/scheduler', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/nlp-solr:latest', ports: '', service: 'ClarityNLP/nlp-solr', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/nlp-mongo:latest', ports: '', service: 'ClarityNLP/nlp-mongo', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/ingest-mongo:latest', ports: '', service: 'ClarityNLP/ingest-mongo', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/nlp-postgres:latest', ports: '', service: 'ClarityNLP/nlp-postgres', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/rtm-api:latest', ports: '', service: 'ClarityNLP/mapper-api', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/ingest-api:latest', ports: '', service: 'ClarityNLP/ingest-api', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a616', environments: '', image: 'postgres', ports: '', service: 'ClarityNLP/mapper-pg', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/rtm-client:latest', ports: '', service: 'ClarityNLP/mapper-client', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/ingest-client:latest', ports: '', service: 'ClarityNLP/ingest-client', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a616', environments: '', image: 'redis:3.2.0', ports: '', service: 'ClarityNLP/redis', timeout: 60

                }
            }
        }
    }
}
