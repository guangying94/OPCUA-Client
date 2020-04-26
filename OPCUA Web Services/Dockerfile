FROM ubuntu:18.04

LABEL maintainer="gutee"

RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip nginx unixodbc-dev curl libssl1.0.0 libssl-dev

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 80

ENTRYPOINT ["/usr/bin/python3"]

CMD ["opc-client.py"]