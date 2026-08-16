"""
Test suite for payments app.
Covers: subscription management and premium behavior.
"""

from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import Client as TestClient
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import BusinessProfile
from clients.models import Client
from services.models import ServiceRequest
from quotes.models import Quote

from .models import Subscription
from .services import (
    is_premium,
    monthly_quote_count,
    can_generate_quote,
    FREE_MONTHLY_QUOTE_LIMIT,
)


class SubscriptionModelTests(TestCase):
    """Tests for Subscription model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
        )

    def test_create_subscription(self):
        """Test that the user already has a default free subscription."""
        subscription = Subscription.objects.get(user=self.user)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.plan, "free")
        self.assertFalse(subscription.is_active)

    def test_subscription_has_stripe_customer_id(self):
        """Test that subscription can have stripe customer ID."""
        subscription = Subscription.objects.get(user=self.user)
        subscription.plan = "premium"
        subscription.is_active = True
        subscription.stripe_customer_id = "cus_123456"
        subscription.save()
        self.assertEqual(subscription.stripe_customer_id, "cus_123456")

    def test_subscription_has_expiration_date(self):
        """Test that subscription can have expiration date."""
        future_date = timezone.now() + timedelta(days=30)
        subscription = Subscription.objects.get(user=self.user)
        subscription.plan = "premium"
        subscription.is_active = True
        subscription.expiration_date = future_date
        subscription.save()
        self.assertEqual(subscription.expiration_date, future_date)

    def test_subscription_one_to_one_relationship(self):
        """Test that each user has exactly one subscription record."""
        subscription = Subscription.objects.get(user=self.user)
        self.assertEqual(Subscription.objects.filter(user=self.user).count(), 1)
        self.assertEqual(subscription.user, self.user)

    def test_subscription_defaults_to_free_plan(self):
        """Test that the default stored plan is free."""
        subscription = Subscription.objects.get(user=self.user)
        self.assertEqual(subscription.plan, "free")

    def test_subscription_defaults_to_inactive(self):
        """Test that the default stored subscription is inactive."""
        subscription = Subscription.objects.get(user=self.user)
        self.assertFalse(subscription.is_active)


class PremiumBehaviorTests(TestCase):
    """Tests for premium subscription behavior."""

    def setUp(self):
        self.user_free = User.objects.create_user(
            username="freeuser",
            email="free@example.com",
            password="TestPassword123!",
        )
        self.sub_free = Subscription.objects.get(user=self.user_free)
        self.user_premium = User.objects.create_user(
            username="premiumuser",
            email="premium@example.com",
            password="TestPassword123!",
        )
        self.sub_premium = Subscription.objects.get(user=self.user_premium)
        self.sub_premium.plan = "premium"
        self.sub_premium.is_active = True
        self.sub_premium.save()

    def test_is_premium_returns_true_for_premium_user(self):
        """Test that is_premium returns True for premium users."""
        self.assertTrue(is_premium(self.user_premium))

    def test_is_premium_returns_false_for_free_user(self):
        """Test that is_premium returns False for free users."""
        self.assertFalse(is_premium(self.user_free))

    def test_is_premium_returns_false_for_inactive_premium(self):
        """Test that is_premium returns False for inactive premium subscription."""
        self.sub_premium.is_active = False
        self.sub_premium.save()
        self.assertFalse(is_premium(self.user_premium))

    def test_premium_user_can_generate_unlimited_quotes(self):
        """Test that premium user can generate unlimited quotes."""
        business = BusinessProfile.objects.get(
            user=self.user_premium
        )
        client = Client.objects.create(
            name="Client",
            business=business,
        )
        
        # Create many quotes
        for i in range(FREE_MONTHLY_QUOTE_LIMIT + 10):
            service = ServiceRequest.objects.create(
                client=client,
                title=f"Service {i}",
                description=f"Desc {i}",
            )
            Quote.objects.create(
                service_request=service,
                content=f"Quote {i}",
            )
        
        self.assertTrue(can_generate_quote(self.user_premium))

    def test_free_user_limited_to_monthly_quota(self):
        """Test that free user is limited to monthly quota."""
        business = BusinessProfile.objects.get(
            user=self.user_free
        )
        client = Client.objects.create(
            name="Client",
            business=business,
        )
        
        # Create quotes up to limit
        for i in range(FREE_MONTHLY_QUOTE_LIMIT):
            service = ServiceRequest.objects.create(
                client=client,
                title=f"Service {i}",
                description=f"Desc {i}",
            )
            Quote.objects.create(
                service_request=service,
                content=f"Quote {i}",
            )
        
        # Should be at limit now
        self.assertFalse(can_generate_quote(self.user_free))

    def test_free_user_can_generate_until_limit(self):
        """Test that free user can generate quotes until limit."""
        business = BusinessProfile.objects.get(
            user=self.user_free
        )
        client = Client.objects.create(
            name="Client",
            business=business,
        )
        
        # Create one quote
        service = ServiceRequest.objects.create(
            client=client,
            title="Service",
            description="Desc",
        )
        Quote.objects.create(
            service_request=service,
            content="Quote",
        )
        
        # Should still be able to generate
        self.assertTrue(can_generate_quote(self.user_free))


class UpgradePageTests(TestCase):
    """Tests for upgrade page and premium features."""

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
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_upgrade_page_loads(self):
        """Test that upgrade page loads."""
        response = self.client_tester.get(reverse("payments:upgrade"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payments/upgrade.html")

    def test_upgrade_page_shows_quote_usage(self):
        """Test that upgrade page shows quote usage statistics."""
        response = self.client_tester.get(reverse("payments:upgrade"))
        self.assertIn("used_quotes", response.context)
        self.assertEqual(response.context["used_quotes"], 0)

    def test_upgrade_page_shows_quote_limit(self):
        """Test that upgrade page shows quote limit."""
        response = self.client_tester.get(reverse("payments:upgrade"))
        self.assertIn("limit", response.context)
        self.assertEqual(response.context["limit"], FREE_MONTHLY_QUOTE_LIMIT)

    def test_upgrade_page_shows_premium_status(self):
        """Test that upgrade page shows premium status."""
        response = self.client_tester.get(reverse("payments:upgrade"))
        self.assertIn("is_premium", response.context)
        self.assertFalse(response.context["is_premium"])

    def test_upgrade_page_shows_correct_usage_with_quotes(self):
        """Test that upgrade page shows correct usage when quotes exist."""
        client = Client.objects.create(
            name="Client",
            business=self.business,
        )
        for i in range(2):
            service = ServiceRequest.objects.create(
                client=client,
                title=f"Service {i}",
                description=f"Desc {i}",
            )
            Quote.objects.create(
                service_request=service,
                content=f"Quote {i}",
            )
        
        response = self.client_tester.get(reverse("payments:upgrade"))
        self.assertEqual(response.context["used_quotes"], 2)

    def test_unauthenticated_user_cannot_access_upgrade_page(self):
        """Test that unauthenticated user cannot access upgrade page."""
        self.client_tester.logout()
        response = self.client_tester.get(reverse("payments:upgrade"), follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])


@patch("payments.stripe_service.stripe.checkout.Session.create")
class CheckoutTests(TestCase):
    """Tests for stripe checkout process."""

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
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_checkout_page_redirects(self, mock_checkout):
        """Test that checkout redirects to Stripe."""
        mock_checkout.return_value = MagicMock(url="https://checkout.stripe.com/test")
        response = self.client_tester.get(reverse("payments:checkout"), follow=False)
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_user_cannot_access_checkout(self, mock_checkout):
        """Test that unauthenticated user cannot access checkout."""
        self.client_tester.logout()
        response = self.client_tester.get(reverse("payments:checkout"), follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])


class SuccessAndCancelTests(TestCase):
    """Tests for checkout success and cancel pages."""

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
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_success_page_loads(self):
        """Test that success page loads after checkout."""
        response = self.client_tester.get(reverse("payments:success"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payments/success.html")

    def test_cancel_page_loads(self):
        """Test that cancel page loads when checkout is cancelled."""
        response = self.client_tester.get(reverse("payments:cancel"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payments/cancel.html")

    def test_unauthenticated_user_cannot_access_success_page(self):
        """Test that unauthenticated user cannot access success page."""
        self.client_tester.logout()
        response = self.client_tester.get(reverse("payments:success"), follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])

    def test_unauthenticated_user_cannot_access_cancel_page(self):
        """Test that unauthenticated user cannot access cancel page."""
        self.client_tester.logout()
        response = self.client_tester.get(reverse("payments:cancel"), follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])


class QuoteGenerationAccessControlTests(TestCase):
    """Tests for quote generation access control with premium features."""

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
            name="Client",
            business=self.business,
        )
        self.client_tester.login(username="testuser", password="TestPassword123!")

    @patch("quotes.views.generate_quote")
    def test_free_user_sees_upgrade_prompt_after_limit(self, mock_generate):
        """Test that free user sees upgrade prompt when limit is reached."""
        mock_generate.return_value = MagicMock(
            content="Quote",
            provider="test",
        )
        
        # Create quotes at limit
        for i in range(FREE_MONTHLY_QUOTE_LIMIT):
            service = ServiceRequest.objects.create(
                client=self.client,
                title=f"Service {i}",
                description=f"Desc {i}",
            )
            Quote.objects.create(
                service_request=service,
                content=f"Quote {i}",
            )
        
        # Try to generate another
        new_service = ServiceRequest.objects.create(
            client=self.client,
            title="Excess",
            description="Excess",
        )
        
        url = reverse("quotes:generate", kwargs={"service_id": new_service.pk})
        response = self.client_tester.get(url, follow=True)
        
        # Should be redirected to upgrade page
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.request["PATH_INFO"].endswith(reverse("payments:upgrade")))

    def test_premium_user_not_blocked_by_quote_limit(self):
        """Test that premium user is not blocked by quote limit."""
        # Upgrade to premium
        self.subscription.plan = "premium"
        self.subscription.is_active = True
        self.subscription.save()
        
        # Create many quotes
        for i in range(FREE_MONTHLY_QUOTE_LIMIT + 5):
            service = ServiceRequest.objects.create(
                client=self.client,
                title=f"Service {i}",
                description=f"Desc {i}",
            )
            Quote.objects.create(
                service_request=service,
                content=f"Quote {i}",
            )
        
        # Should still be able to generate
        can_gen = can_generate_quote(self.user)
        self.assertTrue(can_gen)
