# GitHub Actions CI/CD 설정 가이드

## 개요

이 프로젝트는 다음과 같은 CI/CD 파이프라인을 제공합니다:

- **메인 워크플로우** (`.github/workflows/ci-cd.yml`): 전체 테스트, 빌드, 배포
- **스테이징 워크플로우** (`.github/workflows/deploy-staging.yml`): 빠른 테스트 및 스테이징 배포

## 필요한 Secrets 설정

GitHub 리포지토리의 Settings > Secrets and variables > Actions에서 다음 secrets를 설정해야 합니다:

### 1. Docker Hub 설정
```
DOCKER_USERNAME: Docker Hub 사용자명
DOCKER_PASSWORD: Docker Hub 비밀번호 또는 토큰
```

### 2. Railway 배포 설정
```
RAILWAY_TOKEN: Railway 프로젝트 토큰
```

Railway 토큰 생성 방법:
1. [Railway](https://railway.app/) 로그인
2. 프로젝트 선택 후 Settings > Tokens
3. 새 토큰 생성 및 복사

### 3. 슬랙 알림 설정 (선택사항)
```
SLACK_WEBHOOK_URL: Slack 웹훅 URL
```

## 배포 서비스 설정

### Railway 사용 시

1. **Railway 프로젝트 생성**
   ```bash
   # Railway CLI 설치
   curl -fsSL https://railway.app/install.sh | sh

   # 로그인
   railway login

   # 프로젝트 생성
   railway new pyladies-seoul
   ```

2. **환경 변수 설정**
   Railway 대시보드에서 다음 환경 변수를 설정:
   ```
   SECRET_KEY: Django 시크릿 키
   DEBUG: False
   ALLOWED_HOSTS: your-app.railway.app
   DATABASE_URL: (자동 생성됨)
   ```

3. **데이터베이스 추가**
   ```bash
   railway add postgresql
   ```

### DigitalOcean App Platform 사용 시

1. **앱 생성**
   - DigitalOcean 대시보드에서 "Create App" 선택
   - GitHub 리포지토리 연결

2. **환경 변수 설정**
   ```
   SECRET_KEY: Django 시크릿 키
   DEBUG: False
   DATABASE_URL: 데이터베이스 연결 문자열
   ```

3. **빌드 설정**
   ```yaml
   # app.yaml
   name: pyladies-seoul
   services:
   - name: web
     dockerfile_path: Dockerfile
     http_port: 8000
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
   ```

### Google Cloud Run 사용 시

1. **서비스 계정 생성**
   ```bash
   gcloud iam service-accounts create pyladies-seoul-deploy \
     --display-name="PyLadies Seoul Deploy"
   ```

2. **권한 부여**
   ```bash
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:pyladies-seoul-deploy@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.admin"
   ```

3. **키 파일 생성 및 GitHub Secrets 추가**
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=pyladies-seoul-deploy@PROJECT_ID.iam.gserviceaccount.com
   ```

## 워크플로우 설명

### 메인 워크플로우 (main 브랜치)

1. **Lint 검사**
   - pre-commit hooks 실행
   - Black, isort, flake8, mypy 검사

2. **보안 검사**
   - bandit: 보안 취약점 스캔
   - safety: 의존성 취약점 검사

3. **테스트 실행**
   - PostgreSQL 서비스 시작
   - Django 테스트 실행
   - 커버리지 측정 및 업로드

4. **프론트엔드 빌드**
   - Node.js 의존성 설치
   - Tailwind CSS 컴파일

5. **Docker 이미지 빌드**
   - 멀티스테이지 Docker 빌드
   - 이미지 태깅 및 푸시

6. **배포**
   - Railway/DigitalOcean/GCP 배포
   - 슬랙 알림 발송

### 스테이징 워크플로우 (develop 브랜치)

1. **빠른 테스트**
   - 기본 테스트만 실행 (병렬 처리)

2. **스테이징 배포**
   - CSS 빌드
   - Railway 스테이징 환경 배포

## 환경별 설정

### 로컬 개발 환경

```bash
# 의존성 설치
uv sync

# pre-commit 설정
pre-commit install

# 테스트 실행
python manage.py test

# 커버리지 측정
coverage run --source='.' manage.py test
coverage report
```

### 개발 도구 설정

#### VS Code 설정
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true
}
```

#### PyCharm 설정
1. File > Settings > Project > Python Interpreter
2. Add Interpreter > Existing Environment
3. `.venv/bin/python` 선택

## 트러블슈팅

### 일반적인 오류

#### 1. UV 관련 오류
```bash
# UV 재설치
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

#### 2. 의존성 오류
```bash
# 의존성 다시 설치
uv sync --reinstall
```

#### 3. pre-commit 오류
```bash
# pre-commit 재설치
pre-commit uninstall
pre-commit install
pre-commit run --all-files
```

#### 4. Docker 빌드 오류
```bash
# Docker 캐시 클리어
docker system prune -a
```

### 배포 관련 오류

#### Railway 배포 실패
1. Railway 토큰 확인
2. 서비스 이름 확인
3. 환경 변수 설정 확인

#### 테스트 실패
1. PostgreSQL 서비스 상태 확인
2. 환경 변수 설정 확인
3. 테스트 데이터베이스 권한 확인

## 성능 최적화

### GitHub Actions 최적화

1. **캐시 활용**
   - Python 의존성 캐시
   - Node.js 의존성 캐시
   - Docker 레이어 캐시

2. **병렬 처리**
   - 테스트 병렬 실행
   - 독립적인 Job 병렬 처리

3. **조건부 실행**
   - 변경된 파일에 따른 선택적 실행
   - 브랜치별 다른 워크플로우

### 배포 최적화

1. **이미지 크기 최소화**
   - 멀티스테이지 빌드
   - 불필요한 패키지 제거

2. **배포 속도 향상**
   - 이미지 캐싱
   - 증분 배포

## 보안 고려사항

1. **Secrets 관리**
   - GitHub Secrets 사용
   - 환경별 다른 토큰 사용

2. **의존성 보안**
   - 정기적인 의존성 업데이트
   - 보안 취약점 모니터링

3. **이미지 보안**
   - 베이스 이미지 정기 업데이트
   - 보안 스캔 도구 사용

## 모니터링 및 알림

### 배포 모니터링
- Railway/DigitalOcean/GCP 모니터링 도구 활용
- 로그 집계 및 분석

### 알림 설정
- 슬랙 통합
- 이메일 알림
- 배포 상태 뱃지
