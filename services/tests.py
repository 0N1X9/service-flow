"""
Test suite for services app.
Covers: create, update, delete, and status changes.
"""

from django.contrib.auth.models import User
from django.test import Client as TestClient
from django.test import TestCase
from django.urls import reverse

from core.models import BusinessProfile
from clients.models import Client

from .models import ServiceRequest


class ServiceCreateTests(TestCase):
    """Tests for service request creation functionality."""

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
        self.client = Client.objects.create(
            name="Test Client",
            business=self.business,
        )
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_service_create_page_loads(self):
        """Test that service creation page loads."""
        response = self.client_tester.get(reverse("services:add"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/service_form.html")

    def test_create_service_with_required_fields(self):
        """Test creating a service with only required fields."""
        data = {
            "client": self.client.pk,
            "title": "Fix Plumbing",
            "description": "Repair the kitchen sink",
            "status": "NEW",
        }
        response = self.client_tester.post(reverse("services:add"), data)
        self.assertEqual(response.status_code, 302)
        service = ServiceRequest.objects.get(title="Fix Plumbing")
        self.assertEqual(service.client, self.client)
        self.assertEqual(service.status, "NEW")

    def test_create_service_with_estimated_price(self):
        """Test creating a service with estimated price."""
        data = {
            "client": self.client.pk,
            "title": "Electrical Work",
            "description": "Install new outlet",
            "status": "NEW",
            "estimated_price": "150.00",
        }
        response = self.client_tester.post(reverse("services:add"), data)
        self.assertEqual(response.status_code, 302)
        service = ServiceRequest.objects.get(title="Electrical Work")
        self.assertEqual(float(service.estimated_price), 150.00)

    def test_create_service_default_status_is_new(self):
        """Test that newly created service has NEW status."""
        data = {
            "client": self.client.pk,
            "title": "New Service",
            "description": "A new service",
            "status": "NEW",
        }
        self.client_tester.post(reverse("services:add"), data)
        service = ServiceRequest.objects.get(title="New Service")
        self.assertEqual(service.status, "NEW")

    def test_create_service_shows_success_message(self):
        """Test that success message is shown after creation."""
        data = {
            "client": self.client.pk,
            "title": "Success Service",
            "description": "Created successfully",
            "status": "NEW",
        }
        response = self.client_tester.post(
            reverse("services:add"), data, follow=True
        )
        messages = list(response.context["messages"])
        self.assertTrue(any("Job created successfully." in str(m) for m in messages))

    def test_create_service_without_title_fails(self):
        """Test that creating service without title fails."""
        data = {
            "client": self.client.pk,
            "description": "No title provided",
        }
        response = self.client_tester.post(reverse("services:add"), data)
        self.assertEqual(response.status_code, 200)

    def test_create_service_without_description_fails(self):
        """Test that creating service without description fails."""
        data = {
            "client": self.client.pk,
            "title": "No Description",
        }
        response = self.client_tester.post(reverse("services:add"), data)
        self.assertEqual(response.status_code, 200)

    def test_create_service_only_shows_user_clients(self):
        """Test that create form only shows user's own clients."""
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
        response = self.client_tester.get(reverse("services:add"))
        form_clients = response.context["form"].fields["client"].queryset
        self.assertIn(self.client, form_clients)
        self.assertNotIn(client2, form_clients)

    def test_unauthenticated_user_cannot_create_service(self):
        """Test that unauthenticated user cannot create a service."""
        self.client_tester.logout()
        response = self.client_tester.get(reverse("services:add"), follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])


class ServiceReadTests(TestCase):
    """Tests for service list functionality."""

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
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="TestPassword123!",
        )
        self.business2 = BusinessProfile.objects.get(
            user=self.user2
        )
        self.client = Client.objects.create(
            name="Test Client",
            business=self.business,
        )
        self.client2 = Client.objects.create(
            name="Other Client",
            business=self.business2,
        )
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_service_list_page_loads(self):
        """Test that service list page loads."""
        response = self.client_tester.get(reverse("services:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/service_list.html")

    def test_service_list_shows_user_services(self):
        """Test that service list shows only user's services."""
        service1 = ServiceRequest.objects.create(
            client=self.client,
            title="Service 1",
            description="Desc 1",
        )
        service2 = ServiceRequest.objects.create(
            client=self.client,
            title="Service 2",
            description="Desc 2",
        )
        response = self.client_tester.get(reverse("services:list"))
        self.assertContains(response, "Service 1")
        self.assertContains(response, "Service 2")

    def test_service_list_does_not_show_other_users_services(self):
        """Test that service list doesn't show other users' services."""
        other_service = ServiceRequest.objects.create(
            client=self.client2,
            title="Other Service",
            description="Not visible",
        )
        response = self.client_tester.get(reverse("services:list"))
        self.assertNotContains(response, "Other Service")

    def test_service_list_sorted_by_created_at_descending(self):
        """Test that services are sorted by created_at in descending order."""
        service1 = ServiceRequest.objects.create(
            client=self.client,
            title="Service 1",
            description="Desc 1",
        )
        service2 = ServiceRequest.objects.create(
            client=self.client,
            title="Service 2",
            description="Desc 2",
        )
        response = self.client_tester.get(reverse("services:list"))
        services = response.context["services"]
        self.assertEqual(services[0].title, "Service 2")
        self.assertEqual(services[1].title, "Service 1")

    def test_empty_service_list(self):
        """Test that empty service list displays correctly."""
        response = self.client_tester.get(reverse("services:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["services"]), 0)

    def test_unauthenticated_user_cannot_access_service_list(self):
        """Test that unauthenticated user cannot access service list."""
        self.client_tester.logout()
        response = self.client_tester.get(reverse("services:list"), follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])


class ServiceUpdateTests(TestCase):
    """Tests for service update functionality."""

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
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="TestPassword123!",
        )
        self.business2 = BusinessProfile.objects.get(
            user=self.user2
        )
        self.client = Client.objects.create(
            name="Test Client",
            business=self.business,
        )
        self.client2 = Client.objects.create(
            name="Other Client",
            business=self.business2,
        )
        self.service = ServiceRequest.objects.create(
            client=self.client,
            title="Original Service",
            description="Original description",
        )
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_service_update_page_loads(self):
        """Test that service update page loads."""
        url = reverse("services:edit", kwargs={"pk": self.service.pk})
        response = self.client_tester.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/service_form.html")

    def test_update_service_title(self):
        """Test updating service title."""
        url = reverse("services:edit", kwargs={"pk": self.service.pk})
        data = {
            "client": self.client.pk,
            "title": "Updated Title",
            "description": self.service.description,
            "status": self.service.status,
        }
        response = self.client_tester.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.service.refresh_from_db()
        self.assertEqual(self.service.title, "Updated Title")

    def test_update_service_description(self):
        """Test updating service description."""
        url = reverse("services:edit", kwargs={"pk": self.service.pk})
        data = {
            "client": self.client.pk,
            "title": self.service.title,
            "description": "New description",
            "status": self.service.status,
        }
        response = self.client_tester.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.service.refresh_from_db()
        self.assertEqual(self.service.description, "New description")

    def test_update_service_estimated_price(self):
        """Test updating service estimated price."""
        url = reverse("services:edit", kwargs={"pk": self.service.pk})
        data = {
            "client": self.client.pk,
            "title": self.service.title,
            "description": self.service.description,
            "status": self.service.status,
            "estimated_price": "500",
        }
        response = self.client_tester.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.service.refresh_from_db()
        self.assertEqual(float(self.service.estimated_price), 500)

    def test_update_service_shows_success_message(self):
        """Test that success message is shown after update."""
        url = reverse("services:edit", kwargs={"pk": self.service.pk})
        data = {
            "client": self.client.pk,
            "title": "Updated",
            "description": "Updated",
            "status": self.service.status,
        }
        response = self.client_tester.post(url, data, follow=True)
        messages = list(response.context["messages"])
        self.assertTrue(any("Job updated successfully." in str(m) for m in messages))

    def test_cannot_update_other_users_service(self):
        """Test that user cannot update another user's service."""
        other_service = ServiceRequest.objects.create(
            client=self.client2,
            title="Other Service",
            description="Other",
        )
        url = reverse("services:edit", kwargs={"pk": other_service.pk})
        response = self.client_tester.get(url, follow=False)
        self.assertEqual(response.status_code, 404)

    def test_update_service_only_shows_user_clients(self):
        """Test that update form only shows user's own clients."""
        url = reverse("services:edit", kwargs={"pk": self.service.pk})
        response = self.client_tester.get(url)
        form_clients = response.context["form"].fields["client"].queryset
        self.assertIn(self.client, form_clients)
        self.assertNotIn(self.client2, form_clients)

    def test_unauthenticated_user_cannot_update_service(self):
        """Test that unauthenticated user cannot update a service."""
        self.client_tester.logout()
        url = reverse("services:edit", kwargs={"pk": self.service.pk})
        response = self.client_tester.get(url, follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])


