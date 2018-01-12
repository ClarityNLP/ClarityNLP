FROM ubuntu:latest
MAINTAINER Health Data Analytics
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /api
WORKDIR /api
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["api.py"]
