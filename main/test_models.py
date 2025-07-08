"""
모델 레이어 테스트
"""

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import FAQ, Activity, ContributionOpportunity, Organizer, SocialMediaPlatform
from .test_factories import (
    ActivityFactory,
    ContributionOpportunityFactory,
    FAQFactory,
    OrganizerFactory,
    SocialMediaPlatformFactory,
)


class ActivityModelTest(TestCase):
    """Activity 모델 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.activity = ActivityFactory.create()

    def test_activity_creation(self) -> None:
        """Activity 생성 테스트"""
        self.assertIsInstance(self.activity, Activity)
        self.assertEqual(self.activity.title_ko, "파이썬 세미나")
        self.assertEqual(self.activity.activity_type, "seminar")
        self.assertTrue(self.activity.is_public)
        self.assertFalse(self.activity.is_featured)

    def test_activity_str_representation(self) -> None:
        """Activity __str__ 메서드 테스트"""
        expected = f"{self.activity.get_activity_type_display()} - " f"{self.activity.title_ko}"
        self.assertEqual(str(self.activity), expected)

    def test_activity_is_event_property(self) -> None:
        """Activity is_event 속성 테스트"""
        # 세미나는 이벤트
        self.assertTrue(self.activity.is_event)

        # 스터디그룹은 이벤트가 아님
        study_group = ActivityFactory.create_study_group()
        self.assertFalse(study_group.is_event)

    def test_activity_is_study_group_property(self) -> None:
        """Activity is_study_group 속성 테스트"""
        # 세미나는 스터디그룹이 아님
        self.assertFalse(self.activity.is_study_group)

        # 스터디그룹은 스터디그룹
        study_group = ActivityFactory.create_study_group()
        self.assertTrue(study_group.is_study_group)

    def test_activity_date_property(self) -> None:
        """Activity date 속성 테스트 (하위 호환성)"""
        self.assertEqual(self.activity.date, self.activity.start_datetime)

    def test_activity_location_properties(self) -> None:
        """Activity location 속성들 테스트 (하위 호환성)"""
        self.assertEqual(self.activity.location_ko, self.activity.location_name_ko)
        self.assertEqual(self.activity.location_en, self.activity.location_name_en)

    def test_activity_ordering(self) -> None:
        """Activity 정렬 테스트"""
        # 미래 활동들 생성
        future_activity = ActivityFactory.create(
            title_ko="미래 세미나",
            start_datetime=timezone.now() + timedelta(days=14),
        )

        # 가장 최근 start_datetime 순으로 정렬되어야 함
        activities = Activity.objects.all()
        self.assertEqual(activities.first(), future_activity)

    def test_study_group_creation(self) -> None:
        """스터디그룹 생성 테스트"""
        study_group = ActivityFactory.create_study_group(
            title_ko="파이썬 스터디",
            meeting_schedule_ko="매주 수요일 오후 8시",
        )

        self.assertEqual(study_group.activity_type, "study_group")
        self.assertEqual(study_group.meeting_schedule_ko, "매주 수요일 오후 8시")
        self.assertTrue(study_group.is_recruiting)
        self.assertIsNone(study_group.start_datetime)
        self.assertIsNone(study_group.end_datetime)


class OrganizerModelTest(TestCase):
    """Organizer 모델 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.organizer = OrganizerFactory.create()

    def test_organizer_creation(self) -> None:
        """Organizer 생성 테스트"""
        self.assertIsInstance(self.organizer, Organizer)
        self.assertTrue(self.organizer.name_ko.startswith("김파이썬"))
        self.assertEqual(self.organizer.role_ko, "리드 오거나이저")
        self.assertTrue(self.organizer.is_public)

    def test_organizer_str_representation(self) -> None:
        """Organizer __str__ 메서드 테스트"""
        expected = f"{self.organizer.name_ko} ({self.organizer.role_ko})"
        self.assertEqual(str(self.organizer), expected)

    def test_organizer_ordering(self) -> None:
        """Organizer 정렬 테스트"""
        organizer2 = OrganizerFactory.create(name_ko="이파이썬", order=1)
        organizer3 = OrganizerFactory.create(name_ko="박파이썬", order=2)

        organizers = Organizer.objects.all()
        self.assertEqual(organizers[0], self.organizer)  # order=0
        self.assertEqual(organizers[1], organizer2)  # order=1
        self.assertEqual(organizers[2], organizer3)  # order=2

    def test_organizer_email_validation(self) -> None:
        """Organizer 이메일 유효성 검사 테스트"""
        # 유효한 이메일
        organizer = OrganizerFactory.build(email="test@example.com")
        organizer.full_clean()  # 유효성 검사 실행

        # 잘못된 이메일 형식은 Django에서 자동으로 검증됨
        with self.assertRaises(ValidationError):
            organizer = OrganizerFactory.build(email="invalid-email")
            organizer.full_clean()


