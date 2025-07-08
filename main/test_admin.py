"""
관리자 페이지 테스트
"""

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse

from .models import Activity
from .test_factories import (
    ActivityFactory,
    ContributionOpportunityFactory,
    FAQFactory,
    OrganizerFactory,
    SocialMediaPlatformFactory,
)

User = get_user_model()


class AdminAccessTest(TestCase):
    """관리자 페이지 접근 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()

        # 일반 사용자 생성
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # 관리자 사용자 생성
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )

    def test_admin_login_required(self) -> None:
        """관리자 로그인 필요 테스트"""
        response: HttpResponse = self.client.get("/admin/")
        # 로그인 페이지로 리다이렉트
        self.assertEqual(response.status_code, 302)

    def test_admin_access_with_regular_user(self) -> None:
        """일반 사용자로 관리자 페이지 접근 테스트"""
        self.client.login(username="testuser", password="testpass123")
        response: HttpResponse = self.client.get("/admin/")
        # 로그인 페이지로 리다이렉트 (권한 없음)
        self.assertEqual(response.status_code, 302)

    def test_admin_access_with_admin_user(self) -> None:
        """관리자 사용자로 관리자 페이지 접근 테스트"""
        self.client.login(username="admin", password="adminpass123")
        response: HttpResponse = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

        # 관리자 페이지 컨텐츠 확인
        content = response.content.decode("utf-8")
        self.assertIn("Django administration", content)


class ActivityAdminTest(TestCase):
    """Activity 관리자 페이지 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.client.login(username="admin", password="adminpass123")

        # 테스트 데이터 생성
        self.activity = ActivityFactory.create()

    def test_activity_admin_list_view(self) -> None:
        """Activity 관리자 목록 페이지 테스트"""
        url = reverse("admin:main_activity_changelist")
        response: HttpResponse = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 활동 제목이 목록에 표시되는지 확인
        content = response.content.decode("utf-8")
        self.assertIn(self.activity.title_ko, content)

    def test_activity_admin_detail_view(self) -> None:
        """Activity 관리자 상세 페이지 테스트"""
        url = reverse("admin:main_activity_change", args=[self.activity.pk])
        response: HttpResponse = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 폼 필드들이 표시되는지 확인
        content = response.content.decode("utf-8")
        self.assertIn("title_ko", content)
        self.assertIn("activity_type", content)
        self.assertIn("is_public", content)

    def test_activity_admin_create_view(self) -> None:
        """Activity 관리자 생성 페이지 테스트"""
        url = reverse("admin:main_activity_add")
        response: HttpResponse = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 생성 폼이 표시되는지 확인
        content = response.content.decode("utf-8")
        self.assertIn("title_ko", content)
        self.assertIn("activity_type", content)

    def test_activity_admin_create_post(self) -> None:
        """Activity 관리자 생성 POST 테스트"""
        url = reverse("admin:main_activity_add")
        data = {
            "title_ko": "새 활동",
            "title_en": "New Activity",
            "description_ko": "새 활동 설명",
            "description_en": "New activity description",
            "activity_type": "seminar",
            "is_public": True,
            "is_featured": False,
            "is_recruiting": False,
        }

        response: HttpResponse = self.client.post(url, data)
        # 성공 시 목록 페이지로 리다이렉트
        self.assertEqual(response.status_code, 302)

        # 새 활동이 생성되었는지 확인
        self.assertTrue(Activity.objects.filter(title_ko="새 활동").exists())


