FROM node:18 AS build
WORKDIR /frontend
COPY package.json ./
RUN npm install
COPY . ./
RUN npm run build
FROM nginx:latest
WORKDIR /usr/share/nginx/html
COPY --from=build /frontend/dist/ .
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
