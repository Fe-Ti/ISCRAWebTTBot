FROM python:3-alpine

WORKDIR /usr/src/app

RUN apk add envsubst

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./bot ./
COPY iscrawebttbot_run.sh /usr/local/bin/

ENTRYPOINT [ "/usr/local/bin/iscrawebttbot_run.sh" ]
