FROM ubuntu:latest
MAINTAINER Health Data Analytics
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y python-pip python-dev build-essential python3-pip
COPY . /api
WORKDIR /api
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["api.py"]
