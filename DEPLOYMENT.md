# 🐳 Docker 배포 가이드

## 📋 사전 준비

### 필수 요구사항
- Docker 설치 (20.10 이상)
- Docker Compose 설치 (v2.0 이상)
- OpenAI API 키
- Pinecone API 키 및 인덱스

## 🚀 로컬에서 Docker로 실행

### 1. 환경 변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집하여 실제 API 키 입력
nano .env
```

`.env` 파일 예시:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
PINECONE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=paper-reading-agent
```

### 2. Docker 이미지 빌드 및 실행

```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 특정 서비스만 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. 접속

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Backend Health Check**: http://localhost:8000/docs

### 4. 중지 및 삭제

```bash
# 컨테이너 중지
docker-compose down

# 컨테이너 및 볼륨 삭제 (데이터 완전 삭제)
docker-compose down -v

# 이미지까지 모두 삭제
docker-compose down --rmi all -v
```

## ☁️ AWS 배포 방법

### Option 1: EC2 + Docker Compose (추천 - 가장 간단)

#### 1.1 EC2 인스턴스 생성
- **인스턴스 타입**: t3.medium 이상 (2 vCPU, 4GB RAM)
- **OS**: Amazon Linux 2023 또는 Ubuntu 22.04
- **보안 그룹**: 
  - 포트 22 (SSH)
  - 포트 80 (HTTP)
  - 포트 443 (HTTPS)
  - 포트 3000 (Frontend - 임시)
  - 포트 8000 (Backend - 임시)

#### 1.2 Docker 설치

**Amazon Linux 2023:**
```bash
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 재로그인 필요
exit
```

**Ubuntu 22.04:**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
exit
```

#### 1.3 프로젝트 배포

```bash
# Git 클론 (또는 파일 직접 업로드)
git clone https://github.com/your-username/paper-reading-agent.git
cd paper-reading-agent

# 환경 변수 설정
nano .env
# API 키들 입력

# 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f
```

#### 1.4 Nginx 리버스 프록시 설정 (선택사항)

```bash
sudo yum install nginx -y  # Amazon Linux
# 또는
sudo apt-get install nginx -y  # Ubuntu

sudo nano /etc/nginx/conf.d/paper-agent.conf
```

`/etc/nginx/conf.d/paper-agent.conf`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: AWS Lightsail Container Service (저렴)

```bash
# Lightsail CLI 설치
aws lightsail create-container-service \
  --service-name paper-agent \
  --power medium \
  --scale 1

# 컨테이너 배포
aws lightsail push-container-image \
  --service-name paper-agent \
  --label backend \
  --image paper-agent-backend:latest
```

### Option 3: AWS ECS (프로덕션 환경)

1. **ECR에 이미지 푸시**
```bash
# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 태그 및 푸시
docker tag paper-agent-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/paper-agent-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/paper-agent-backend:latest

docker tag paper-agent-frontend:latest YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/paper-agent-frontend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/paper-agent-frontend:latest
```

2. **ECS Task Definition 생성** (AWS Console에서)
3. **ALB (Application Load Balancer) 설정**
4. **ECS Service 생성**

## ⚠️ 세션 기반 주의사항

### 현재 제한사항
- **메모리 세션**: 컨테이너 재시작 시 세션 데이터 손실
- **단일 컨테이너**: 스케일링 불가 (여러 컨테이너로 확장 시 세션 공유 안 됨)
- **PDF 저장**: 볼륨 마운트로 영구 저장 (docker-compose.yml에 이미 설정됨)

### 프로덕션 개선 방안

#### Redis 세션 저장소 추가

`docker-compose.yml`에 Redis 추가:
```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: paper-agent-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

`backend/requirements.txt`에 추가:
```
redis>=5.0.0
```

## 🔧 트러블슈팅

### 포트 충돌
```bash
# 포트 사용 중인 프로세스 확인
lsof -i :3000
lsof -i :8000

# 프로세스 종료
kill -9 <PID>
```

### 로그 확인
```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스
docker-compose logs -f backend
docker-compose logs -f frontend

# 최근 100줄만
docker-compose logs --tail=100 backend
```

### 컨테이너 재시작
```bash
# 특정 서비스만 재시작
docker-compose restart backend

# 모든 서비스 재시작
docker-compose restart
```

### 이미지 다시 빌드
```bash
# 캐시 없이 완전히 다시 빌드
docker-compose build --no-cache

# 빌드 후 바로 실행
docker-compose up --build --force-recreate
```

### 디스크 공간 정리
```bash
# 사용하지 않는 이미지/컨테이너 삭제
docker system prune -a

# 볼륨까지 삭제
docker system prune -a --volumes
```

## 📊 배포 체크리스트

- [ ] `.env` 파일 생성 및 API 키 설정
- [ ] Pinecone 인덱스 생성 (dimension=1536)
- [ ] 로컬에서 `docker-compose up --build` 테스트
- [ ] AWS 보안 그룹 설정 (포트 오픈)
- [ ] EC2 인스턴스에 Docker 설치
- [ ] 프로젝트 파일 업로드 (Git 또는 SCP)
- [ ] `docker-compose up -d --build` 실행
- [ ] 로그 확인 및 정상 작동 테스트
- [ ] (선택) 도메인 연결 및 SSL 인증서 설정
- [ ] (선택) Nginx 리버스 프록시 설정
- [ ] (선택) CloudWatch 모니터링 설정

## 🔐 보안 권장사항

1. **환경 변수 보안**
   - AWS Secrets Manager 사용
   - `.env` 파일 절대 Git에 커밋하지 않기

2. **HTTPS 설정** (프로덕션 필수)
   - Let's Encrypt 사용 (무료)
   - Certbot으로 자동 갱신

3. **방화벽 설정**
   - 필요한 포트만 오픈
   - SSH는 특정 IP만 허용

4. **정기 업데이트**
   ```bash
   # Docker 이미지 업데이트
   docker-compose pull
   docker-compose up -d
   ```

## 📚 추가 리소스

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [AWS EC2 가이드](https://docs.aws.amazon.com/ec2/)
- [Next.js Standalone 배포](https://nextjs.org/docs/advanced-features/output-file-tracing)

