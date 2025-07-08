"""
통합 테스트 - 전체 워크플로우 테스트
"""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponse
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse

from .models import Activity, Organizer
from .test_factories import (
    ActivityFactory,
    ContributionOpportunityFactory,
    OrganizerFactory,
    SocialMediaPlatformFactory,
    create_sample_activities,
    create_sample_organizers,
)

User = get_user_model()


class FullWorkflowTest(TestCase):
    """전체 워크플로우 통합 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()

        # 관리자 사용자 생성
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )

        # 기본 데이터 생성
        self.platform = SocialMediaPlatformFactory.create()

    def test_complete_content_management_workflow(self) -> None:
        """완전한 컨텐츠 관리 워크플로우 테스트"""
        # 1. 관리자 로그인
        self.client.login(username="admin", password="adminpass123")

        # 2. 새 활동 생성
        activity_data = {
            "title_ko": "새로운 파이썬 세미나",
            "title_en": "New Python Seminar",
            "description_ko": "파이썬 기초를 배우는 세미나입니다.",
            "description_en": "A seminar to learn Python basics.",
            "activity_type": "seminar",
            "is_public": True,
            "is_featured": False,
            "is_recruiting": False,
        }

        response = self.client.post(reverse("admin:main_activity_add"), activity_data)
        self.assertEqual(response.status_code, 302)

        # 활동이 생성되었는지 확인
        self.assertTrue(Activity.objects.filter(title_ko="새로운 파이썬 세미나").exists())

        # 3. 오거나이저 생성
        organizer_data = {
            "name_ko": "김파이썬",
            "name_en": "Python Kim",
            "role_ko": "리드 오거나이저",
            "role_en": "Lead Organizer",
            "bio_ko": "파이썬 전문가입니다.",
            "bio_en": "Python expert.",
            "email": "python@example.com",
            "order": 0,
            "is_public": True,
        }

        response = self.client.post(reverse("admin:main_organizer_add"), organizer_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Organizer.objects.filter(name_ko="김파이썬").exists())

        # 4. FAQ 생성
        faq_data = {
            "category": "general",
            "question_ko": "파이레이디스는 무엇인가요?",
            "question_en": "What is PyLadies?",
            "answer_ko": "여성 파이썬 개발자 커뮤니티입니다.",
            "answer_en": "A community for women Python developers.",
            "order": 0,
            "is_public": True,
        }

        response = self.client.post(reverse("admin:main_faq_add"), faq_data)
        self.assertEqual(response.status_code, 302)

        # 5. 기여 기회 생성
        opportunity_data = {
            "type": "speaker",
            "title_ko": "발표자 모집",
            "title_en": "Speaker Recruitment",
            "description_ko": "발표자를 모집합니다.",
            "description_en": "We are recruiting speakers.",
            "requirements_ko": "파이썬 경험 필요",
            "requirements_en": "Python experience required",
            "contact_method_ko": "이메일 연락",
            "contact_method_en": "Contact via email",
            "order": 0,
            "is_open": True,
            "is_public": True,
        }

        response = self.client.post(reverse("admin:main_contributionopportunity_add"), opportunity_data)
        self.assertEqual(response.status_code, 302)

        # 6. 관리자 로그아웃
        self.client.logout()

        # 7. 일반 사용자로 홈페이지 방문
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

        # 생성된 컨텐츠가 홈페이지에 표시되는지 확인
        content = response.content.decode("utf-8")
        self.assertIn("새로운 파이썬 세미나", content)
        self.assertIn("김파이썬", content)

        # 8. 다른 페이지들도 확인
        pages = [
            ("contribute", "발표자 모집"),
            ("faq", "파이레이디스는 무엇인가요?"),
            ("coc", "행동 강령"),
        ]

        for page_name, expected_content in pages:
            response = self.client.get(reverse(page_name))
            self.assertEqual(response.status_code, 200)
            content = response.content.decode("utf-8")
            self.assertIn(expected_content, content)

    def test_data_consistency_across_pages(self) -> None:
        """페이지 간 데이터 일관성 테스트"""
        # 테스트 데이터 생성
        ActivityFactory.create(title_ko="일관성 테스트 활동", is_public=True, is_featured=True)
        OrganizerFactory.create(name_ko="일관성 테스트 오거나이저", is_public=True)

        # 모든 페이지에서 동일한 데이터가 표시되는지 확인
        pages = ["home", "contribute", "faq", "coc"]

        for page in pages:
            response: HttpResponse = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200)

            # 공통 컨텍스트 데이터가 모든 페이지에 있는지 확인
            self.assertIn("community_info", response.context)
            self.assertIn("social_platforms", response.context)
            self.assertIn("discord_url", response.context)

    def test_error_recovery_workflow(self) -> None:
        """에러 복구 워크플로우 테스트"""
        # 잘못된 데이터로 모델 생성 시도
        with self.assertRaises(Exception):
            # 잘못된 이메일 형식으로 오거나이저 생성
            organizer = OrganizerFactory.build(email="invalid-email")
            organizer.full_clean()  # 유효성 검사에서 실패해야 함

        # 정상적인 데이터로 다시 생성
        organizer = OrganizerFactory.create(email="valid@example.com")
        self.assertIsNotNone(organizer)

        # 홈페이지가 여전히 정상 작동하는지 확인
        response: HttpResponse = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)


class DatabaseIntegrityTest(TransactionTestCase):
    """데이터베이스 무결성 테스트"""

    def test_concurrent_data_creation(self) -> None:
        """동시 데이터 생성 테스트"""

        def create_activities():
            for i in range(5):
                ActivityFactory.create(title_ko=f"동시 생성 활동 {i}")

        def create_organizers():
            for i in range(5):
                OrganizerFactory.create(
                    name_ko=f"동시 생성 오거나이저 {i}",
                    email=f"organizer{i}@example.com",
                )

        # 동시에 데이터 생성
        with transaction.atomic():
            create_activities()
            create_organizers()

        # 모든 데이터가 정상적으로 생성되었는지 확인
        self.assertEqual(Activity.objects.count(), 5)
        self.assertEqual(Organizer.objects.count(), 5)

    def test_data_migration_simulation(self) -> None:
        """데이터 마이그레이션 시뮬레이션 테스트"""
        # 기존 데이터 생성
        old_activities = create_sample_activities(3)
        old_organizers = create_sample_organizers(3)

        # 초기 데이터 개수 확인
        initial_activity_count = Activity.objects.count()
        initial_organizer_count = Organizer.objects.count()

        # 마이그레이션 시뮬레이션 (데이터 업데이트)
        for activity in old_activities:
            activity.is_featured = True
            activity.save()

        for organizer in old_organizers:
            organizer.order += 10  # order 값 업데이트
            organizer.save()

        # 데이터 개수가 변하지 않았는지 확인
        self.assertEqual(Activity.objects.count(), initial_activity_count)
        self.assertEqual(Organizer.objects.count(), initial_organizer_count)

        # 업데이트된 값이 정확한지 확인
        for activity in Activity.objects.all():
            self.assertTrue(activity.is_featured)

        for organizer in Organizer.objects.all():
            self.assertGreaterEqual(organizer.order, 10)


class PerformanceIntegrationTest(TestCase):
    """성능 통합 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()

        # 대규모 데이터셋 생성
        create_sample_activities(50)
        create_sample_organizers(20)
        SocialMediaPlatformFactory.create_batch(5)

    def test_homepage_performance_with_large_dataset(self) -> None:
        """대규모 데이터셋 환경에서 홈페이지 성능 테스트"""
        from django.db import connection
        from django.test.utils import override_settings

        with override_settings(DEBUG=True):
            # 쿼리 수 측정
            initial_queries = len(connection.queries)

            response: HttpResponse = self.client.get(reverse("home"))

            final_queries = len(connection.queries)
            query_count = final_queries - initial_queries

            # 성능 검증
            self.assertEqual(response.status_code, 200)
            self.assertLess(query_count, 30)  # 쿼리 수 제한

            # 응답 시간 검증 (간접적)
            self.assertIn("recent_activities", response.context)
            self.assertLessEqual(len(response.context["recent_activities"]), 3)  # 최신 3개만 로드

    def test_all_pages_performance(self) -> None:
        """모든 페이지 성능 테스트"""
        pages = ["home", "contribute", "faq", "coc"]

        for page in pages:
            with self.subTest(page=page):
                response: HttpResponse = self.client.get(reverse(page))
                self.assertEqual(response.status_code, 200)

                # 응답 크기가 합리적인지 확인 (10MB 미만)
                content_length = len(response.content)
                self.assertLess(content_length, 10 * 1024 * 1024)


