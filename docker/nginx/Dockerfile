FROM nginx


RUN service nginx stop

RUN rm /etc/nginx/conf.d/default.conf

RUN mkdir /etc/nginx/certs/

COPY self_signed.crt /etc/nginx/certs/self_signed.crt
COPY self_signed.key /etc/nginx/certs/self_signed.key

COPY nginx.local.conf /etc/nginx/conf.d

#RUN service nginx reload
# RUN service nginx start