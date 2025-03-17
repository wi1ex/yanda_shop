FROM node:18
WORKDIR /frontend

# Копируем зависимости
COPY package.json .
COPY package-lock.json .

# Установка зависимостей
RUN npm install

# Копируем ВСЕ файлы
COPY . .

# Сборка проекта
RUN npm run build

EXPOSE 8080
CMD ["npx", "serve", "-s", "dist", "-l", "8080"]