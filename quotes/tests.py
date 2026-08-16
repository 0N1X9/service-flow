"""
Test suite for quotes app.
Covers: generation, regeneration, and usage limits.
"""

from unittest.mock import patch, MagicMock
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import Client as TestClient
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import BusinessProfile
from clients.models import Client
from services.models import ServiceRequest
from payments.models import Subscription
from payments.services import FREE_MONTHLY_QUOTE_LIMIT, monthly_quote_count

from .models import Quote


class QuoteGenerationTests(TestCase):
    """Tests for quote generation functionality."""

    def setUp(self):
        self.client_tester = TestClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
        )
        self.business = BusinessProfile.objects.get(
            user=self.user
        )
        self.subscription = Subscription.objects.get(user=self.user)
        self.subscription.plan = "free"
        self.subscription.is_active = False
        self.subscription.save()
        self.client = Client.objects.create(
            name="Test Client",
            business=self.business,
        )
        self.service = ServiceRequest.objects.create(
            client=self.client,
            title="Test Service",
            description="Need a quote for this",
        )
        self.client_tester.login(username="testuser", password="TestPassword123!")

    @patch("quotes.views.generate_quote")
    def test_generate_quote_creates_quote(self, mock_generate):
        """Test that quote generation creates a quote."""
        mock_generate.return_value = MagicMock(
            content="Generated quote content",
            provider="test_provider",
        )
        url = reverse("quotes:generate", kwargs={"service_id": self.service.pk})
        response = self.client_tester.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Quote.objects.filter(
            service_request=self.service
        ).exists())

    @patch("quotes.views.generate_quote")
    def test_generate_quote_sets_content(self, mock_generate):
        """Test that generated quote has correct content."""
        expected_content = "Test quote content"
        mock_generate.return_value = MagicMock(
            content=expected_content,
            provider="test_provider",
        )
        url = reverse("quotes:generate", kwargs={"service_id": self.service.pk})
        self.client_tester.get(url)

        quote = Quote.objects.get(service_request=self.service)
        self.assertEqual(quote.content, expected_content)

    @patch("quotes.views.generate_quote")
    def test_generate_quote_sets_provider(self, mock_generate):
        """Test that generated quote has correct provider."""
        mock_generate.return_value = MagicMock(
            content="Content",
            provider="openai",
        )
        url = reverse("quotes:generate", kwargs={"service_id": self.service.pk})
        self.client_tester.get(url)

        quote = Quote.objects.get(service_request=self.service)
        self.assertEqual(quote.provider, "openai")

    @patch("quotes.views.generate_quote")
    def test_generate_quote_sets_price(self, mock_generate):
        """Test that generated quote uses service estimated price."""
        self.service.estimated_price = "500"
        self.service.save()

        mock_generate.return_value = MagicMock(
            content="Content",
            provider="test",
        )
        url = reverse("quotes:generate", kwargs={"service_id": self.service.pk})
        self.client_tester.get(url)

        quote = Quote.objects.get(service_request=self.service)
        self.assertEqual(float(quote.price), 500)

    @patch("quotes.views.generate_quote")
    def test_generate_quote_updates_service_status(self, mock_generate):
        """Test that quote generation updates service status to QUOTED."""
        mock_generate.return_value = MagicMock(
            content="Content",
            provider="test",
        )
        url = reverse("quotes:generate", kwargs={"service_id": self.service.pk})
        self.client_tester.get(url)

        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "QUOTED")

    @patch("quotes.views.generate_quote")
    def test_generate_quote_shows_success_message(self, mock_generate):
        """Test that success message is shown after generation."""
        mock_generate.return_value = MagicMock(
            content="Content",
            provider="test",
        )
        url = reverse("quotes:generate", kwargs={"service_id": self.service.pk})
        response = self.client_tester.get(url, follow=True)

        messages = list(response.context["messages"])
        self.assertTrue(any("generated successfully" in str(m) for m in messages))

    @patch("quotes.views.generate_quote")
    def test_generate_quote_not_outdated_after_generation(self, mock_generate):
        """Test that newly generated quote is not marked as outdated."""
        mock_generate.return_value = MagicMock(
            content="Content",
            provider="test",
        )
        url = reverse("quotes:generate", kwargs={"service_id": self.service.pk})
        self.client_tester.get(url)

        quote = Quote.objects.get(service_request=self.service)
        self.assertFalse(quote.is_outdated)

    @patch("quotes.views.generate_quote")
    def test_unauthenticated_user_cannot_generate_quote(self, mock_generate):
        """Test that unauthenticated user cannot generate quote."""
        self.client_tester.logout()
        url = reverse("quotes:generate", kwargs={"service_id": self.service.pk})
        response = self.client_tester.get(url, follow=False)

        self.assertIn(response.status_code, [301, 302, 303, 307, 308])

    @patch("quotes.views.generate_quote")
    def test_cannot_generate_quote_for_other_users_service(self, mock_generate):
        """Test that user cannot generate quote for another user's service."""
        user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="TestPassword123!",
        )
        business2 = BusinessProfile.objects.get(
            user=user2
        )
        client2 = Client.objects.create(
            name="Other Client",
            business=business2,
        )
        service2 = ServiceRequest.objects.create(
            client=client2,
            title="Other Service",
            description="Other",
        )

        url = reverse("quotes:generate", kwargs={"service_id": service2.pk})
        response = self.client_tester.get(url, follow=False)

        self.assertEqual(response.status_code, 404)


