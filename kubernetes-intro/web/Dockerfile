FROM nginx:1.18.0-alpine

LABEL maintainer="Dmitrii Ponomarev <dimpon@gmail.com>"

RUN apk add --no-cache shadow \
    && usermod -u 1001 nginx \
    && groupmod -g 1001 nginx

RUN  mkdir /app

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./index.html /app

EXPOSE 8000
USER 1001