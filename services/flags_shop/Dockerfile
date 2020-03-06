FROM python:3.8

ADD requirements.txt /requirements.txt
RUN pip install uvloop gunicorn
RUN pip install -r requirements.txt

ADD app/main.py /main.py
ADD app/init_db.py /init_db.py
ADD start.sh /start.sh

ADD app /app
ADD config /config

RUN chmod +x /start.sh
CMD ["/start.sh"]
