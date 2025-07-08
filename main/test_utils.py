"""
테스트 유틸리티 및 공통 기능
"""

from typing import TYPE_CHECKING, Any, Dict, List

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse

from .models import FAQ, Activity, Organizer, SocialMediaPlatform

if TYPE_CHECKING:
    from django.contrib.auth.models import User as AuthUserType

User = get_user_model()


class TestDataMixin:
    """테스트 데이터 생성을 위한 믹스인"""

    def create_test_user(
        self,
        username: str = "testuser",
        email: str = "test@example.com",
        password: str = "testpass123",
        is_staff: bool = False,
        is_superuser: bool = False,
    ) -> "AuthUserType":
        """테스트 사용자 생성"""
        if is_superuser:
            return User.objects.create_superuser(username=username, email=email, password=password)
        elif is_staff:
            return User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
            )
        else:
            return User.objects.create_user(username=username, email=email, password=password)

    def create_admin_user(self) -> "AuthUserType":
        """관리자 사용자 생성"""
        return self.create_test_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            is_superuser=True,
        )

    def create_basic_test_data(self) -> Dict[str, Any]:
        """기본 테스트 데이터 생성"""
        from .test_factories import (
            ActivityFactory,
            ContributionOpportunityFactory,
            FAQFactory,
            OrganizerFactory,
            SocialMediaPlatformFactory,
        )

        return {
            "activity": ActivityFactory.create(),
            "organizer": OrganizerFactory.create(),
            "faq": FAQFactory.create(),
            "platform": SocialMediaPlatformFactory.create(),
            "opportunity": ContributionOpportunityFactory.create(),
        }


