FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN mkdir /app/static && mkdir /app/media

COPY . /app

#CMD ["/app/entrypoint.sh"]

CMD ["celery", "-A", "netology_pd_diplom", "worker", "-D"]
CMD ["python", "manage.py", "collectstatic"]
CMD ["python", "manage.py", "makemigrations"]
CMD ["python", "manage.py", "migrate"]
CMD ["gunicorn", "netology_pd_diplom.wsgi:application", "-b", "0.0.0.0:8000"]

EXPOSE 8080
