FROM python:3.11.0b3-alpine3.16


RUN mkdir -p /opt/telinsta/
COPY main.py requirements.txt /opt/telinsta/

RUN pip install -r /opt/telinsta/requirements.txt

WORKDIR /opt/telinsta/

CMD ["python", "main.py"]