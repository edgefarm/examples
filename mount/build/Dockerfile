FROM python:3.9.4-slim-buster
WORKDIR /src
COPY . .
RUN pip3 install -r requirements.txt

CMD [ "python3", "-u", "./main.py" ]
