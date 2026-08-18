# Build multi-stage do frontend do PreDis (Vue 3 + Vite), servido por Nginx.
# Contexto de build esperado: frontend/ — ver docker-compose.yml.

FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# VITE_API_URL permite apontar para um backend diferente de
# http://127.0.0.1:8000 (padrão usado quando a variável não é definida —
# ver frontend/src/components/Dashboard.vue).
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