class FAQModelTest(TestCase):
    """FAQ 모델 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.faq = FAQFactory.create()

    def test_faq_creation(self) -> None:
        """FAQ 생성 테스트"""
        self.assertIsInstance(self.faq, FAQ)
        categories = ["general", "joining", "participation"]
        self.assertIn(self.faq.category, categories)
        self.assertTrue(self.faq.question_ko.startswith("질문"))
        self.assertTrue(self.faq.is_public)

    def test_faq_str_representation(self) -> None:
        """FAQ __str__ 메서드 테스트"""
        expected = f"{self.faq.get_category_display()} - {self.faq.question_ko}"
        self.assertEqual(str(self.faq), expected)

    def test_faq_ordering(self) -> None:
        """FAQ 정렬 테스트"""
        FAQFactory.create(category="joining", question_ko="가입 방법", order=0)
        FAQFactory.create(category="general", question_ko="일반 질문", order=1)

        faqs = FAQ.objects.all()
        # category 먼저, 그 다음 order 순으로 정렬
        self.assertEqual(faqs[0].category, "general")
        self.assertEqual(faqs[1].category, "general")
        self.assertEqual(faqs[2].category, "joining")

    def test_faq_categories(self) -> None:
        """FAQ 카테고리 테스트"""
        categories = [
            "general",
            "joining",
            "participation",
            "technical",
            "contact",
        ]

        for category in categories:
            faq = FAQFactory.create(category=category)
            self.assertEqual(faq.category, category)
            self.assertIn(category, dict(FAQ.FAQ_CATEGORIES))


class SocialMediaPlatformModelTest(TestCase):
    """SocialMediaPlatform 모델 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.platform = SocialMediaPlatformFactory.create()

    def test_platform_creation(self) -> None:
        """SocialMediaPlatform 생성 테스트"""
        self.assertIsInstance(self.platform, SocialMediaPlatform)
        self.assertEqual(self.platform.name_ko, "디스코드")
        self.assertEqual(self.platform.name_en, "Discord")
        self.assertTrue(self.platform.is_active)

    def test_platform_str_representation(self) -> None:
        """SocialMediaPlatform __str__ 메서드 테스트"""
        self.assertEqual(str(self.platform), self.platform.name_ko)

    def test_platform_ordering(self) -> None:
        """SocialMediaPlatform 정렬 테스트"""
        platform2 = SocialMediaPlatformFactory.create(name_ko="깃허브", order=1)
        platform3 = SocialMediaPlatformFactory.create(name_ko="슬랙", order=2)

        platforms = SocialMediaPlatform.objects.all()
        self.assertEqual(platforms[0], self.platform)  # order=0
        self.assertEqual(platforms[1], platform2)  # order=1
        self.assertEqual(platforms[2], platform3)  # order=2

    def test_platform_url_validation(self) -> None:
        """SocialMediaPlatform URL 유효성 검사 테스트"""
        # 유효한 URL
        platform = SocialMediaPlatformFactory.build(url="https://discord.gg/pyladies")
        platform.full_clean()

        # 잘못된 URL 형식
        with self.assertRaises(ValidationError):
            platform = SocialMediaPlatformFactory.build(url="invalid-url")
            platform.full_clean()


