## Docker Compose Clarity NLP Application

### Docker Compose (Development) Architecture Diagram

![Alt text](/docker-compose.png?raw=true "Docker Compose Dev Diagram")

### Production Deployment

1. Install both Docker and Docker-Compose on your machine. Go [here](https://docs.docker.com/install/#server) to install Docker, <br/>
find your OS and follow instructions. Go [here](https://docs.docker.com/compose/install/) to install Docker Compose.

2. Run `git clone [this-project-url] [folder-name]`

3. Initialize submodules `git submodule update --init --recursive`

4. Add .env file, use .env.example as a start:
```cd [folder-name]
   touch .env
   cat .env.example >> .env
```

5. Build images and run containers `docker-compose -f docker-compose.prod.yml up --build -d`

### Running Locally

1. Install [Docker for Mac](https://www.docker.com/docker-mac) or [Docker for Windows](https://www.docker.com/docker-windows)

2. Run `git clone [this-project-url] [folder-name]`

3. Initialize submodules `git submodule update --init --recursive`

4. Add .env file, use .env.example as a start:
```cd [folder-name]
   touch .env
   cat .env.example >> .env
```

5. Build images and run containers `docker-compose up --build`

Now you can run `docker ps` to confirm the project's containers are running.

### Updating to download latest changes
From the command line, run:
```
git pull
git submodule update --recursive
```