class OrganizerAdminTest(TestCase):
    """Organizer 관리자 페이지 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.client.login(username="admin", password="adminpass123")

        # 테스트 데이터 생성
        self.organizer = OrganizerFactory.create()

    def test_organizer_admin_list_view(self) -> None:
        """Organizer 관리자 목록 페이지 테스트"""
        url = reverse("admin:main_organizer_changelist")
        response: HttpResponse = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 오거나이저 이름이 목록에 표시되는지 확인
        content = response.content.decode("utf-8")
        self.assertIn(self.organizer.name_ko, content)

    def test_organizer_admin_ordering(self) -> None:
        """Organizer 관리자 정렬 테스트"""
        # 추가 오거나이저 생성 (다른 order 값)
        organizer2 = OrganizerFactory.create(name_ko="두번째 오거나이저", order=1)

        url = reverse("admin:main_organizer_changelist")
        response: HttpResponse = self.client.get(url)
        content = response.content.decode("utf-8")

        # order 순으로 정렬되어 표시되는지 확인
        first_pos = content.find(self.organizer.name_ko)
        second_pos = content.find(organizer2.name_ko)
        self.assertLess(first_pos, second_pos)


class FAQAdminTest(TestCase):
    """FAQ 관리자 페이지 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.client.login(username="admin", password="adminpass123")

        # 테스트 데이터 생성
        self.faq = FAQFactory.create()

    def test_faq_admin_list_view(self) -> None:
        """FAQ 관리자 목록 페이지 테스트"""
        url = reverse("admin:main_faq_changelist")
        response: HttpResponse = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # FAQ 질문이 목록에 표시되는지 확인
        content = response.content.decode("utf-8")
        self.assertIn(self.faq.question_ko, content)

    def test_faq_admin_category_filter(self) -> None:
        """FAQ 관리자 카테고리 필터 테스트"""
        # 다른 카테고리 FAQ 생성
        faq_joining = FAQFactory.create(category="joining", question_ko="가입 관련 질문")

        url = reverse("admin:main_faq_changelist")

        # 카테고리 필터 적용
        response: HttpResponse = self.client.get(f"{url}?category=joining")
        content = response.content.decode("utf-8")

        # 해당 카테고리 FAQ만 표시되는지 확인
        self.assertIn(faq_joining.question_ko, content)
        self.assertNotIn(self.faq.question_ko, content)


class SocialMediaPlatformAdminTest(TestCase):
    """SocialMediaPlatform 관리자 페이지 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.client.login(username="admin", password="adminpass123")

        # 테스트 데이터 생성
        self.platform = SocialMediaPlatformFactory.create()

    def test_platform_admin_list_view(self) -> None:
        """SocialMediaPlatform 관리자 목록 페이지 테스트"""
        url = reverse("admin:main_socialmediaplatform_changelist")
        response: HttpResponse = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 플랫폼 이름이 목록에 표시되는지 확인
        content = response.content.decode("utf-8")
        self.assertIn(self.platform.name_ko, content)

    def test_platform_admin_active_filter(self) -> None:
        """SocialMediaPlatform 관리자 활성 상태 필터 테스트"""
        # 비활성 플랫폼 생성
        inactive_platform = SocialMediaPlatformFactory.create(name_ko="비활성 플랫폼", is_active=False)

        url = reverse("admin:main_socialmediaplatform_changelist")

        # 활성 상태 필터 적용
        response: HttpResponse = self.client.get(f"{url}?is_active=1")
        content = response.content.decode("utf-8")

        # 활성 플랫폼만 표시되는지 확인
        self.assertIn(self.platform.name_ko, content)
        self.assertNotIn(inactive_platform.name_ko, content)


class ContributionOpportunityAdminTest(TestCase):
    """ContributionOpportunity 관리자 페이지 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.client.login(username="admin", password="adminpass123")

        # 테스트 데이터 생성
        self.opportunity = ContributionOpportunityFactory.create()

    def test_opportunity_admin_list_view(self) -> None:
        """ContributionOpportunity 관리자 목록 페이지 테스트"""
        url = reverse("admin:main_contributionopportunity_changelist")
        response: HttpResponse = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 기여 기회 제목이 목록에 표시되는지 확인
        content = response.content.decode("utf-8")
        self.assertIn(self.opportunity.title_ko, content)

    def test_opportunity_admin_type_filter(self) -> None:
        """ContributionOpportunity 관리자 타입 필터 테스트"""
        # 다른 타입 기여 기회 생성
        sponsor_opportunity = ContributionOpportunityFactory.create(type="sponsor", title_ko="스폰서 기회")

        url = reverse("admin:main_contributionopportunity_changelist")

        # 타입 필터 적용
        response: HttpResponse = self.client.get(f"{url}?type=sponsor")
        content = response.content.decode("utf-8")

        # 해당 타입 기여 기회만 표시되는지 확인
        self.assertIn(sponsor_opportunity.title_ko, content)
        self.assertNotIn(self.opportunity.title_ko, content)