class QuoteRegenerationTests(TestCase):
    """Tests for quote regeneration functionality."""

    def setUp(self):
        self.client_tester = TestClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
        )
        self.business = BusinessProfile.objects.get(
            user=self.user
        )
        self.subscription = Subscription.objects.get(user=self.user)
        self.subscription.plan = "free"
        self.subscription.is_active = False
        self.subscription.save()
        self.client = Client.objects.create(
            name="Test Client",
            business=self.business,
        )
        self.service = ServiceRequest.objects.create(
            client=self.client,
            title="Test Service",
            description="Need a quote",
        )
        self.quote = Quote.objects.create(
            service_request=self.service,
            content="Original quote",
            provider="test",
        )
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_quote_detail_page_loads(self):
        """Test that quote detail page loads."""
        url = reverse("quotes:detail", kwargs={"pk": self.quote.pk})
        response = self.client_tester.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "quotes/quote_detail.html")

    def test_quote_detail_shows_quote_content(self):
        """Test that quote detail shows quote content."""
        url = reverse("quotes:detail", kwargs={"pk": self.quote.pk})
        response = self.client_tester.get(url)

        self.assertContains(response, "Original quote")

    @patch("quotes.views.generate_quote")
    def test_regenerate_quote_via_quote_generation(self, mock_generate):
        """Test that regenerating quote via quote generation updates existing quote."""
        new_content = "Regenerated quote"
        mock_generate.return_value = MagicMock(
            content=new_content,
            provider="test",
        )

        quote_id = self.quote.pk
        url = reverse("quotes:generate", kwargs={"service_id": self.service.pk})
        self.client_tester.get(url)

        quote = Quote.objects.get(pk=quote_id)
        self.assertEqual(quote.content, new_content)

    def test_edit_quote_content(self):
        """Test editing quote content."""
        url = reverse("quotes:detail", kwargs={"pk": self.quote.pk})
        data = {
            "content": "Edited quote content",
        }
        response = self.client_tester.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.content, "Edited quote content")

    def test_edit_quote_shows_success_message(self):
        """Test that success message is shown after editing quote."""
        url = reverse("quotes:detail", kwargs={"pk": self.quote.pk})
        data = {
            "content": "Edited content",
        }
        response = self.client_tester.post(url, data, follow=True)

        messages = list(response.context["messages"])
        self.assertTrue(any("updated successfully" in str(m) for m in messages))

    def test_cannot_edit_other_users_quote(self):
        """Test that user cannot edit another user's quote."""
        user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="TestPassword123!",
        )
        business2 = BusinessProfile.objects.get(
            user=user2
        )
        client2 = Client.objects.create(
            name="Other Client",
            business=business2,
        )
        service2 = ServiceRequest.objects.create(
            client=client2,
            title="Other Service",
            description="Other",
        )
        other_quote = Quote.objects.create(
            service_request=service2,
            content="Other quote",
        )

        url = reverse("quotes:detail", kwargs={"pk": other_quote.pk})
        response = self.client_tester.get(url, follow=False)

        self.assertEqual(response.status_code, 404)

    def test_quote_list_page_loads(self):
        """Test that quote list page loads."""
        response = self.client_tester.get(reverse("quotes:list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "quotes/quote_list.html")

    def test_quote_list_shows_user_quotes(self):
        """Test that quote list shows only user's quotes."""
        response = self.client_tester.get(reverse("quotes:list"))

        self.assertContains(response, self.quote.service_request.title)

    def test_quote_list_does_not_show_other_users_quotes(self):
        """Test that quote list doesn't show other users' quotes."""
        user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="TestPassword123!",
        )
        business2 = BusinessProfile.objects.get(
            user=user2
        )
        client2 = Client.objects.create(
            name="Other Client",
            business=business2,
        )
        service2 = ServiceRequest.objects.create(
            client=client2,
            title="Other Service",
            description="Other",
        )
        other_quote = Quote.objects.create(
            service_request=service2,
            content="Other quote",
        )

        response = self.client_tester.get(reverse("quotes:list"))

        self.assertNotContains(response, "Other Service")


class QuoteUsageLimitTests(TestCase):
    """Tests for quote generation usage limits."""

    def setUp(self):
        self.client_tester = TestClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
        )
        self.business = BusinessProfile.objects.get(
            user=self.user
        )
        self.subscription = Subscription.objects.get(user=self.user)
        self.subscription.plan = "free"
        self.subscription.is_active = False
        self.subscription.save()
        self.client = Client.objects.create(
            name="Test Client",
            business=self.business,
        )
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_free_user_has_monthly_limit(self):
        """Test that free users have a monthly quote limit."""
        # Create services and quotes for current month
        for i in range(FREE_MONTHLY_QUOTE_LIMIT):
            service = ServiceRequest.objects.create(
                client=self.client,
                title=f"Service {i}",
                description=f"Description {i}",
            )
            Quote.objects.create(
                service_request=service,
                content=f"Quote {i}",
            )

        # Check that limit is reached
        count = monthly_quote_count(self.user)
        self.assertEqual(count, FREE_MONTHLY_QUOTE_LIMIT)

    @patch("quotes.views.generate_quote")
    def test_free_user_cannot_exceed_monthly_limit(self, mock_generate):
        """Test that free user cannot exceed monthly quote limit."""
        from payments.services import can_generate_quote

        # Create quotes at the limit
        for i in range(FREE_MONTHLY_QUOTE_LIMIT):
            service = ServiceRequest.objects.create(
                client=self.client,
                title=f"Service {i}",
                description=f"Description {i}",
            )
            Quote.objects.create(
                service_request=service,
                content=f"Quote {i}",
            )

        # Try to generate another quote
        new_service = ServiceRequest.objects.create(
            client=self.client,
            title="Excess Service",
            description="Over limit",
        )

        can_gen = can_generate_quote(self.user)
        self.assertFalse(can_gen)

    @patch("quotes.views.generate_quote")
    def test_free_user_limit_exceeded_shows_upgrade_message(self, mock_generate):
        """Test that exceeding limit redirects to upgrade page."""
        # Create quotes at the limit
        for i in range(FREE_MONTHLY_QUOTE_LIMIT):
            service = ServiceRequest.objects.create(
                client=self.client,
                title=f"Service {i}",
                description=f"Description {i}",
            )
            Quote.objects.create(
                service_request=service,
                content=f"Quote {i}",
            )

        # Try to generate another quote
        new_service = ServiceRequest.objects.create(
            client=self.client,
            title="Excess Service",
            description="Over limit",
        )

        url = reverse("quotes:generate", kwargs={"service_id": new_service.pk})
        response = self.client_tester.get(url, follow=True)

        messages = list(response.context["messages"])
        self.assertTrue(any("reached your monthly AI quote limit" in str(m) for m in messages))

    def test_premium_user_has_unlimited_quotes(self):
        """Test that premium users have unlimited quotes."""
        from payments.services import can_generate_quote

        # Upgrade to premium
        self.subscription.plan = "premium"
        self.subscription.is_active = True
        self.subscription.save()

        # Create many quotes
        for i in range(FREE_MONTHLY_QUOTE_LIMIT + 10):
            service = ServiceRequest.objects.create(
                client=self.client,
                title=f"Service {i}",
                description=f"Description {i}",
            )
            Quote.objects.create(
                service_request=service,
                content=f"Quote {i}",
            )

        # Should still be able to generate
        can_gen = can_generate_quote(self.user)
        self.assertTrue(can_gen)

    def test_monthly_quote_count_resets_next_month(self):
        """Test that quote count resets for next month."""
        # Create a quote last month
        last_month = timezone.now() - timedelta(days=35)
        service1 = ServiceRequest.objects.create(
            client=self.client,
            title="Last Month Service",
            description="Old",
        )
        quote1 = Quote.objects.create(
            service_request=service1,
            content="Old quote",
        )
        quote1.created_at = last_month
        quote1.save()

        # Count should only include current month
        count = monthly_quote_count(self.user)
        self.assertEqual(count, 0)

    def test_multiple_quotes_in_same_month_count(self):
        """Test that multiple quotes in same month are counted."""
        for i in range(3):
            service = ServiceRequest.objects.create(
                client=self.client,
                title=f"Service {i}",
                description=f"Description {i}",
            )
            Quote.objects.create(
                service_request=service,
                content=f"Quote {i}",
            )

        count = monthly_quote_count(self.user)
        self.assertEqual(count, 3)

    def test_inactive_subscription_treated_as_free_tier(self):
        """Test that inactive subscription is treated as free tier."""
        from payments.services import is_premium

        self.subscription.is_active = False
        self.subscription.save()

        is_prem = is_premium(self.user)
        self.assertFalse(is_prem)

    def test_upgrade_page_shows_usage_stats(self):
        """Test that upgrade page shows quote usage statistics."""
        response = self.client_tester.get(reverse("payments:upgrade"))

        self.assertIn("used_quotes", response.context)
        self.assertIn("limit", response.context)
        self.assertIn("is_premium", response.context)
