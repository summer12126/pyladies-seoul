#!/bin/bash

# GitHub Wiki 동기화 스크립트
# 로컬 docs/wiki 폴더의 내용을 GitHub Wiki에 동기화합니다.

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 설정
REPO_NAME="pyladies-seoul"
ORG_NAME="pyladies-seoul"
WIKI_URL="https://github.com/${ORG_NAME}/${REPO_NAME}.wiki.git"
TEMP_DIR="/tmp/wiki-sync"
DOCS_DIR="docs/wiki"

echo -e "${GREEN}🔄 GitHub Wiki 동기화를 시작합니다...${NC}"

# 임시 디렉토리 정리
if [ -d "$TEMP_DIR" ]; then
    echo -e "${YELLOW}기존 임시 디렉토리를 정리합니다...${NC}"
    rm -rf "$TEMP_DIR"
fi

# Wiki 저장소 클론
echo -e "${YELLOW}Wiki 저장소를 클론합니다...${NC}"
git clone "$WIKI_URL" "$TEMP_DIR" 2>/dev/null || {
    echo -e "${RED}❌ Wiki 저장소 클론에 실패했습니다.${NC}"
    echo -e "${YELLOW}💡 GitHub에서 Wiki를 먼저 활성화해야 합니다.${NC}"
    echo -e "   1. GitHub 저장소 페이지로 이동"
    echo -e "   2. Settings 탭 클릭"
    echo -e "   3. Features 섹션에서 Wikis 체크박스 활성화"
    echo -e "   4. Wiki 탭에서 첫 번째 페이지 생성"
    exit 1
}

# 기존 Wiki 내용 백업
echo -e "${YELLOW}기존 Wiki 내용을 백업합니다...${NC}"
cd "$TEMP_DIR"
if [ -n "$(ls -A .)" ]; then
    mkdir -p backup
    cp *.md backup/ 2>/dev/null || true
fi

# 새 Wiki 내용 복사
echo -e "${YELLOW}새 Wiki 내용을 복사합니다...${NC}"
cd - > /dev/null
cp "$DOCS_DIR"/*.md "$TEMP_DIR/"

# Wiki 저장소에 커밋 및 푸시
cd "$TEMP_DIR"
git add .
if git diff --staged --quiet; then
    echo -e "${GREEN}✅ Wiki에 변경사항이 없습니다.${NC}"
else
    echo -e "${YELLOW}Wiki 변경사항을 커밋합니다...${NC}"
    git commit -m "docs: Update wiki from main repository

- Sync wiki content from docs/wiki directory
- Updated: $(date '+%Y-%m-%d %H:%M:%S')"

    echo -e "${YELLOW}Wiki 변경사항을 푸시합니다...${NC}"
    git push origin master
    echo -e "${GREEN}✅ Wiki 동기화가 완료되었습니다!${NC}"
fi

# 정리
cd - > /dev/null
rm -rf "$TEMP_DIR"

echo -e "${GREEN}🎉 Wiki 동기화 작업이 완료되었습니다.${NC}"
echo -e "Wiki 확인: https://github.com/${ORG_NAME}/${REPO_NAME}/wiki"
