FROM python:3.10-alpine
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
COPY ./resources resources
COPY ./app /app

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip3 install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh entrypoint.sh
RUN sed -i 's/\r$//g' entrypoint.sh
RUN chmod +x entrypoint.sh

# create folders for static files
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# create the app user
RUN addgroup -S app && adduser -S app -G app

# chown static files to the app user
RUN chown -R app:app /vol/
RUN chmod -R 755 /vol/web

WORKDIR /app

# change to the app user
USER app

ENTRYPOINT ["sh", "/entrypoint.sh"]