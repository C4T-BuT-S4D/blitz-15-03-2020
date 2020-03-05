FROM python:3.8

COPY requirements.txt /
WORKDIR /
RUN pip install gunicorn
RUN pip install -r requirements.txt

COPY app/main.py /
COPY app/init_db.py /
COPY start.sh /

ADD app /app
ADD config /config

RUN chmod +x start.sh
CMD ["./start.sh"]
