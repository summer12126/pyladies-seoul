from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import FAQ, Activity, ActivityPublication, ContributionOpportunity, Organizer, SocialMediaPlatform


class ActivityPublicationInline(admin.TabularInline):
    model = ActivityPublication
    extra = 1
    autocomplete_fields = ("platform",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "title_ko",
        "activity_type",
        "start_datetime",
        "end_datetime",
        "is_recruiting",
        "is_public",
        "is_featured",
    )
    list_filter = (
        "activity_type",
        "is_public",
        "is_featured",
        "is_recruiting",
        "start_datetime",
    )
    search_fields = (
        "title_ko",
        "title_en",
        "description_ko",
        "description_en",
        "location_name_ko",
        "location_name_en",
    )
    date_hierarchy = "start_datetime"
    inlines = [ActivityPublicationInline]

    fieldsets = (
        (
            "기본 정보",
            {
                "fields": (
                    "title_ko",
                    "title_en",
                    "description_ko",
                    "description_en",
                    "activity_type",
                    "image",
                )
            },
        ),
        (
            "이벤트 정보",
            {
                "fields": (
                    "start_datetime",
                    "end_datetime",
                    "location_name_ko",
                    "location_name_en",
                    "location_address",
                    "location_url",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "스터디그룹 정보",
            {
                "fields": (
                    "meeting_schedule_ko",
                    "meeting_schedule_en",
                    "is_recruiting",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "공개 설정",
            {
                "fields": ("is_public", "is_featured"),
            },
        ),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Activity]:
        """QuerySet을 최적화"""
        return super().get_queryset(request).select_related()


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = (
        "name_ko",
        "name_en",
        "role_ko",
        "role_en",
        "order",
        "is_public",
    )
    list_filter = ("is_public",)
    search_fields = ("name_ko", "name_en", "role_ko", "role_en")
    ordering = ("order", "name_ko")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = (
        "question_ko",
        "question_en",
        "category",
        "order",
        "is_public",
    )
    list_filter = ("category", "is_public")
    search_fields = ("question_ko", "question_en", "answer_ko", "answer_en")
    ordering = ("category", "order")


@admin.register(SocialMediaPlatform)
class SocialMediaPlatformAdmin(admin.ModelAdmin):
    list_display = (
        "name_ko",
        "url",
        "link_type",
        "order",
        "is_active",
        "modified",
    )
    list_filter = ("is_active", "link_type")
    search_fields = ("name_ko", "name_en")
    list_editable = ("link_type", "order", "is_active")
    ordering = ("order", "name_ko")

    fieldsets = (
        (None, {"fields": ("name_ko", "name_en", "url", "link_type")}),
        (
            _("표시 설정"),
            {"fields": ("icon", "icon_class", "order", "is_active")},
        ),
    )


@admin.register(ContributionOpportunity)
class ContributionOpportunityAdmin(admin.ModelAdmin):
    list_display = (
        "title_ko",
        "type",
        "order",
        "is_open",
        "is_public",
        "modified",
    )
    list_filter = ("type", "is_open", "is_public")
    search_fields = (
        "title_ko",
        "title_en",
        "description_ko",
        "description_en",
    )
    list_editable = ("order", "is_open", "is_public")
    ordering = ("order", "type")

    fieldsets = (
        (None, {"fields": ("type", "title_ko", "title_en")}),
        (_("설명"), {"fields": ("description_ko", "description_en")}),
        (
            _("요구사항"),
            {
                "fields": ("requirements_ko", "requirements_en"),
                "classes": ("collapse",),
            },
        ),
        (
            _("연락 방법"),
            {"fields": ("contact_method_ko", "contact_method_en")},
        ),
        (_("설정"), {"fields": ("order", "is_open", "is_public")}),
    )
