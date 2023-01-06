FROM python

ENV DONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt update

ADD requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ADD . .

CMD while ! python3 manage.py sqlflush > /dev/null 2>&1 ; do sleep 1 ; done && \
    python3 manage.py makemigrations --noinput && \
    python3 manage.py migrate --noinput && \
    python3 manage.py collectstatic --noinput && \
    python3 manage.py createsuperuser --mobile_number 09130740148 --email vahidtwo@gmail.com --noinput; \
    gunicorn -b 0.0.0.0:8000 settings.wsgi