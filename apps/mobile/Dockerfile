FROM node:20-slim AS builder

WORKDIR /app

# 复制根目录的依赖文件
COPY package*.json ./
COPY apps/mobile/package*.json ./apps/mobile/

# 安装依赖
RUN npm install
RUN cd apps/mobile && npm install

# 复制代码
COPY . .

# 构建
WORKDIR /app/apps/mobile
RUN npx vite build

# 生产镜像
FROM nginx:alpine
COPY --from=builder /app/apps/mobile/dist /usr/share/nginx/html
COPY apps/mobile/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

