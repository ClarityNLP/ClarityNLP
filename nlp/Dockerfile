FROM python:3.6.8

MAINTAINER Health Data Analytics

RUN apt-get update && apt-get install -y \
    less \
    vim

ARG NLP_API_CONTAINER_PORT
ENV APP_HOME /api
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

VOLUME ["/tmp"]

COPY requirements.txt $APP_HOME
COPY install_models.py $APP_HOME
COPY config.py $APP_HOME

RUN CFLAGS="-Wno-narrowing" pip3 install -U cld2-cffi
RUN pip3 install -r requirements.txt
RUN pip3 install -U pytest
RUN python3 -m spacy download en_core_web_sm
RUN python3 install_models.py

COPY . .

CMD ["gunicorn", "api", "--config", "config.py", "-b", "$NLP_API_CONTAINER_PORT"]
