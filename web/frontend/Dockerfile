FROM node:20-alpine AS base

WORKDIR /app

COPY package.json package-lock.json* yarn.lock* pnpm-lock.yaml* ./

RUN if [ -f package-lock.json ]; then npm install; \
    elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm install --frozen-lockfile; \
    else npm install; fi

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]