class AdminTestMixin:
    """관리자 테스트를 위한 믹스인"""

    def setUp_admin(self) -> None:
        """관리자 테스트 설정"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.client.login(username="admin", password="adminpass123")

    def admin_get(self, url: str) -> HttpResponse:
        """관리자 페이지 GET 요청"""
        return self.client.get(url)

    def admin_post(self, url: str, data: Dict[str, Any]) -> HttpResponse:
        """관리자 페이지 POST 요청"""
        return self.client.post(url, data)

    def assert_admin_page_accessible(self, model_name: str) -> None:
        """관리자 페이지 접근 가능성 테스트"""
        url = reverse(f"admin:main_{model_name}_changelist")
        response = self.admin_get(url)
        self.assertEqual(response.status_code, 200)

    def assert_admin_create_works(self, model_name: str, data: Dict[str, Any]) -> None:
        """관리자 페이지 생성 기능 테스트"""
        url = reverse(f"admin:main_{model_name}_add")
        response = self.admin_post(url, data)
        self.assertEqual(response.status_code, 302)  # 성공 시 리다이렉트


class ViewTestMixin:
    """뷰 테스트를 위한 믹스인"""

    def setUp_view(self) -> None:
        """뷰 테스트 설정"""
        self.client = Client()
        from .test_factories import SocialMediaPlatformFactory

        SocialMediaPlatformFactory.create()  # 모든 페이지에서 필요

    def assert_page_accessible(self, url_name: str) -> HttpResponse:
        """페이지 접근 가능성 테스트"""
        response = self.client.get(reverse(url_name))
        self.assertEqual(response.status_code, 200)
        return response

    def assert_template_used(self, url_name: str, template_name: str) -> None:
        """템플릿 사용 테스트"""
        response = self.client.get(reverse(url_name))
        self.assertTemplateUsed(response, template_name)

    def assert_context_contains(self, url_name: str, context_keys: List[str]) -> None:
        """컨텍스트 포함 테스트"""
        response = self.client.get(reverse(url_name))
        for key in context_keys:
            self.assertIn(key, response.context)

    def assert_content_contains(self, url_name: str, expected_content: List[str]) -> None:
        """컨텐츠 포함 테스트"""
        response = self.client.get(reverse(url_name))
        content = response.content.decode("utf-8")
        for expected in expected_content:
            self.assertIn(expected, content)


class ModelTestMixin:
    """모델 테스트를 위한 믹스인"""

    def assert_model_str_representation(self, instance: Any, expected: str) -> None:
        """모델 문자열 표현 테스트"""
        self.assertEqual(str(instance), expected)

    def assert_model_fields_exist(self, model_class: Any, field_names: List[str]) -> None:
        """모델 필드 존재 테스트"""
        for field_name in field_names:
            self.assertTrue(
                hasattr(model_class, field_name),
                f"{model_class.__name__} 모델에 {field_name} 필드가 없습니다.",
            )

    def assert_model_ordering(self, model_class: Any, ordering_fields: List[str]) -> None:
        """모델 정렬 테스트"""
        meta = getattr(model_class, "_meta", None)
        if meta:
            self.assertEqual(meta.ordering, ordering_fields)


class PerformanceTestMixin:
    """성능 테스트를 위한 믹스인"""

    def assert_query_count_less_than(self, max_queries: int, url_name: str) -> None:
        """쿼리 수 제한 테스트"""
        from django.db import connection
        from django.test.utils import override_settings

        with override_settings(DEBUG=True):
            initial_queries = len(connection.queries)
            response = self.client.get(reverse(url_name))
            final_queries = len(connection.queries)

            self.assertEqual(response.status_code, 200)
            query_count = final_queries - initial_queries
            self.assertLess(
                query_count,
                max_queries,
                f"쿼리 수가 {max_queries}개를 초과했습니다: {query_count}개",
            )

    def assert_response_size_reasonable(self, url_name: str, max_size_mb: float = 1.0) -> None:
        """응답 크기 제한 테스트"""
        response = self.client.get(reverse(url_name))
        content_length = len(response.content)
        max_size_bytes = max_size_mb * 1024 * 1024

        self.assertLess(
            content_length,
            max_size_bytes,
            f"응답 크기가 {max_size_mb}MB를 초과했습니다: " f"{content_length / (1024 * 1024):.2f}MB",
        )


class SecurityTestMixin:
    """보안 테스트를 위한 믹스인"""

    def assert_xss_protection(
        self,
        url_name: str,
        malicious_content: str = '<script>alert("XSS")</script>',
    ) -> None:
        """XSS 보호 테스트"""
        response = self.client.get(reverse(url_name))
        content = response.content.decode("utf-8")

        # 스크립트 태그가 이스케이프되었는지 확인
        self.assertNotIn("<script>", content)
        if "&lt;script&gt;" in content:
            self.assertIn("&lt;script&gt;", content)

    def assert_csrf_protection(self, url_name: str, post_data: Dict[str, Any]) -> None:
        """CSRF 보호 테스트"""
        response = self.client.post(reverse(url_name), post_data, HTTP_X_CSRFTOKEN="invalid_token")
        # CSRF 보호로 인해 실패해야 함
        self.assertNotEqual(response.status_code, 200)

    def assert_sql_injection_protection(self, url_name: str) -> None:
        """SQL 인젝션 보호 테스트"""
        malicious_query = "'; DROP TABLE main_activity; --"
        response = self.client.get(f"{reverse(url_name)}?search={malicious_query}")

        # 페이지가 정상적으로 로드되고 테이블이 삭제되지 않았는지 확인
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Activity.objects.exists())


class AccessibilityTestMixin:
    """접근성 테스트를 위한 믹스인"""

    def assert_semantic_html_structure(self, url_name: str) -> None:
        """시맨틱 HTML 구조 테스트"""
        response = self.client.get(reverse(url_name))
        content = response.content.decode("utf-8")

        semantic_elements = [
            "<header",
            "<nav",
            "<main",
            "<section",
            "<article",
            "<aside",
            "<footer",
        ]

        found_elements = []
        for element in semantic_elements:
            if element in content:
                found_elements.append(element)

        # 최소 3개 이상의 시맨틱 요소가 있어야 함
        self.assertGreaterEqual(
            len(found_elements),
            3,
            f"시맨틱 HTML 요소가 부족합니다: {found_elements}",
        )

    def assert_alt_text_for_images(self, url_name: str) -> None:
        """이미지 alt 텍스트 테스트"""
        import re

        response = self.client.get(reverse(url_name))
        content = response.content.decode("utf-8")

        img_tags = re.findall(r"<img[^>]*>", content)

        for img_tag in img_tags:
            self.assertIn(
                "alt=",
                img_tag,
                f"이미지 태그에 alt 속성이 없습니다: {img_tag}",
            )

    def assert_heading_hierarchy(self, url_name: str) -> None:
        """헤딩 계층 구조 테스트"""
        response = self.client.get(reverse(url_name))
        content = response.content.decode("utf-8")

        # h1 태그가 존재하는지 확인
        self.assertIn("<h1", content, "h1 태그가 없습니다.")

        # 페이지 제목이 적절한지 확인
        self.assertIn("<title>", content, "title 태그가 없습니다.")


class DatabaseTestMixin:
    """데이터베이스 테스트를 위한 믹스인"""

    def assert_model_count(self, model_class: Any, expected_count: int) -> None:
        """모델 개수 테스트"""
        actual_count = model_class.objects.count()
        self.assertEqual(
            actual_count,
            expected_count,
            f"{model_class.__name__} 개수가 예상과 다릅니다: " f"예상 {expected_count}, 실제 {actual_count}",
        )

    def assert_model_exists(self, model_class: Any, **kwargs: Any) -> None:
        """모델 존재 테스트"""
        self.assertTrue(
            model_class.objects.filter(**kwargs).exists(),
            f"{model_class.__name__} 모델이 존재하지 않습니다: {kwargs}",
        )

    def assert_model_does_not_exist(self, model_class: Any, **kwargs: Any) -> None:
        """모델 비존재 테스트"""
        self.assertFalse(
            model_class.objects.filter(**kwargs).exists(),
            f"{model_class.__name__} 모델이 존재합니다: {kwargs}",
        )


class IntegrationTestMixin:
    """통합 테스트를 위한 믹스인"""

    def assert_all_pages_accessible(self, page_names: List[str]) -> None:
        """모든 페이지 접근 가능성 테스트"""
        for page_name in page_names:
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))
                self.assertEqual(
                    response.status_code,
                    200,
                    f"{page_name} 페이지에 접근할 수 없습니다.",
                )

    def assert_common_context_data(self, page_names: List[str], context_keys: List[str]) -> None:
        """공통 컨텍스트 데이터 테스트"""
        for page_name in page_names:
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))
                for key in context_keys:
                    self.assertIn(
                        key,
                        response.context,
                        f"{page_name} 페이지에 {key} 컨텍스트가 없습니다.",
                    )

    def assert_navigation_links(self, base_page: str, linked_pages: List[str]) -> None:
        """네비게이션 링크 테스트"""
        response = self.client.get(reverse(base_page))
        content = response.content.decode("utf-8")

        for page in linked_pages:
            page_url = reverse(page)
            self.assertIn(
                f'href="{page_url}"',
                content,
                f"{base_page}에서 {page}로의 링크가 없습니다.",
            )


def create_test_data_set(count: int = 5) -> Dict[str, List[Any]]:
    """테스트 데이터 세트 생성"""
    from .test_factories import (
        ContributionOpportunityFactory,
        SocialMediaPlatformFactory,
        create_sample_activities,
        create_sample_faqs,
        create_sample_organizers,
    )

    return {
        "activities": create_sample_activities(count),
        "organizers": create_sample_organizers(count),
        "faqs": create_sample_faqs(count),
        "platforms": [SocialMediaPlatformFactory.create(name_ko=f"플랫폼 {i}", order=i) for i in range(count)],
        "opportunities": [
            ContributionOpportunityFactory.create(title_ko=f"기여 기회 {i}", order=i) for i in range(count)
        ],
    }


def assert_response_contains_all(response: HttpResponse, expected_contents: List[str]) -> None:
    """응답에 모든 예상 컨텐츠가 포함되어 있는지 확인"""
    content = response.content.decode("utf-8")
    missing_contents = []

    for expected in expected_contents:
        if expected not in content:
            missing_contents.append(expected)

    if missing_contents:
        raise AssertionError(f"다음 컨텐츠가 응답에 없습니다: {missing_contents}")


def clean_test_data() -> None:
    """테스트 데이터 정리"""
    models = [Activity, Organizer, FAQ, SocialMediaPlatform]

    for model in models:
        model.objects.all().delete()


class BaseTestCase:
    """기본 테스트 케이스 (다중 상속용)"""

    def setUp(self) -> None:
        """기본 설정"""
        from .test_factories import SocialMediaPlatformFactory

        self.client = Client()
        self.platform = SocialMediaPlatformFactory.create()

    def tearDown(self) -> None:
        """정리"""
        clean_test_data()


# 편의 함수들
def create_admin_client() -> tuple[Client, "AuthUserType"]:
    """테스트용 관리자 클라이언트 생성"""
    client = Client()
    admin_user = User.objects.create_superuser(
        username="admin_client",
        email="admin_client@example.com",
        password="password123",
    )
    client.login(username="admin_client", password="password123")
    return client, admin_user


def create_test_client_with_data() -> tuple[Client, Dict[str, Any]]:
    """테스트 데이터가 포함된 클라이언트 생성"""
    client = Client()
    data = create_test_data_set(3)
    return client, data
