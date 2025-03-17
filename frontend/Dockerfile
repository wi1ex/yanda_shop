FROM node:18
WORKDIR /frontend

# Копируем зависимости
COPY package.json .
RUN npm install

# Копируем исходники
COPY public/ ./public/
COPY src/ ./src/
COPY vite.config.js ./

# Сборка
RUN npm run build

EXPOSE 8080
CMD ["npx", "serve", "-s", "dist", "-l", "8080"]