class ServiceDeleteTests(TestCase):
    """Tests for service delete functionality."""

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
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="TestPassword123!",
        )
        self.business2 = BusinessProfile.objects.get(
            user=self.user2
        )
        self.client = Client.objects.create(
            name="Test Client",
            business=self.business,
        )
        self.client2 = Client.objects.create(
            name="Other Client",
            business=self.business2,
        )
        self.service = ServiceRequest.objects.create(
            client=self.client,
            title="Service to Delete",
            description="Will be deleted",
        )
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_service_delete_page_loads(self):
        """Test that service delete confirmation page loads."""
        url = reverse("services:delete", kwargs={"pk": self.service.pk})
        response = self.client_tester.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services/service_confirm_delete.html")

    def test_delete_service(self):
        """Test deleting a service."""
        service_id = self.service.pk
        url = reverse("services:delete", kwargs={"pk": service_id})
        response = self.client_tester.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ServiceRequest.objects.filter(pk=service_id).exists())

    def test_delete_service_shows_success_message(self):
        """Test that success message is shown after deletion."""
        url = reverse("services:delete", kwargs={"pk": self.service.pk})
        response = self.client_tester.post(url, follow=True)
        messages = list(response.context["messages"])
        self.assertTrue(any("deleted successfully" in str(m) for m in messages))

    def test_cannot_delete_other_users_service(self):
        """Test that user cannot delete another user's service."""
        other_service = ServiceRequest.objects.create(
            client=self.client2,
            title="Other Service",
            description="Other",
        )
        url = reverse("services:delete", kwargs={"pk": other_service.pk})
        response = self.client_tester.get(url, follow=False)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(ServiceRequest.objects.filter(pk=other_service.pk).exists())

    def test_unauthenticated_user_cannot_delete_service(self):
        """Test that unauthenticated user cannot delete a service."""
        self.client_tester.logout()
        url = reverse("services:delete", kwargs={"pk": self.service.pk})
        response = self.client_tester.get(url, follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])


