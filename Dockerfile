FROM ubuntu:latest

MAINTAINER Health Data Analytics

RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y python-pip python-dev build-essential python3-pip

ENV APP_HOME /api
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

COPY requirements.txt $APP_HOME

RUN pip3 install -r requirements.txt
RUN pip3 install -U pytest
RUN python3 -m spacy download en
RUN python3 -m spacy download en_core_web_md

COPY . .


# COPY . /api
# WORKDIR /api
ENTRYPOINT ["python3"]
CMD ["api.py"]
