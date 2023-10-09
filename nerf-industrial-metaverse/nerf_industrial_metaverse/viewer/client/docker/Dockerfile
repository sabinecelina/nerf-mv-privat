FROM docker.deagxartifactory.sickcn.net/nginx:1.23.3

ENV NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx

ENV CONTENT_SECURITY_POLICY="add_header Content-Security-Policy \"frame-ancestors *.sickcn.net *.sick.com;\";"

COPY ./build/ /usr/share/nginx/html/

COPY ./docker/nginx.conf.template /etc/nginx/templates/

RUN find /usr/share/nginx/html/ -type f -regex ".*\.\(html\|js\|css\)" -exec sh -c "gzip < {} > {}.gz" \;
