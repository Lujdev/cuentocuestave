FROM node:20-alpine AS builder
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY package.json pnpm-workspace.yaml ./
COPY apps/web/package.json apps/web/
RUN pnpm install --frozen-lockfile
COPY apps/web apps/web
RUN pnpm --filter web build

FROM nginx:alpine AS runtime
COPY --from=builder /app/apps/web/dist /usr/share/nginx/html
COPY infra/docker/nginx-web.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
