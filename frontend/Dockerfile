FROM node:18
WORKDIR /frontend
COPY package.json .
RUN npm install
COPY src /frontend/src
RUN npm run build
CMD ["npx", "serve", "-s", "dist", "-l", "8080"]