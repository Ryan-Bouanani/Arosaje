FROM instrumentisto/flutter:latest

WORKDIR /app

ENV FLUTTER_SUPPRESS_ANALYTICS=true
ENV CI=true

COPY . .

RUN flutter pub get

RUN flutter build web

RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

RUN cp -r build/web/* /var/www/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]