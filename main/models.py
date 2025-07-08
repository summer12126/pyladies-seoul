from datetime import datetime
from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel


class ActivityType(models.TextChoices):
    SEMINAR = "seminar", _("세미나")
    WORKSHOP = "workshop", _("워크숍")
    MEETUP = "meetup", _("밋업")
    NETWORKING = "networking", _("네트워킹")
    STUDY_GROUP = "study_group", _("스터디그룹")


class Activity(TimeStampedModel):
    """통합된 활동 모델 (이벤트 + 스터디그룹)"""

    # 공통 필드들
    title_ko = models.CharField(
        max_length=200,
        verbose_name=_("제목 (한국어)"),
        db_comment="Activity title in Korean",
    )
    title_en = models.CharField(
        max_length=200,
        verbose_name=_("제목 (영어)"),
        db_comment="Activity title in English",
    )
    description_ko = models.TextField(
        verbose_name=_("설명 (한국어)"),
        db_comment="Activity detailed description in Korean",
    )
    description_en = models.TextField(
        verbose_name=_("설명 (영어)"),
        db_comment="Activity detailed description in English",
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
        default=ActivityType.SEMINAR,
        verbose_name=_("활동 유형"),
        db_comment="Activity type (seminar, workshop, meetup, networking, " "study_group)",
    )

    # 이벤트용 필드들 (일회성 활동)
    start_datetime = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("시작 일시"),
        db_comment="Event start date and time",
    )
    end_datetime = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("종료 일시"),
        db_comment="Event end date and time",
    )
    location_name_ko = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("장소명 (한국어)"),
        db_comment="Event location name in Korean",
    )
    location_name_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("장소명 (영어)"),
        db_comment="Event location name in English",
    )
    location_address = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("장소 주소"),
        db_comment="Event location detailed address",
    )
    location_url = models.URLField(
        blank=True,
        verbose_name=_("장소 URL"),
        db_comment="Online event URL or location-related link",
    )

    # 스터디그룹용 필드들 (지속적 활동)
    meeting_schedule_ko = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("정기 모임 일정 (한국어)"),
        db_comment="Study group regular meeting schedule in Korean",
        help_text=_("예: 매주 화요일 오후 7시"),
    )
    meeting_schedule_en = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("정기 모임 일정 (영어)"),
        db_comment="Study group regular meeting schedule in English",
        help_text=_("예: Every Tuesday 7PM"),
    )
    is_recruiting = models.BooleanField(
        default=False,
        verbose_name=_("모집 중"),
        db_comment="Whether study group is recruiting members",
    )

    # 공통 메타 필드들
    image = models.ImageField(
        upload_to="activities/",
        blank=True,
        null=True,
        verbose_name=_("대표 이미지"),
        db_comment="Activity representative image",
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_("공개 여부"),
        db_comment="Whether activity is public",
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("추천 활동"),
        db_comment="Whether activity is featured on main page",
    )

    published_on: models.ManyToManyField = models.ManyToManyField(
        "SocialMediaPlatform",
        through="ActivityPublication",
        related_name="published_activities",
        verbose_name=_("발행된 플랫폼"),
    )

    class Meta:
        ordering = ["-start_datetime", "-created"]
        verbose_name = _("활동")
        verbose_name_plural = _("활동")
        db_table_comment = "PyLadies Seoul activities (events and study groups)"

    def __str__(self) -> str:
        return f"{self.get_activity_type_display()} - {self.title_ko}"

    @property
    def is_event(self) -> bool:
        """일회성 이벤트인지 확인"""
        return self.activity_type in [
            ActivityType.SEMINAR,
            ActivityType.WORKSHOP,
            ActivityType.MEETUP,
            ActivityType.NETWORKING,
        ]

    @property
    def is_study_group(self) -> bool:
        """스터디그룹인지 확인"""
        return self.activity_type == ActivityType.STUDY_GROUP

    @property
    def date(self) -> Optional[datetime]:
        """하위 호환성을 위한 date 속성 (start_datetime와 동일)"""
        return self.start_datetime

    @property
    def location_ko(self) -> str:
        """하위 호환성을 위한 location_ko 속성"""
        return self.location_name_ko

    @property
    def location_en(self) -> str:
        """하위 호환성을 위한 location_en 속성"""
        return self.location_name_en


