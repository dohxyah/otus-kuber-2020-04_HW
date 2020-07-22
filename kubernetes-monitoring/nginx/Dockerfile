FROM nginx:1.18.0-alpine
LABEL maintainer="Dmitrii Ponomarev <dimpon@gmail.com>"
COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./index.html /usr/share/nginx/html
EXPOSE 80