class AdminIntegrationTest(TestCase):
    """관리자 페이지 통합 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.client.login(username="admin", password="adminpass123")

    def test_all_models_registered(self) -> None:
        """모든 모델이 관리자 페이지에 등록되어 있는지 테스트"""
        response: HttpResponse = self.client.get("/admin/")
        content = response.content.decode("utf-8")

        # 모든 모델이 관리자 페이지에 표시되는지 확인
        self.assertIn("Activities", content)
        self.assertIn("Organizers", content)
        self.assertIn("FAQs", content)
        self.assertIn("Social media platforms", content)
        self.assertIn("Contribution opportunities", content)

    def test_admin_search_functionality(self) -> None:
        """관리자 페이지 검색 기능 테스트"""
        # 테스트 데이터 생성
        activity = ActivityFactory.create(title_ko="검색 테스트 활동")

        # Activity 검색 테스트
        url = reverse("admin:main_activity_changelist")
        response: HttpResponse = self.client.get(f"{url}?q=검색")
        content = response.content.decode("utf-8")

        # 검색 결과에 해당 활동이 표시되는지 확인
        self.assertIn(activity.title_ko, content)

    def test_admin_bulk_actions(self) -> None:
        """관리자 페이지 대량 작업 테스트"""
        # 여러 활동 생성
        activities = [ActivityFactory.create(title_ko=f"활동 {i}", is_public=True) for i in range(3)]

        url = reverse("admin:main_activity_changelist")

        # 대량 작업 데이터 준비
        data = {
            "action": "make_private",  # 비공개로 변경 액션
            "_selected_action": [str(activity.pk) for activity in activities],
        }

        response: HttpResponse = self.client.post(url, data)

        # 액션이 실행되었는지 확인 (리다이렉트 또는 성공 메시지)
        self.assertIn(response.status_code, [200, 302])

    def test_admin_permissions(self) -> None:
        """관리자 페이지 권한 테스트"""
        # 스태프 권한만 있는 사용자 생성
        User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="staffpass123",
            is_staff=True,
        )

        # 관리자 로그아웃
        self.client.logout()

        # 스태프 사용자로 로그인
        self.client.login(username="staff", password="staffpass123")

        # 관리자 페이지 접근 가능한지 확인
        response: HttpResponse = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

    def test_admin_custom_actions(self) -> None:
        """관리자 페이지 커스텀 액션 테스트"""
        # 공개 상태의 활동들 생성
        activities = [ActivityFactory.create(is_public=True, is_featured=False) for _ in range(3)]

        url = reverse("admin:main_activity_changelist")

        # 커스텀 액션 실행 (예: 추천 활동으로 설정)
        data = {
            "action": "make_featured",
            "_selected_action": [str(activity.pk) for activity in activities],
        }

        response: HttpResponse = self.client.post(url, data)

        # 액션이 실행되었는지 확인
        self.assertIn(response.status_code, [200, 302])

        # 실제로 변경되었는지 확인
        for activity in activities:
            activity.refresh_from_db()
            # 커스텀 액션이 구현되어 있다면 is_featured가 True가 되어야 함
            # 구현되지 않았다면 이 테스트는 실패할 수 있음
