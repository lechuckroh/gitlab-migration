FROM python:3.8

RUN mkdir -p /app
COPY migrate.py /app
COPY gitlab-migration.cfg /app
COPY requirements.txt /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD python migrate.py
