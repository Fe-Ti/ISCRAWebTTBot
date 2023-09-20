FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY ./bot ./
COPY config.json ./

RUN pip install --no-cache-dir -r requirements.txt

COPY iscrawebttbot_run.sh /usr/local/bin/

ENTRYPOINT [ "/usr/local/bin/iscrawebttbot_run.sh" ]
