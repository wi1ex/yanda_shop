FROM nginx:latest
WORKDIR /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=frontend-build /frontend/dist/ .
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
