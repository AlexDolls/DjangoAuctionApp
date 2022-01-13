# pull official image
FROM nginx:1.21.5-alpine

# delete default config file
RUN rm /etc/nginx/conf.d/default.conf

# copy new config
COPY nginx.conf /etc/nginx/conf.d