class ServiceStatusChangeTests(TestCase):
    """Tests for service status transitions."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
        )
        self.business = BusinessProfile.objects.get(
            user=self.user
        )
        self.client = Client.objects.create(
            name="Test Client",
            business=self.business,
        )
        self.service = ServiceRequest.objects.create(
            client=self.client,
            title="Test Service",
            description="Test",
        )

    def test_new_service_has_new_status(self):
        """Test that newly created service has NEW status."""
        self.assertEqual(self.service.status, "NEW")

    def test_service_status_choices_exist(self):
        """Test that all expected status choices exist."""
        status_choices = dict(ServiceRequest.STATUS_CHOICES)
        self.assertIn("NEW", status_choices)
        self.assertIn("QUOTED", status_choices)
        self.assertIn("SCHEDULED", status_choices)
        self.assertIn("IN_PROGRESS", status_choices)
        self.assertIn("COMPLETED", status_choices)
        self.assertIn("CANCELLED", status_choices)

    def test_change_status_to_quoted(self):
        """Test changing service status to QUOTED."""
        self.service.status = "QUOTED"
        self.service.save()
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "QUOTED")

    def test_change_status_to_scheduled(self):
        """Test changing service status to SCHEDULED."""
        self.service.status = "SCHEDULED"
        self.service.save()
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "SCHEDULED")

    def test_change_status_to_in_progress(self):
        """Test changing service status to IN_PROGRESS."""
        self.service.status = "IN_PROGRESS"
        self.service.save()
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "IN_PROGRESS")

    def test_change_status_to_completed(self):
        """Test changing service status to COMPLETED."""
        self.service.status = "COMPLETED"
        self.service.save()
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "COMPLETED")

    def test_change_status_to_cancelled(self):
        """Test changing service status to CANCELLED."""
        self.service.status = "CANCELLED"
        self.service.save()
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "CANCELLED")

    def test_status_persists_after_update(self):
        """Test that status persists when service is updated."""
        self.service.status = "QUOTED"
        self.service.save()
        self.service.title = "Updated Title"
        self.service.save()
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "QUOTED")

    def test_updating_relevant_fields_marks_quote_outdated(self):
        """Test that updating relevant fields marks associated quote as outdated."""
        from quotes.models import Quote

        # Create a quote for the service
        quote = Quote.objects.create(
            service_request=self.service,
            content="Test quote",
            is_outdated=False,
        )
        
        # Update a relevant field
        self.service.title = "New Title"
        self.service.save()
        
        # Check that quote is marked outdated
        quote.refresh_from_db()
        self.assertTrue(quote.is_outdated)

    def test_multiple_status_transitions(self):
        """Test multiple status transitions in sequence."""
        transitions = ["QUOTED", "SCHEDULED", "IN_PROGRESS", "COMPLETED"]
        for status in transitions:
            self.service.status = status
            self.service.save()
            self.service.refresh_from_db()
            self.assertEqual(self.service.status, status)
