# FROM python:3.6

# ENV PYTHONUNBUFFERED 1

# COPY ./requirements.txt requirements.txt
# RUN pip install -r requirements.txt

# COPY . product_service
# WORKDIR /product_service

FROM python:3.8.6

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python","run.py" ]
