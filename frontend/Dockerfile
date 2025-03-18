FROM node:18 AS frontend-build
WORKDIR /frontend
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:latest AS frontend-runtime
WORKDIR /usr/share/nginx/html
COPY --from=frontend-build /frontend/dist/ .
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