class ContributionOpportunityModelTest(TestCase):
    """ContributionOpportunity 모델 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.opportunity = ContributionOpportunityFactory.create()

    def test_opportunity_creation(self) -> None:
        """ContributionOpportunity 생성 테스트"""
        self.assertIsInstance(self.opportunity, ContributionOpportunity)
        self.assertEqual(self.opportunity.type, "speaker")
        self.assertEqual(self.opportunity.title_ko, "발표자 모집")
        self.assertTrue(self.opportunity.is_open)
        self.assertTrue(self.opportunity.is_public)

    def test_opportunity_str_representation(self) -> None:
        """ContributionOpportunity __str__ 메서드 테스트"""
        expected = f"{self.opportunity.get_type_display()} - " f"{self.opportunity.title_ko}"
        self.assertEqual(str(self.opportunity), expected)

    def test_opportunity_ordering(self) -> None:
        """ContributionOpportunity 정렬 테스트"""
        opportunity2 = ContributionOpportunityFactory.create(type="sponsor", title_ko="스폰서 모집", order=1)

        opportunities = ContributionOpportunity.objects.all()
        self.assertEqual(opportunities[0], self.opportunity)  # order=0
        self.assertEqual(opportunities[1], opportunity2)  # order=1

    def test_opportunity_types(self) -> None:
        """ContributionOpportunity 타입 테스트"""
        types = [
            "maker",
            "speaker",
            "study_leader",
            "sponsor",
            "volunteer",
            "donor",
            "other",
        ]

        for opportunity_type in types:
            opportunity = ContributionOpportunityFactory.create(type=opportunity_type)
            self.assertEqual(opportunity.type, opportunity_type)
            self.assertIn(
                opportunity_type,
                dict(ContributionOpportunity.OPPORTUNITY_TYPES),
            )


class ModelIntegrationTest(TestCase):
    """모델 통합 테스트"""

    def test_model_relationships(self) -> None:
        """모델 간 관계 테스트"""
        # 모든 모델 생성
        ActivityFactory.create()
        OrganizerFactory.create()
        FAQFactory.create()
        SocialMediaPlatformFactory.create()
        ContributionOpportunityFactory.create()

        # 모든 모델이 정상적으로 생성되었는지 확인
        self.assertEqual(Activity.objects.count(), 1)
        self.assertEqual(Organizer.objects.count(), 1)
        self.assertEqual(FAQ.objects.count(), 1)
        self.assertEqual(SocialMediaPlatform.objects.count(), 1)
        self.assertEqual(ContributionOpportunity.objects.count(), 1)

    def test_model_timestamps(self) -> None:
        """모델 타임스탬프 테스트"""
        activity = ActivityFactory.create()

        # created와 modified 필드가 자동으로 설정되는지 확인
        self.assertIsNotNone(activity.created)
        self.assertIsNotNone(activity.modified)

        # 수정 시 modified 필드가 업데이트되는지 확인
        original_modified = activity.modified
        activity.title_ko = "수정된 제목"
        activity.save()

        activity.refresh_from_db()
        self.assertGreater(activity.modified, original_modified)

    def test_model_soft_deletion(self) -> None:
        """모델 소프트 삭제 테스트 (is_public 필드 활용)"""
        activity = ActivityFactory.create(is_public=True)
        organizer = OrganizerFactory.create(is_public=True)
        faq = FAQFactory.create(is_public=True)

        # 공개 상태에서 조회 가능
        self.assertEqual(Activity.objects.filter(is_public=True).count(), 1)
        self.assertEqual(Organizer.objects.filter(is_public=True).count(), 1)
        self.assertEqual(FAQ.objects.filter(is_public=True).count(), 1)

        # 비공개로 변경 (소프트 삭제)
        activity.is_public = False
        organizer.is_public = False
        faq.is_public = False

        activity.save()
        organizer.save()
        faq.save()

        # 공개 상태에서 조회 불가
        self.assertEqual(Activity.objects.filter(is_public=True).count(), 0)
        self.assertEqual(Organizer.objects.filter(is_public=True).count(), 0)
        self.assertEqual(FAQ.objects.filter(is_public=True).count(), 0)

        # 전체 조회에서는 여전히 존재
        self.assertEqual(Activity.objects.count(), 1)
        self.assertEqual(Organizer.objects.count(), 1)
        self.assertEqual(FAQ.objects.count(), 1)
