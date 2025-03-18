FROM node:18
WORKDIR /frontend
COPY package.json .
RUN npm install
COPY ./frontend/src /frontend/dist
RUN npm run build
CMD ["npx", "serve", "-s", "dist", "-l", "8080"]
