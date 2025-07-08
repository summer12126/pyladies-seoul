# 코딩 스타일 가이드

PyLadies Seoul 프로젝트의 코딩 스타일과 컨벤션을 정의합니다.

## 🐍 Python 코딩 스타일

### 기본 원칙

1. **PEP 8 준수**: Python의 공식 스타일 가이드를 따릅니다
2. **가독성 우선**: 코드는 읽기 쉬워야 합니다
3. **일관성 유지**: 프로젝트 전체에서 일관된 스타일을 유지합니다

### 포매팅 규칙

```python
# 줄 길이: 79자 제한
MAX_LINE_LENGTH = 79

# 들여쓰기: 4칸 스페이스
def example_function():
    if condition:
        return True
    return False

# 함수/클래스 간 빈 줄
class ExampleClass:
    """클래스 docstring."""

    def method_one(self):
        """메서드 docstring."""
        pass

    def method_two(self):
        """메서드 docstring."""
        pass


def standalone_function():
    """독립 함수 docstring."""
    pass
```

### 명명 규칙

```python
# 변수, 함수: snake_case
user_name = "example"
def get_user_data():
    pass

# 클래스: PascalCase
class UserProfile:
    pass

# 상수: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30

# 비공개 변수/메서드: 앞에 언더스코어
class Example:
    def __init__(self):
        self._private_var = "private"

    def _private_method(self):
        pass
```

### 타입 힌트

모든 함수와 메서드에 타입 힌트를 사용합니다:

```python
from typing import List, Dict, Optional, Union
from django.http import HttpRequest, HttpResponse

def process_user_data(
    user_id: int,
    data: Dict[str, str],
    options: Optional[List[str]] = None
) -> bool:
    """사용자 데이터를 처리합니다."""
    if options is None:
        options = []

    # 처리 로직
    return True

def view_function(request: HttpRequest) -> HttpResponse:
    """Django 뷰 함수."""
    return HttpResponse("Hello")
```

### Docstring 규칙

```python
def calculate_total(items: List[Dict[str, float]], tax_rate: float) -> float:
    """
    아이템 목록의 총합을 세금과 함께 계산합니다.

    Args:
        items: 가격 정보가 포함된 아이템 목록
        tax_rate: 세율 (0.0 ~ 1.0)

    Returns:
        세금이 포함된 총 금액

    Raises:
        ValueError: tax_rate가 유효하지 않을 때

    Example:
        >>> items = [{"price": 100.0}, {"price": 200.0}]
        >>> calculate_total(items, 0.1)
        330.0
    """
    if not 0 <= tax_rate <= 1:
        raise ValueError("Tax rate must be between 0 and 1")

    subtotal = sum(item["price"] for item in items)
    return subtotal * (1 + tax_rate)
```

## 🎯 Django 특화 규칙

### 모델 정의

```python
from django.db import models
from django.utils.translation import gettext_lazy as _

class Activity(models.Model):
    """활동 모델."""

    title_ko = models.CharField(
        max_length=200,
        verbose_name=_("제목 (한국어)"),
        help_text=_("활동의 한국어 제목을 입력하세요"),
        db_comment="Korean title of the activity"
    )
    title_en = models.CharField(
        max_length=200,
        verbose_name=_("제목 (영어)"),
        help_text=_("활동의 영어 제목을 입력하세요"),
        db_comment="English title of the activity"
    )

    class Meta:
        verbose_name = _("활동")
        verbose_name_plural = _("활동들")
        db_table = "activities"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title_ko or self.title_en
```

### 뷰 함수

```python
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet

def activity_list(request: HttpRequest) -> HttpResponse:
    """활동 목록 뷰."""
    activities: QuerySet[Activity] = Activity.objects.select_related(
        "category"
    ).prefetch_related(
        "participants"
    ).filter(
        is_active=True
    ).order_by("-created_at")

    context = {
        "activities": activities,
        "title": "활동 목록"
    }
    return render(request, "activities/list.html", context)
```

### URL 패턴

```python
from django.urls import path
from . import views

app_name = "activities"

urlpatterns = [
    path("", views.activity_list, name="list"),
    path("<int:pk>/", views.activity_detail, name="detail"),
    path("create/", views.activity_create, name="create"),
    path("<int:pk>/update/", views.activity_update, name="update"),
    path("<int:pk>/delete/", views.activity_delete, name="delete"),
]
```

## 🎨 프론트엔드 스타일

### HTML 템플릿

```html
<!-- 들여쓰기: 2칸 스페이스 -->
<div class="container mx-auto px-4">
  <h1 class="text-2xl font-bold mb-4">
    {{ title }}
  </h1>

  {% for activity in activities %}
    <div class="bg-white rounded-lg shadow-md p-6 mb-4">
      <h2 class="text-xl font-semibold mb-2">
        {{ activity.title_ko }}
      </h2>
      <p class="text-gray-600">
        {{ activity.description|truncatewords:20 }}
      </p>
    </div>
  {% empty %}
    <p class="text-gray-500 text-center py-8">
      등록된 활동이 없습니다.
    </p>
  {% endfor %}
</div>
```

### CSS/Tailwind 클래스

```html
<!-- 의미 있는 클래스 조합 -->
<button class="btn btn-primary">
  <!-- 또는 -->
  <button class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded">
    버튼
  </button>
</button>

<!-- 반응형 디자인 -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- 콘텐츠 -->
</div>
```

## 🧪 테스트 코드

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class ActivityViewTests(TestCase):
    """활동 뷰 테스트."""

    def setUp(self) -> None:
        """테스트 설정."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.activity = Activity.objects.create(
            title_ko="테스트 활동",
            title_en="Test Activity",
            description="테스트 설명"
        )

    def test_activity_list_view(self) -> None:
        """활동 목록 뷰 테스트."""
        url = reverse("activities:list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "테스트 활동")
        self.assertContains(response, "Test Activity")
```

## 📝 커밋 메시지

### 커밋 메시지 형식

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 타입 분류

- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 스타일 변경
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드 과정 또는 도구 변경

### 예시

```
feat(activities): Add activity filtering by category

- Add category filter dropdown in activity list
- Update activity list view to handle category parameter
- Add tests for category filtering functionality

Closes #123
```

## 🔧 자동화 도구

### Pre-commit 훅

프로젝트에서 사용하는 자동화 도구들:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
        args: ["--profile", "black", "--line-length", "79"]

  - repo: https://github.com/psf/black
    hooks:
      - id: black
        args: ["--line-length", "79"]

  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
        args: ["--max-line-length", "79"]
```

### IDE 설정

**VS Code 설정 예시 (`.vscode/settings.json`)**:

```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "79"],
  "python.sortImports.args": ["--profile", "black", "--line-length", "79"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## 📚 참고 자료

- [PEP 8 – Style Guide for Python Code](https://pep8.org/)
- [Django Coding Style](https://docs.djangoproject.com/en/stable/internals/contributing/writing-code/coding-style/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Black Code Style](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)
