FROM node:18
WORKDIR /frontend
COPY package.json .
RUN npm install
COPY . .
RUN ls -l
RUN ls -l public
RUN npm run build
CMD ["npx", "serve", "-s", "dist", "-l", "8080"]
