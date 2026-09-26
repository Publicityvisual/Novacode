FROM node:20-alpine AS base

WORKDIR /app

COPY package.json ./
RUN npm install --production

COPY server.js ./
COPY artifacts ./artifacts

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000
ENV ARTIFACTS_DIR=/app/artifacts
ENV BASE_URL=https://novacode.dev/updates

CMD ["node", "server.js"]
