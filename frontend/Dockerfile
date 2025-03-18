FROM node:18
WORKDIR /frontend
RUN npm cache clean --force
RUN rm -rf node_modules dist package-lock.json
COPY package.json .
RUN npm install
COPY . .
RUN npm run build
CMD ["npx", "serve", "-s", "dist", "-l", "8080"]