class Organizer(TimeStampedModel):
    name_ko = models.CharField(
        max_length=100,
        verbose_name=_("이름 (한국어)"),
        db_comment="Organizer name in Korean",
    )
    name_en = models.CharField(
        max_length=100,
        verbose_name=_("이름 (영어)"),
        db_comment="Organizer name in English",
    )
    role_ko = models.CharField(
        max_length=100,
        verbose_name=_("역할 (한국어)"),
        db_comment="Organizer role in Korean",
    )
    role_en = models.CharField(
        max_length=100,
        verbose_name=_("역할 (영어)"),
        db_comment="Organizer role in English",
    )
    bio_ko = models.TextField(
        blank=True,
        verbose_name=_("소개 (한국어)"),
        db_comment="Organizer bio in Korean",
    )
    bio_en = models.TextField(
        blank=True,
        verbose_name=_("소개 (영어)"),
        db_comment="Organizer bio in English",
    )
    photo = models.ImageField(
        upload_to="organizers/",
        blank=True,
        null=True,
        verbose_name=_("프로필 사진"),
        db_comment="Organizer profile photo",
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_("이메일"),
        db_comment="Organizer contact email",
    )
    github = models.URLField(
        blank=True,
        verbose_name=_("GitHub URL"),
        db_comment="Organizer GitHub profile URL",
    )
    linkedin = models.URLField(
        blank=True,
        verbose_name=_("LinkedIn URL"),
        db_comment="Organizer LinkedIn profile URL",
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("표시 순서"),
        db_comment="Display order of organizer",
        help_text=_("표시 순서"),
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_("공개 여부"),
        db_comment="Whether organizer is public",
    )

    class Meta:
        ordering = ["order", "name_ko"]
        verbose_name = _("오거나이저")
        verbose_name_plural = _("오거나이저")
        db_table_comment = "PyLadies Seoul organizer information"

    def __str__(self) -> str:
        return f"{self.name_ko} ({self.role_ko})"


class FAQ(TimeStampedModel):
    FAQ_CATEGORIES = [
        ("general", _("일반")),
        ("joining", _("참여")),
        ("participation", _("활동")),
        ("technical", _("기술")),
        ("contact", _("연락처")),
    ]

    category = models.CharField(
        max_length=20,
        choices=FAQ_CATEGORIES,
        default="general",
        verbose_name=_("카테고리"),
        db_comment="FAQ category",
    )
    question_ko = models.CharField(
        max_length=200,
        verbose_name=_("질문 (한국어)"),
        db_comment="FAQ question in Korean",
    )
    question_en = models.CharField(
        max_length=200,
        verbose_name=_("질문 (영어)"),
        db_comment="FAQ question in English",
    )
    answer_ko = models.TextField(
        verbose_name=_("답변 (한국어)"),
        db_comment="FAQ answer in Korean",
    )
    answer_en = models.TextField(
        verbose_name=_("답변 (영어)"),
        db_comment="FAQ answer in English",
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("표시 순서"),
        db_comment="Display order of FAQ",
        help_text=_("표시 순서"),
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_("공개 여부"),
        db_comment="Whether FAQ is public",
    )

    class Meta:
        ordering = ["category", "order"]
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQ")
        db_table_comment = "PyLadies Seoul frequently asked questions"

    def __str__(self) -> str:
        return f"{self.get_category_display()} - {self.question_ko}"


class LinkType(models.TextChoices):
    MAIN_CHANNEL = "main_channel", _("메인 채널")
    PUBLICATION_PLATFORM = "publication_platform", _("발행 플랫폼")


class SocialMediaPlatform(TimeStampedModel):
    """
    Social media platforms and external links for PyLadies Seoul.

    Manages various social media platforms and external services
    with their URLs, icons, and display settings.
    """

    name_ko = models.CharField(
        max_length=100,
        verbose_name=_("플랫폼명 (한국어)"),
        db_comment="Platform name in Korean",
    )
    name_en = models.CharField(
        max_length=100,
        verbose_name=_("플랫폼명 (영어)"),
        db_comment="Platform name in English",
    )
    url = models.URLField(
        verbose_name=_("URL"),
        db_comment="Platform URL or invite link",
    )
    link_type = models.CharField(
        max_length=20,
        choices=LinkType.choices,
        default=LinkType.MAIN_CHANNEL,
        verbose_name=_("링크 유형"),
        db_comment="Type of the link (main channel or publication platform)",
    )
    icon = models.ImageField(
        upload_to="social_media/",
        blank=True,
        null=True,
        verbose_name=_("아이콘"),
        db_comment="Platform icon or logo",
    )
    icon_class = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("아이콘 CSS 클래스"),
        db_comment="CSS class for icon (e.g., Font Awesome class)",
        help_text=_("예: fab fa-discord, fab fa-github"),
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("표시 순서"),
        db_comment="Display order of platform",
        help_text=_("표시 순서"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("활성 상태"),
        db_comment="Whether platform is active and should be displayed",
    )

    class Meta:
        ordering = ["order", "name_ko"]
        verbose_name = _("소셜 미디어 플랫폼")
        verbose_name_plural = _("소셜 미디어 플랫폼")
        db_table_comment = "PyLadies Seoul social media platforms and external links"

    def __str__(self) -> str:
        return self.name_ko


