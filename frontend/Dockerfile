FROM node:18
WORKDIR /frontend
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build  # Сборка проекта в папку dist
EXPOSE 8080
CMD ["npx", "serve", "-s", "dist", "-l", "8080"]