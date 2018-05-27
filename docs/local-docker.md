## Running ClarityNLP Locally

This is the best setup for getting started with ClarityNLP.


![Alt text](_static/docker-compose.png "Docker Compose Dev Diagram")

### Running Locally

1. Install [Docker for Mac](https://www.docker.com/docker-mac) or [Docker for Windows](https://www.docker.com/docker-windows)

2. Run `git clone https://github.com/ClarityNLP/ClarityNLP`

3. Initialize submodules `git submodule update --init --recursive`

4. Add .env file, use .env.example as a start:
```
    cd ClarityNLP
   touch .env
   cat .env.example >> .env
```


### Updating to download latest changes
From the command line, run:
```
git pull
git submodule update --recursive
```