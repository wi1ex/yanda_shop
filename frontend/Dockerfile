# Используем Node.js для сборки фронта
FROM node:18 AS build
WORKDIR /frontend

COPY package.json ./
RUN npm install

COPY index.html ./
COPY src/ ./src/
COPY vite.config.js ./
RUN npm run build

# Используем Nginx для раздачи статики
FROM nginx:latest
WORKDIR /usr/share/nginx/html
COPY --from=build /frontend/dist/ .
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
