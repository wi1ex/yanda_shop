FROM node:18
WORKDIR /frontend
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 8080
CMD ["sh", "-c", "npm run build && npx serve -s dist -l 8080"]