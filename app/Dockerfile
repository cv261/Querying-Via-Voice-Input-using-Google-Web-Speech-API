FROM python:3.7


ENV FLASK_DEBUG 1
WORKDIR /home/flask_app

ADD . .

RUN pip3 install -r requirements.txt

CMD ["python3", "app.py"]
