FROM node:20-alpine AS builder
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY package.json pnpm-workspace.yaml ./
COPY apps/admin/package.json apps/admin/
RUN pnpm install --frozen-lockfile
COPY apps/admin apps/admin
RUN pnpm --filter admin build

FROM nginx:alpine AS runtime
COPY --from=builder /app/apps/admin/dist /usr/share/nginx/html
COPY infra/docker/nginx-spa.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
