FROM node:20 AS b
WORKDIR /w
COPY package.json . 
RUN npm i
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=b /w/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
