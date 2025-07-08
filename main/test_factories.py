"""
테스트 데이터 생성을 위한 Factory Boy 팩토리 클래스들
"""

from datetime import timedelta
from typing import Any

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from .models import FAQ, Activity, ContributionOpportunity, Organizer, SocialMediaPlatform


class ActivityFactory(DjangoModelFactory):
    """Activity 모델 팩토리"""

    class Meta:
        model = Activity

    title_ko = "파이썬 세미나"
    title_en = "Python Seminar"
    description_ko = "파이썬 기초부터 심화까지 다루는 세미나입니다."
    description_en = "A seminar covering Python from basics to advanced topics."
    activity_type = "seminar"
    start_datetime = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    end_datetime = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7, hours=2))
    location_name_ko = "강남역 세미나실"
    location_name_en = "Gangnam Station Seminar Room"
    location_address = "서울시 강남구 강남대로 123"
    location_url = "https://example.com/location"
    meeting_schedule_ko = ""
    meeting_schedule_en = ""
    is_recruiting = False
    is_public = True
    is_featured = False

    @classmethod
    def create_study_group(cls, **kwargs: Any) -> Activity:
        """스터디그룹 생성"""
        study_defaults = {
            "activity_type": "study_group",
            "start_datetime": None,
            "end_datetime": None,
            "location_name_ko": "",
            "location_name_en": "",
            "location_address": "",
            "location_url": "",
            "meeting_schedule_ko": "매주 화요일 오후 7시",
            "meeting_schedule_en": "Every Tuesday 7PM",
            "is_recruiting": True,
        }
        study_defaults.update(kwargs)
        return cls.create(**study_defaults)


class OrganizerFactory(DjangoModelFactory):
    """Organizer 모델 팩토리"""

    class Meta:
        model = Organizer

    name_ko = factory.Sequence(lambda n: f"김파이썬{n}")
    name_en = factory.Sequence(lambda n: f"Python Kim{n}")
    role_ko = "리드 오거나이저"
    role_en = "Lead Organizer"
    bio_ko = "파이썬 개발자로 5년간 활동하고 있습니다."
    bio_en = "Python developer with 5 years of experience."
    email = factory.Sequence(lambda n: f"organizer{n}@pyladies.com")
    github = factory.LazyAttribute(lambda obj: (f"https://github.com/{obj.name_en.lower().replace(' ', '')}"))
    linkedin = factory.LazyAttribute(lambda obj: (f"https://linkedin.com/in/{obj.name_en.lower().replace(' ', '')}"))
    order = factory.Sequence(lambda n: n)
    is_public = True


class FAQFactory(DjangoModelFactory):
    """FAQ 모델 팩토리"""

    class Meta:
        model = FAQ

    category = factory.Iterator(["general", "joining", "participation"])
    question_ko = factory.Sequence(lambda n: f"질문 {n}")
    question_en = factory.Sequence(lambda n: f"Question {n}")
    answer_ko = factory.Sequence(lambda n: f"답변 {n}")
    answer_en = factory.Sequence(lambda n: f"Answer {n}")
    order = factory.Sequence(lambda n: n)
    is_public = True


class SocialMediaPlatformFactory(DjangoModelFactory):
    """SocialMediaPlatform 모델 팩토리"""

    class Meta:
        model = SocialMediaPlatform

    name_ko = factory.Iterator(["디스코드", "슬랙", "카카오톡", "텔레그램"])
    name_en = factory.Iterator(["Discord", "Slack", "KakaoTalk", "Telegram"])
    url = factory.Sequence(lambda n: f"https://discord.gg/pyladies-seoul-{n}")
    icon_class = factory.Iterator(
        [
            "fab fa-discord",
            "fab fa-slack",
            "fas fa-comment",
            "fab fa-telegram",
        ]
    )
    order = factory.Sequence(lambda n: n)
    is_active = True


class ContributionOpportunityFactory(DjangoModelFactory):
    """ContributionOpportunity 모델 팩토리"""

    class Meta:
        model = ContributionOpportunity

    type = factory.Iterator(["speaker", "volunteer", "mentor", "sponsor"])
    title_ko = factory.Iterator(
        [
            "발표자 모집",
            "자원봉사자 모집",
            "멘토 모집",
            "스폰서 모집",
        ]
    )
    title_en = factory.Iterator(
        [
            "Speaker Recruitment",
            "Volunteer Recruitment",
            "Mentor Recruitment",
            "Sponsor Recruitment",
        ]
    )
    description_ko = factory.LazyAttribute(lambda obj: f"{obj.title_ko}에 대한 상세 설명입니다.")
    description_en = factory.LazyAttribute(lambda obj: f"Detailed description for {obj.title_en}.")
    requirements_ko = "관련 경험 1년 이상"
    requirements_en = "More than 1 year of relevant experience"
    contact_method_ko = "이메일로 연락주세요: seoul@pyladies.com"
    contact_method_en = "Please contact us via email: seoul@pyladies.com"
    order = factory.Sequence(lambda n: n)
    is_open = True
    is_public = True


# 편의 함수들
def create_sample_activities(count: int = 3) -> list[Activity]:
    """샘플 활동 생성"""
    return ActivityFactory.create_batch(
        count,
        title_ko=factory.Sequence(lambda n: f"파이썬 세미나 {n+1}"),
        title_en=factory.Sequence(lambda n: f"Python Seminar {n+1}"),
        start_datetime=factory.Sequence(lambda n: timezone.now() + timedelta(days=n * 7)),
        end_datetime=factory.Sequence(lambda n: timezone.now() + timedelta(days=n * 7, hours=2)),
    )


def create_sample_organizers(count: int = 3) -> list[Organizer]:
    """샘플 오거나이저 생성"""
    return OrganizerFactory.create_batch(count)


def create_sample_faqs(count: int = 3) -> list[FAQ]:
    """샘플 FAQ 생성"""
    return FAQFactory.create_batch(count)