class SecurityIntegrationTest(TestCase):
    """보안 통합 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")

    def test_xss_protection(self) -> None:
        """XSS 보호 테스트"""
        # 악의적인 스크립트를 포함하는 활동 생성
        ActivityFactory.create(title_ko='<script>alert("XSS")</script>', is_public=True)

        # 홈페이지에서 스크립트가 실행되지 않는지 확인
        response: HttpResponse = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('<script>alert("XSS")</script>', response.content.decode())
        self.assertIn("&lt;script&gt;", response.content.decode())

    def test_sql_injection_protection(self) -> None:
        """SQL 인젝션 보호 테스트"""
        # 홈페이지 검색 기능 등에서 테스트
        response = self.client.get(reverse("home") + "?q='; --")  # 예시
        self.assertEqual(response.status_code, 200)

    def test_csrf_protection(self) -> None:
        """CSRF 보호 테스트"""
        self.client.login(username="testuser", password="password")

        # 관리자만 접근 가능한 기능에 일반 사용자가 접근 시도
        activity_data = {
            "title_ko": "CSRF 시도",
            "title_en": "CSRF Attempt",
            "activity_type": "seminar",
            "is_public": True,
        }

        # CSRF 토큰 없이 POST 요청 보내기
        # 참고: Django의 테스트 클라이언트는 기본적으로 CSRF 체크를 비활성화함
        # 실제 CSRF 테스트는 Client(enforce_csrf_checks=True)를 사용해야 함
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username="testuser", password="password")
        response = csrf_client.post(reverse("admin:main_activity_add"), activity_data)

        # 일반 사용자는 이 뷰에 접근할 수 없으므로 로그인 페이지로 리디렉션되거나
        # 권한 거부(403) 응답을 받아야 함
        self.assertIn(response.status_code, [302, 403])


class AccessibilityIntegrationTest(TestCase):
    """접근성 통합 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()

        # 테스트 데이터 생성
        create_sample_activities(3)
        create_sample_organizers(3)
        SocialMediaPlatformFactory.create()
        ContributionOpportunityFactory.create()

    def test_semantic_html_structure(self) -> None:
        """시맨틱 HTML 구조 테스트"""
        response: HttpResponse = self.client.get(reverse("home"))
        content = response.content.decode("utf-8")

        # 시맨틱 HTML 요소들이 포함되어 있는지 확인
        semantic_elements = [
            "<header",
            "<nav",
            "<main",
            "<section",
            "<article",
            "<aside",
            "<footer",
        ]

        for element in semantic_elements:
            self.assertIn(element, content)

    def test_alt_text_for_images(self) -> None:
        """이미지 alt 텍스트 테스트"""
        response: HttpResponse = self.client.get(reverse("home"))
        content = response.content.decode("utf-8")

        # img 태그가 있다면 alt 속성이 있는지 확인
        import re

        img_tags = re.findall(r"<img[^>]*>", content)

        for img_tag in img_tags:
            self.assertIn("alt=", img_tag)

    def test_heading_hierarchy(self) -> None:
        """헤딩 계층 구조 테스트"""
        response: HttpResponse = self.client.get(reverse("home"))
        content = response.content.decode("utf-8")

        # h1 태그가 존재하는지 확인
        self.assertIn("<h1", content)

        # 페이지 제목이 적절한지 확인
        self.assertIn("<title>", content)


class MultiLanguageIntegrationTest(TestCase):
    """다국어 통합 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()
        create_sample_activities(3)
        create_sample_organizers(3)
        SocialMediaPlatformFactory.create_batch(3)

    def test_korean_content_display(self) -> None:
        """한국어 컨텐츠 표시 테스트"""
        response: HttpResponse = self.client.get(reverse("home"))
        content = response.content.decode("utf-8")

        # 한국어 컨텐츠가 표시되는지 확인
        self.assertIn("한국어 제목", content)
        self.assertIn("파이레이디스 서울", content)

    def test_english_content_availability(self) -> None:
        """영어 컨텐츠 가용성 테스트"""
        # 영어 컨텐츠가 데이터베이스에 저장되어 있는지 확인
        self.assertEqual(self.activity.title_en, "English Title")
        self.assertEqual(self.activity.description_en, "English Description")

        # 향후 국제화를 위한 기반이 마련되어 있는지 확인
        self.assertIsNotNone(self.activity.title_en)
        self.assertIsNotNone(self.activity.description_en)
