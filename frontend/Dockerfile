FROM node:18 AS build
WORKDIR /frontend
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18
WORKDIR /frontend
COPY --from=build /frontend/dist ./dist
RUN npm install -g serve
CMD ["npx", "serve", "-s", "dist", "-l", "8080"]