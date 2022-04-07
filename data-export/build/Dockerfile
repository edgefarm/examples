FROM python:3.9.4-slim-buster AS builder
RUN apt-get update && apt-get install -y --no-install-recommends make gcc curl build-essential
WORKDIR /src
COPY . .
RUN pip3 install -r requirements.txt

FROM python:3.9.4-slim-buster

WORKDIR /src
COPY --from=builder /src /src
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

CMD [ "python3", "-u", "./main.py" ]
