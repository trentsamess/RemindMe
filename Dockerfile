FROM python:3
ENV PYTHONUNBUFFERED 1
RUN apt update && apt install -y netcat gettext
RUN mkdir -p /app && mkdir -p /app/storage && mkdir -p /app/logs
WORKDIR /app
ADD ./requirements.txt /app
RUN pip install --upgrade pip && pip3 install -r requirements.txt
ADD . /app


ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["prod"]
