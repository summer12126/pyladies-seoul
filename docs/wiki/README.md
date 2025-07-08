# PyLadies Seoul Wiki 관리

이 디렉토리는 GitHub Wiki 콘텐츠를 관리하는 곳입니다.

## 📚 Wiki 구조

```
docs/wiki/
├── Home.md                    # Wiki 홈페이지
├── Development-Setup.md       # 개발 환경 설정
├── Coding-Style-Guide.md     # 코딩 스타일 가이드
├── Project-Structure.md      # 프로젝트 구조 (추후 추가)
├── Contributing.md           # 기여 가이드 (추후 추가)
└── README.md                 # 이 파일
```

## 🔄 Wiki 동기화

### 자동 동기화 (권장)

Wiki 내용을 수정한 후 다음 스크립트를 실행하면 GitHub Wiki에 자동으로 동기화됩니다:

```bash
# Wiki 동기화 실행
./scripts/sync-wiki.sh
```

### 수동 동기화

1. **GitHub Wiki 저장소 클론**
   ```bash
   git clone https://github.com/pyladies-seoul/pyladies-seoul.wiki.git
   ```

2. **로컬 Wiki 내용 복사**
   ```bash
   cp docs/wiki/*.md pyladies-seoul.wiki/
   ```

3. **변경사항 커밋 및 푸시**
   ```bash
   cd pyladies-seoul.wiki
   git add .
   git commit -m "docs: Update wiki content"
   git push origin master
   ```

## 📝 Wiki 작성 가이드

### 파일명 규칙

- **GitHub Wiki 페이지명**: `Development-Setup` (하이픈 사용)
- **파일명**: `Development-Setup.md`
- **내부 링크**: `[개발 환경 설정](Development-Setup)`

### 마크다운 규칙

```markdown
# 페이지 제목 (H1은 하나만)

간단한 페이지 설명

## 주요 섹션 (H2)

### 하위 섹션 (H3)

- 목록 항목
- 다른 항목

```code
코드 블록
```

> 인용구나 중요한 노트

[다른 Wiki 페이지 링크](Other-Page)
[외부 링크](https://example.com)
```

### 이모지 사용

문서의 가독성을 위해 적절한 이모지를 사용합니다:

- 📚 문서/가이드
- 🚀 시작하기/설치
- 🛠️ 개발/도구
- 🔧 설정/구성
- 🧪 테스트
- 📋 목록/체크리스트
- ⚠️ 주의사항
- 💡 팁/아이디어
- ✅ 완료/성공
- ❌ 오류/실패

## 🔗 GitHub Wiki와의 차이점

### 장점
- **버전 관리**: 메인 저장소와 함께 관리
- **코드 리뷰**: PR을 통한 Wiki 내용 검토 가능
- **백업**: 메인 저장소에 백업 보관
- **일관성**: 프로젝트와 문서의 동기화

### 주의사항
- **동기화 필요**: 변경 후 수동으로 동기화 스크립트 실행
- **이미지**: GitHub Wiki에 업로드된 이미지는 별도 관리 필요
- **링크**: 내부 링크는 GitHub Wiki 형식 사용

## 📸 이미지 관리

### 이미지 업로드 방법

1. **GitHub Wiki에서 직접 업로드**
   - GitHub Wiki 페이지에서 이미지 드래그&드롭
   - 생성된 URL을 로컬 마크다운 파일에 복사

2. **GitHub Issues 활용**
   - 이슈에 이미지 업로드
   - 생성된 URL 사용

3. **외부 이미지 호스팅**
   - Imgur, GitHub Pages 등 활용

### 이미지 링크 예시

```markdown
![스크린샷](https://user-images.githubusercontent.com/username/image-id.png)
```

## 🚀 새 Wiki 페이지 추가

1. **로컬에서 마크다운 파일 생성**
   ```bash
   touch docs/wiki/New-Page.md
   ```

2. **내용 작성**
   - 제목과 내용 작성
   - 다른 페이지에서 링크 추가

3. **Home.md 목차 업데이트**
   - 새 페이지 링크를 목차에 추가

4. **동기화 실행**
   ```bash
   ./scripts/sync-wiki.sh
   ```

## 📋 Wiki 페이지 체크리스트

새 Wiki 페이지를 작성할 때 확인사항:

- [ ] 명확한 제목 (H1)
- [ ] 간단한 페이지 설명
- [ ] 목차 (필요한 경우)
- [ ] 적절한 이모지 사용
- [ ] 코드 블록 문법 하이라이팅
- [ ] 내부/외부 링크 확인
- [ ] Home.md 목차에 추가
- [ ] 동기화 스크립트 실행

## 🤝 기여하기

Wiki 개선에 기여하는 방법:

1. **이슈 생성**: 누락된 문서나 개선사항 제안
2. **PR 생성**: 새 문서 작성이나 기존 문서 개선
3. **리뷰 참여**: 다른 사람의 Wiki PR 리뷰

## 📞 도움말

Wiki 관련 질문이나 문제가 있는 경우:

- [GitHub Issues](https://github.com/pyladies-seoul/pyladies-seoul/issues)에 질문 등록
- [Discord 채널](https://discord.gg/pyladies-seoul)에서 실시간 질문
- Wiki 관리자에게 직접 연락
