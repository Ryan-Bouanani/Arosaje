FROM instrumentisto/flutter:latest

WORKDIR /app

ENV FLUTTER_SUPPRESS_ANALYTICS=true
ENV CI=true

COPY . .

RUN flutter pub get

RUN flutter build web

RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

RUN cp -r build/web/* /var/www/html/

EXPOSE 5000

RUN sed -i 's/listen 80/listen 5000/g' /etc/nginx/sites-enabled/default

CMD ["nginx", "-g", "daemon off;"]