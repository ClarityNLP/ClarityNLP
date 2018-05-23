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
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a7', environments: '', image: 'build.hdap.gatech.edu/rtm-api:latest', ports: '', service: 'clarity/rtm-api', timeout: 60
                    rancher confirm: true, credentialId: 'rancher-server', endpoint: 'https://rancher.hdap.gatech.edu/v2-beta', environmentId: '1a7', environments: '', image: 'build.hdap.gatech.edu/rtm-client:latest', ports: '', service: 'clarity/rtm-client', timeout: 60
                }
            }
        }
    }
}
