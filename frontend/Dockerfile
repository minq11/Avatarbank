# 프론트엔드 Dockerfile (Multi-stage build)

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# API 베이스 URL 은 Vite 가 빌드 시점에 번들에 굽는다. 런타임 환경변수로는 못 바꾼다.
# 운영은 프론트와 같은 오리진에 /api 로 백엔드를 붙이므로 "/api" 가 기본값이다.
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# 의존성 파일 복사 및 설치
COPY package*.json ./
RUN npm ci

# 소스 코드 복사 및 빌드
COPY . .
RUN npm run build

# Stage 2: Production
FROM nginx:1.27-alpine

# 빌드된 파일 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# 공통 스니펫 — nginx.conf / nginx.prod.conf 양쪽에서 include 한다.
COPY nginx.app.conf /etc/nginx/snippets/app.conf
COPY cloudflare-realip.conf /etc/nginx/snippets/cloudflare-realip.conf

# 기본 서버 설정(HTTP). 운영에서는 docker-compose.prod.yml 이
# nginx.prod.conf 를 이 경로 위에 마운트해 443 을 받는다.
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]
