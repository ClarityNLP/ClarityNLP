FROM python:3.6.8

MAINTAINER Health Data Analytics

ENV APP_HOME /api
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

COPY requirements.txt $APP_HOME
COPY install_models.py $APP_HOME

RUN CFLAGS="-Wno-narrowing" pip3 install -U cld2-cffi
RUN pip3 install -r requirements.txt
RUN pip3 install -U pytest
RUN python3 -m spacy download en
RUN python3 -m spacy download en_core_web_md
RUN python3 install_models.py

COPY . .

ENTRYPOINT ["python3"]
CMD ["api.py"]