class ActivityPublication(TimeStampedModel):
    """
    Connects an Activity to its publication on a social media platform.
    """

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="publications",
        verbose_name=_("활동"),
        db_comment="Reference to the activity",
    )
    platform = models.ForeignKey(
        SocialMediaPlatform,
        on_delete=models.CASCADE,
        verbose_name=_("플랫폼"),
        db_comment="Reference to the social media platform",
        limit_choices_to={"link_type": LinkType.PUBLICATION_PLATFORM},
    )
    publication_url = models.URLField(
        verbose_name=_("게시물 URL"),
        db_comment="URL of the specific publication post",
    )
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("게시 일시"),
        db_comment="Date and time when the activity was published",
    )

    class Meta:
        ordering = ["-published_at", "platform__order"]
        verbose_name = _("활동 게시물")
        verbose_name_plural = _("활동 게시물")
        db_table_comment = "Links activities to their social media publications"
        unique_together = ("activity", "platform")

    def __str__(self) -> str:
        return f"{self.activity.title_ko} on {self.platform.name_ko}"


class ContributionOpportunity(TimeStampedModel):
    """
    Community contribution opportunities for PyLadies Seoul.

    Manages various ways people can contribute to the community
    including speaking, organizing, sponsoring, and volunteering.
    """

    OPPORTUNITY_TYPES = [
        ("maker", _("메이커")),
        ("speaker", _("스피커")),
        ("study_leader", _("스터디 리더")),
        ("sponsor", _("스폰서")),
        ("volunteer", _("봉사자")),
        ("donor", _("기부")),
        ("other", _("기타")),
    ]

    type = models.CharField(
        max_length=20,
        choices=OPPORTUNITY_TYPES,
        verbose_name=_("기여 유형"),
        db_comment="Contribution opportunity type",
    )
    title_ko = models.CharField(
        max_length=200,
        verbose_name=_("제목 (한국어)"),
        db_comment="Contribution opportunity title in Korean",
    )
    title_en = models.CharField(
        max_length=200,
        verbose_name=_("제목 (영어)"),
        db_comment="Contribution opportunity title in English",
    )
    description_ko = models.TextField(
        verbose_name=_("설명 (한국어)"),
        db_comment="Contribution opportunity description in Korean",
    )
    description_en = models.TextField(
        verbose_name=_("설명 (영어)"),
        db_comment="Contribution opportunity description in English",
    )
    requirements_ko = models.TextField(
        blank=True,
        verbose_name=_("요구사항 (한국어)"),
        db_comment="Contribution opportunity requirements in Korean",
    )
    requirements_en = models.TextField(
        blank=True,
        verbose_name=_("요구사항 (영어)"),
        db_comment="Contribution opportunity requirements in English",
    )
    contact_method_ko = models.TextField(
        verbose_name=_("연락 방법 (한국어)"),
        db_comment="Contribution opportunity contact method in Korean",
    )
    contact_method_en = models.TextField(
        verbose_name=_("연락 방법 (영어)"),
        db_comment="Contribution opportunity contact method in English",
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("표시 순서"),
        db_comment="Display order of contribution opportunity",
        help_text=_("표시 순서"),
    )
    is_open = models.BooleanField(
        default=True,
        verbose_name=_("모집 중"),
        db_comment="Whether contribution opportunity is open for recruitment",
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_("공개 여부"),
        db_comment="Whether contribution opportunity is public",
    )

    class Meta:
        ordering = ["order", "type", "title_ko"]
        verbose_name = _("기여 기회")
        verbose_name_plural = _("기여 기회")
        db_table_comment = "PyLadies Seoul community contribution " "opportunities"

    def __str__(self) -> str:
        return f"{self.get_type_display()} - {self.title_ko}"
