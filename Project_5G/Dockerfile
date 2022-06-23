FROM alpine:latest

LABEL maintainer="Armandres"

#COPY ./requirements.txt /requirements.txt ##Initially not needed
COPY ./5G_project /5G_project

WORKDIR /5G_project
EXPOSE 8080

#Maybe not needed.
RUN apk add nginx

RUN mkdir -p /run/nginx

RUN touch /run/nginx/nginx.pid

RUN adduser -D -g 'www' www

RUN mkdir /www

RUN chown -R www:www /var/lib/nginx

RUN chown -R www:www /www

RUN apk add sudo

RUN apk update

RUN apk add -U wireguard-tools

RUN umask 077

CMD apk add -U wireguard-tools

ENV PATH="/py/bin:$PATH"