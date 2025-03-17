FROM node:18
WORKDIR /frontend
COPY package.json ./
RUN npm install
COPY public/ ./public/
COPY src/ ./src/
COPY vite.config.js ./
RUN npm run build
EXPOSE 8080
CMD ["npx", "serve", "-s", "dist", "-l", "8080"]