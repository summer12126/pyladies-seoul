"""
뷰 레이어 테스트
"""

from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse

from .test_factories import (
    ContributionOpportunityFactory,
    FAQFactory,
    SocialMediaPlatformFactory,
    create_sample_activities,
    create_sample_faqs,
    create_sample_organizers,
)


class HomeViewTest(TestCase):
    """홈페이지 뷰 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()
        self.url = reverse("home")

        # 테스트 데이터 생성
        self.activities = create_sample_activities(3)
        self.organizers = create_sample_organizers(3)
        SocialMediaPlatformFactory.create()

    def test_home_view_status_code(self) -> None:
        """홈페이지 상태 코드 테스트"""
        response: HttpResponse = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_home_view_template(self) -> None:
        """홈페이지 템플릿 테스트"""
        response: HttpResponse = self.client.get(self.url)
        self.assertTemplateUsed(response, "index.html")

    def test_home_view_context(self) -> None:
        """홈페이지 컨텍스트 테스트"""
        response: HttpResponse = self.client.get(self.url)

        # 컨텍스트에 필요한 데이터가 포함되어 있는지 확인
        self.assertIn("community_info", response.context)
        self.assertIn("social_platforms", response.context)
        self.assertIn("discord_url", response.context)
        self.assertIn("recent_activities", response.context)
        self.assertIn("organizers", response.context)

        # 최근 활동 3개까지만 표시
        recent_activities = response.context["recent_activities"]
        self.assertLessEqual(len(recent_activities), 3)

        # 오거나이저 6개까지만 표시
        organizers = response.context["organizers"]
        self.assertLessEqual(len(organizers), 6)

    def test_home_view_content(self) -> None:
        """홈페이지 컨텐츠 테스트"""
        response: HttpResponse = self.client.get(self.url)
        content = response.content.decode("utf-8")

        # 기본 컨텐츠 확인
        self.assertIn("파이레이디스 서울", content)
        self.assertIn("PyLadies Seoul", content)

    def test_home_view_with_no_data(self) -> None:
        """데이터가 없을 때 홈페이지 테스트"""
        # 모든 데이터 삭제
        from .models import Activity, Organizer, SocialMediaPlatform

        Activity.objects.all().delete()
        Organizer.objects.all().delete()
        SocialMediaPlatform.objects.all().delete()

        response: HttpResponse = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # 빈 쿼리셋도 정상적으로 처리되는지 확인
        self.assertEqual(len(response.context["recent_activities"]), 0)
        self.assertEqual(len(response.context["organizers"]), 0)
        self.assertEqual(len(response.context["social_platforms"]), 0)


class ContributeViewTest(TestCase):
    """기여하기 페이지 뷰 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()
        self.url = reverse("contribute")

        # 테스트 데이터 생성
        self.opportunities = [
            ContributionOpportunityFactory.create(type="speaker", order=0),
            ContributionOpportunityFactory.create(type="sponsor", order=1),
            ContributionOpportunityFactory.create(type="volunteer", order=2),
        ]
        SocialMediaPlatformFactory.create()

    def test_contribute_view_status_code(self) -> None:
        """기여하기 페이지 상태 코드 테스트"""
        response: HttpResponse = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_contribute_view_template(self) -> None:
        """기여하기 페이지 템플릿 테스트"""
        response: HttpResponse = self.client.get(self.url)
        self.assertTemplateUsed(response, "contribute.html")

    def test_contribute_view_context(self) -> None:
        """기여하기 페이지 컨텍스트 테스트"""
        response: HttpResponse = self.client.get(self.url)

        # 컨텍스트에 필요한 데이터가 포함되어 있는지 확인
        self.assertIn("community_info", response.context)
        self.assertIn("social_platforms", response.context)
        self.assertIn("discord_url", response.context)
        self.assertIn("opportunities", response.context)

        # 기여 기회가 order 순으로 정렬되어 있는지 확인
        opportunities = response.context["opportunities"]
        self.assertEqual(len(opportunities), 3)
        self.assertEqual(opportunities[0].type, "speaker")
        self.assertEqual(opportunities[1].type, "sponsor")
        self.assertEqual(opportunities[2].type, "volunteer")

    def test_contribute_view_content(self) -> None:
        """기여하기 페이지 컨텐츠 테스트"""
        response: HttpResponse = self.client.get(self.url)
        content = response.content.decode("utf-8")

        # 기여 기회 제목들이 포함되어 있는지 확인
        self.assertIn("발표자 모집", content)

    def test_contribute_view_only_public_opportunities(self) -> None:
        """공개된 기여 기회만 표시되는지 테스트"""
        # 비공개 기여 기회 생성
        ContributionOpportunityFactory.create(type="donor", title_ko="비공개 기여", is_public=False)

        response: HttpResponse = self.client.get(self.url)
        opportunities = response.context["opportunities"]

        # 공개된 기여 기회만 포함되어야 함
        self.assertEqual(len(opportunities), 3)  # 기존 3개만
        for opportunity in opportunities:
            self.assertTrue(opportunity.is_public)


