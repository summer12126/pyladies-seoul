# 개발 환경 설정

PyLadies Seoul 프로젝트의 개발 환경을 설정하는 방법을 설명합니다.

## 📋 사전 요구사항

다음 도구들이 시스템에 설치되어 있어야 합니다:

- **Python 3.11+**: [Python 공식 웹사이트](https://python.org)
- **Git**: [Git 공식 웹사이트](https://git-scm.com)
- **UV**: Python 패키지 관리자 (권장)
- **Node.js**: Tailwind CSS 빌드용 (선택사항)

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/pyladies-seoul/pyladies-seoul.git
cd pyladies-seoul
```

### 2. UV 설치 (권장)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. 가상환경 생성 및 의존성 설치

```bash
# UV 사용 (권장)
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate     # Windows

uv sync
```

### 4. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
# SECRET_KEY=your-secret-key-here
# DEBUG=True
# DATABASE_URL=sqlite:///db.sqlite3
```

### 5. 데이터베이스 설정

```bash
# 마이그레이션 실행
uv run python manage.py migrate

# 슈퍼유저 생성
uv run python manage.py createsuperuser
```

### 6. 개발 서버 실행

```bash
uv run python manage.py runserver
```

브라우저에서 `http://127.0.0.1:8000`으로 접속하여 확인합니다.

## 🛠️ 개발 도구 설정

### Pre-commit 훅 설정

```bash
# pre-commit 설치 및 훅 설정
uv run pre-commit install

# 모든 파일에 대해 검사 실행
uv run pre-commit run --all-files
```

### 코드 품질 검사

```bash
# 타입 검사
uv run mypy .

# 코드 포매팅
uv run black .
uv run isort .

# 린팅
uv run flake8 .
```

## 🎨 프론트엔드 개발

### Tailwind CSS 설정

```bash
# Node.js 의존성 설치
npm install

# Tailwind CSS 빌드 (개발 모드)
npm run dev

# Tailwind CSS 빌드 (프로덕션 모드)
npm run build
```

## 🧪 테스트 실행

```bash
# 모든 테스트 실행
uv run python manage.py test

# 특정 앱 테스트
uv run python manage.py test main

# 커버리지 포함 테스트
uv run coverage run --source='.' manage.py test
uv run coverage report
```

## 📊 데이터베이스 관리

### 마이그레이션 생성

```bash
# 모델 변경 후 마이그레이션 생성
uv run python manage.py makemigrations

# 특정 앱의 마이그레이션 생성
uv run python manage.py makemigrations main
```

### 데이터베이스 초기화

```bash
# 데이터베이스 파일 삭제
rm db.sqlite3

# 마이그레이션 재실행
uv run python manage.py migrate
```

## 🔧 문제 해결

### 일반적인 문제들

1. **가상환경 활성화 안됨**
   ```bash
   source .venv/bin/activate
   ```

2. **패키지 설치 오류**
   ```bash
   uv sync --reinstall
   ```

3. **마이그레이션 충돌**
   ```bash
   uv run python manage.py migrate --fake-initial
   ```

4. **정적 파일 문제**
   ```bash
   uv run python manage.py collectstatic
   ```

### 도움 요청

문제가 해결되지 않는 경우:

1. [GitHub Issues](https://github.com/pyladies-seoul/pyladies-seoul/issues) 확인
2. [Discord 채널](https://discord.gg/pyladies-seoul)에서 질문
3. 새로운 이슈 생성

## 📚 추가 자료

- [Django 공식 문서](https://docs.djangoproject.com/)
- [UV 문서](https://docs.astral.sh/uv/)
- [Tailwind CSS 문서](https://tailwindcss.com/docs)
- [Pre-commit 문서](https://pre-commit.com/)
