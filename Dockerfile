FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libgtk2.0-dev

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app/

CMD ["python3", "api.py"]