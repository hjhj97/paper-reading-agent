# 멀티 스테이지 빌드 사용
FROM node:20-alpine AS builder

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY package*.json ./
RUN npm ci

# 소스 코드 복사
COPY . .

# 디버깅: 파일 구조 확인
RUN echo "=== Checking directory structure ===" && \
    ls -la && \
    echo "=== Checking src directory ===" && \
    ls -la src/ && \
    echo "=== Checking src/lib directory ===" && \
    ls -la src/lib/ && \
    echo "=== Checking tsconfig.json ===" && \
    cat tsconfig.json

# public 디렉토리가 없으면 생성 (static 파일용)
RUN mkdir -p public

# 환경 변수 설정 (빌드 시)
ENV NEXT_TELEMETRY_DISABLED 1

# Next.js 빌드
RUN npm run build

# 프로덕션 이미지
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# public 디렉토리 복사 (builder 단계에서 생성됨)
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# standalone 빌드 결과물 복사
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

# 포트 노출
EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# 애플리케이션 실행
CMD ["node", "server.js"]

