FROM python:3.7-slim

RUN mkdir /code
WORKDIR /code

# for correct work of postgres inside Docker
RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

COPY ./run_app.sh /run_app.sh
COPY ./run_tests.sh /run_tests.sh
RUN chmod +x /run_app.sh
RUN chmod +x /run_tests.sh