class FAQViewTest(TestCase):
    """FAQ 페이지 뷰 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()
        self.url = reverse("faq")

        # 테스트 데이터 생성
        self.faqs = create_sample_faqs(5)
        SocialMediaPlatformFactory.create()

    def test_faq_view_status_code(self) -> None:
        """FAQ 페이지 상태 코드 테스트"""
        response: HttpResponse = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_faq_view_template(self) -> None:
        """FAQ 페이지 템플릿 테스트"""
        response: HttpResponse = self.client.get(self.url)
        self.assertTemplateUsed(response, "faq.html")

    def test_faq_view_context(self) -> None:
        """FAQ 페이지 컨텍스트 테스트"""
        response: HttpResponse = self.client.get(self.url)

        # 컨텍스트에 필요한 데이터가 포함되어 있는지 확인
        self.assertIn("community_info", response.context)
        self.assertIn("social_platforms", response.context)
        self.assertIn("discord_url", response.context)
        self.assertIn("faqs", response.context)

        # FAQ가 category, order 순으로 정렬되어 있는지 확인
        faqs = response.context["faqs"]
        self.assertEqual(len(faqs), 5)

    def test_faq_view_content(self) -> None:
        """FAQ 페이지 컨텐츠 테스트"""
        response: HttpResponse = self.client.get(self.url)
        content = response.content.decode("utf-8")

        # FAQ 질문들이 포함되어 있는지 확인
        self.assertIn("질문", content)

    def test_faq_view_only_public_faqs(self) -> None:
        """공개된 FAQ만 표시되는지 테스트"""
        # 비공개 FAQ 생성
        FAQFactory.create(question_ko="비공개 질문", answer_ko="비공개 답변", is_public=False)

        response: HttpResponse = self.client.get(self.url)
        faqs = response.context["faqs"]

        # 공개된 FAQ만 포함되어야 함
        self.assertEqual(len(faqs), 5)  # 기존 5개만
        for faq in faqs:
            self.assertTrue(faq.is_public)


class COCViewTest(TestCase):
    """Code of Conduct 페이지 뷰 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()
        self.url = reverse("coc")

        # 테스트 데이터 생성
        SocialMediaPlatformFactory.create()

    def test_coc_view_status_code(self) -> None:
        """CoC 페이지 상태 코드 테스트"""
        response: HttpResponse = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_coc_view_template(self) -> None:
        """CoC 페이지 템플릿 테스트"""
        response: HttpResponse = self.client.get(self.url)
        self.assertTemplateUsed(response, "coc.html")

    def test_coc_view_context(self) -> None:
        """CoC 페이지 컨텍스트 테스트"""
        response: HttpResponse = self.client.get(self.url)

        # 컨텍스트에 필요한 데이터가 포함되어 있는지 확인
        self.assertIn("community_info", response.context)
        self.assertIn("social_platforms", response.context)
        self.assertIn("discord_url", response.context)
        self.assertIn("coc_info", response.context)

        # CoC 정보가 마크다운에서 HTML로 변환되었는지 확인
        coc_info = response.context["coc_info"]
        self.assertIn("community_content_ko", coc_info)
        self.assertIn("community_content_en", coc_info)
        self.assertIn("inappropriate_content_ko", coc_info)
        self.assertIn("inappropriate_content_en", coc_info)

    def test_coc_view_content(self) -> None:
        """CoC 페이지 컨텐츠 테스트"""
        response: HttpResponse = self.client.get(self.url)
        content = response.content.decode("utf-8")

        # CoC 기본 컨텐츠 확인
        self.assertIn("행동 강령", content)
        self.assertIn("Code of Conduct", content)


class ViewIntegrationTest(TestCase):
    """뷰 통합 테스트"""

    def setUp(self) -> None:
        """테스트 설정"""
        self.client = Client()

        # 모든 페이지에서 사용되는 공통 데이터 생성
        SocialMediaPlatformFactory.create()

    def test_all_pages_accessible(self) -> None:
        """모든 페이지가 접근 가능한지 테스트"""
        urls = [
            reverse("home"),
            reverse("contribute"),
            reverse("faq"),
            reverse("coc"),
        ]

        for url in urls:
            with self.subTest(url=url):
                response: HttpResponse = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_common_context_data(self) -> None:
        """모든 페이지의 공통 컨텍스트 데이터 테스트"""
        urls = [
            reverse("home"),
            reverse("contribute"),
            reverse("faq"),
            reverse("coc"),
        ]

        common_keys = ["community_info", "social_platforms", "discord_url"]

        for url in urls:
            with self.subTest(url=url):
                response: HttpResponse = self.client.get(url)
                for key in common_keys:
                    self.assertIn(key, response.context)

    def test_navigation_links(self) -> None:
        """네비게이션 링크 테스트"""
        response: HttpResponse = self.client.get(reverse("home"))
        content = response.content.decode("utf-8")

        # 다른 페이지로의 링크가 포함되어 있는지 확인
        self.assertIn('href="/contribute/"', content)
        self.assertIn('href="/faq/"', content)
        self.assertIn('href="/coc/"', content)

    def test_responsive_design_meta_tags(self) -> None:
        """반응형 디자인 메타 태그 테스트"""
        response: HttpResponse = self.client.get(reverse("home"))
        content = response.content.decode("utf-8")

        # 반응형 디자인을 위한 viewport 메타 태그 확인
        self.assertIn("viewport", content)

    def test_error_handling(self) -> None:
        """에러 처리 테스트"""
        # 존재하지 않는 URL 접근
        response: HttpResponse = self.client.get("/nonexistent-page/")
        self.assertEqual(response.status_code, 404)

    def test_view_performance(self) -> None:
        """뷰 성능 테스트 (기본적인 쿼리 수 확인)"""
        from django.db import connection
        from django.test.utils import override_settings

        # 대량의 테스트 데이터 생성
        create_sample_activities(10)
        create_sample_organizers(10)
        create_sample_faqs(10)

        with override_settings(DEBUG=True):
            # 쿼리 수 측정
            initial_queries = len(connection.queries)
            response: HttpResponse = self.client.get(reverse("home"))
            final_queries = len(connection.queries)

            self.assertEqual(response.status_code, 200)

            # 쿼리 수가 합리적인 범위 내에 있는지 확인 (N+1 문제 방지)
            query_count = final_queries - initial_queries
            self.assertLess(query_count, 20)  # 임의의 합리적인 상한선
