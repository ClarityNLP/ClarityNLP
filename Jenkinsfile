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
                    }
                }
            }
        }

        //Define stage to notify rancher
        stage('Notify'){
            steps{
                //Write a script that notifies the Rancher API that the Docker Image for the application has been updated.
                script{
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'http://rancher.hdap.gatech.edu:8080/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/nlp-api:latest', ports: '', service: 'clarity/nlp-api', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'http://rancher.hdap.gatech.edu:8080/v2-beta', environmentId: '1a616', environments: '', image: 'axiom/docker-luigi:2.7.1', ports: '', service: 'clarity/scheduler', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'http://rancher.hdap.gatech.edu:8080/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/nlp-solr:latest', ports: '', service: 'clarity/nlp-solr', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'http://rancher.hdap.gatech.edu:8080/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/nlp-mongo:latest', ports: '', service: 'clarity/nlp-mongo', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'http://rancher.hdap.gatech.edu:8080/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/nlp-postgres:latest', ports: '', service: 'clarity/nlp-postgres', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'http://rancher.hdap.gatech.edu:8080/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/rtm-api:latest', ports: '', service: 'clarity/mapper-api', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'http://rancher.hdap.gatech.edu:8080/v2-beta', environmentId: '1a616', environments: '', image: 'postgres', ports: '', service: 'clarity/mapper-pg', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'http://rancher.hdap.gatech.edu:8080/v2-beta', environmentId: '1a616', environments: '', image: 'build.hdap.gatech.edu/rtm-client:latest', ports: '', service: 'clarity/mapper-client', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'http://rancher.hdap.gatech.edu:8080/v2-beta', environmentId: '1a616', environments: '', image: 'redis:3.2.0', ports: '', service: 'clarity/redis', timeout: 60

                }
            }
        }
    }
}
