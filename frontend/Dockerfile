FROM node:18
WORKDIR /frontend
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 9000
CMD ["npx", "serve", "-s", "dist", "-l", "9000"]