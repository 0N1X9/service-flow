"""
Test suite for clients app.
Covers: create, read, update, delete, and ownership.
"""

from django.contrib.auth.models import User
from django.test import Client as TestClient
from django.test import TestCase
from django.urls import reverse

from core.models import BusinessProfile

from .models import Client


class ClientCreateTests(TestCase):
    """Tests for client creation functionality."""

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
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_client_create_page_loads(self):
        """Test that client creation page loads."""
        response = self.client_tester.get(reverse("clients:add"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "clients/client_form.html")

    def test_create_client_with_required_fields_only(self):
        """Test creating a client with only required fields."""
        data = {
            "name": "John Client",
        }
        response = self.client_tester.post(reverse("clients:add"), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Client.objects.filter(name="John Client").exists())

    def test_create_client_with_all_fields(self):
        """Test creating a client with all fields."""
        data = {
            "name": "Acme Corp",
            "email": "contact@acme.com",
            "phone": "555-1234",
            "company": "Acme Corporation",
            "notes": "VIP client",
        }
        response = self.client_tester.post(reverse("clients:add"), data)
        self.assertEqual(response.status_code, 302)
        client = Client.objects.get(name="Acme Corp")
        self.assertEqual(client.email, "contact@acme.com")
        self.assertEqual(client.phone, "555-1234")
        self.assertEqual(client.company, "Acme Corporation")
        self.assertEqual(client.notes, "VIP client")

    def test_create_client_associates_with_business(self):
        """Test that created client is associated with user's business."""
        data = {
            "name": "Test Client",
        }
        self.client_tester.post(reverse("clients:add"), data)
        client = Client.objects.get(name="Test Client")
        self.assertEqual(client.business, self.business)

    def test_create_client_with_valid_email(self):
        """Test creating a client with valid email."""
        data = {
            "name": "Email Client",
            "email": "valid@example.com",
        }
        response = self.client_tester.post(reverse("clients:add"), data)
        self.assertEqual(response.status_code, 302)
        client = Client.objects.get(name="Email Client")
        self.assertEqual(client.email, "valid@example.com")

    def test_create_client_with_invalid_email(self):
        """Test creating a client with invalid email format."""
        data = {
            "name": "Bad Email Client",
            "email": "not-an-email",
        }
        response = self.client_tester.post(reverse("clients:add"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Client.objects.filter(name="Bad Email Client").exists())

    def test_create_client_without_name_fails(self):
        """Test that creating a client without name fails."""
        data = {
            "email": "email@example.com",
        }
        response = self.client_tester.post(reverse("clients:add"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Client.objects.filter(email="email@example.com").exists())

    def test_create_client_shows_success_message(self):
        """Test that success message is shown after client creation."""
        data = {
            "name": "Success Client",
        }
        response = self.client_tester.post(
            reverse("clients:add"), data, follow=True
        )
        messages = list(response.context["messages"])
        self.assertTrue(any("created successfully" in str(m) for m in messages))

    def test_unauthenticated_user_cannot_create_client(self):
        """Test that unauthenticated user cannot create a client."""
        self.client_tester.logout()
        response = self.client_tester.get(reverse("clients:add"), follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])


class ClientReadTests(TestCase):
    """Tests for client list and read functionality."""

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
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_client_list_page_loads(self):
        """Test that client list page loads."""
        response = self.client_tester.get(reverse("clients:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "clients/client_list.html")

    def test_client_list_shows_user_clients(self):
        """Test that client list shows only user's clients."""
        client1 = Client.objects.create(name="Client 1", business=self.business)
        client2 = Client.objects.create(name="Client 2", business=self.business)
        response = self.client_tester.get(reverse("clients:list"))
        self.assertContains(response, "Client 1")
        self.assertContains(response, "Client 2")

    def test_client_list_does_not_show_other_users_clients(self):
        """Test that client list doesn't show other users' clients."""
        other_client = Client.objects.create(
            name="Other Client",
            business=self.business2,
        )
        response = self.client_tester.get(reverse("clients:list"))
        self.assertNotContains(response, "Other Client")

    def test_client_list_sorted_by_name(self):
        """Test that clients are sorted by name."""
        Client.objects.create(name="Zebra Client", business=self.business)
        Client.objects.create(name="Apple Client", business=self.business)
        response = self.client_tester.get(reverse("clients:list"))
        clients = response.context["clients"]
        self.assertEqual(clients[0].name, "Apple Client")
        self.assertEqual(clients[1].name, "Zebra Client")

    def test_empty_client_list(self):
        """Test that empty client list displays correctly."""
        response = self.client_tester.get(reverse("clients:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["clients"]), 0)

    def test_client_list_with_multiple_clients(self):
        """Test client list with multiple clients."""
        for i in range(5):
            Client.objects.create(
                name=f"Client {i}",
                business=self.business,
            )
        response = self.client_tester.get(reverse("clients:list"))
        self.assertEqual(len(response.context["clients"]), 5)

    def test_unauthenticated_user_cannot_access_client_list(self):
        """Test that unauthenticated user cannot access client list."""
        self.client_tester.logout()
        response = self.client_tester.get(reverse("clients:list"), follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])


class ClientUpdateTests(TestCase):
    """Tests for client update functionality."""

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
        self.business2= BusinessProfile.objects.get(
            user=self.user2
        )
        self.client_obj = Client.objects.create(
            name="Original Client",
            email="original@example.com",
            business=self.business,
        )
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_client_update_page_loads(self):
        """Test that client update page loads."""
        url = reverse("clients:edit", kwargs={"pk": self.client_obj.pk})
        response = self.client_tester.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "clients/client_form.html")

    def test_update_client_name(self):
        """Test updating client name."""
        url = reverse("clients:edit", kwargs={"pk": self.client_obj.pk})
        data = {
            "name": "Updated Client",
            "email": self.client_obj.email,
        }
        response = self.client_tester.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.client_obj.refresh_from_db()
        self.assertEqual(self.client_obj.name, "Updated Client")

    def test_update_client_email(self):
        """Test updating client email."""
        url = reverse("clients:edit", kwargs={"pk": self.client_obj.pk})
        data = {
            "name": self.client_obj.name,
            "email": "newemail@example.com",
        }
        response = self.client_tester.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.client_obj.refresh_from_db()
        self.assertEqual(self.client_obj.email, "newemail@example.com")

    def test_update_all_client_fields(self):
        """Test updating all client fields."""
        url = reverse("clients:edit", kwargs={"pk": self.client_obj.pk})
        data = {
            "name": "Completely Updated",
            "email": "updated@example.com",
            "phone": "555-9999",
            "company": "New Company",
            "notes": "Updated notes",
        }
        response = self.client_tester.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.client_obj.refresh_from_db()
        self.assertEqual(self.client_obj.name, "Completely Updated")
        self.assertEqual(self.client_obj.email, "updated@example.com")
        self.assertEqual(self.client_obj.phone, "555-9999")
        self.assertEqual(self.client_obj.company, "New Company")
        self.assertEqual(self.client_obj.notes, "Updated notes")

    def test_update_client_shows_success_message(self):
        """Test that success message is shown after update."""
        url = reverse("clients:edit", kwargs={"pk": self.client_obj.pk})
        data = {
            "name": "Updated",
        }
        response = self.client_tester.post(url, data, follow=True)
        messages = list(response.context["messages"])
        self.assertTrue(any("updated successfully" in str(m) for m in messages))

    def test_cannot_update_other_users_client(self):
        """Test that user cannot update another user's client."""
        other_client = Client.objects.create(
            name="Other User's Client",
            business=self.business2,
        )
        url = reverse("clients:edit", kwargs={"pk": other_client.pk})
        response = self.client_tester.get(url, follow=False)
        self.assertEqual(response.status_code, 404)

    def test_update_client_with_invalid_email(self):
        """Test updating client with invalid email."""
        url = reverse("clients:edit", kwargs={"pk": self.client_obj.pk})
        data = {
            "name": self.client_obj.name,
            "email": "not-an-email",
        }
        response = self.client_tester.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.client_obj.refresh_from_db()
        self.assertNotEqual(self.client_obj.email, "not-an-email")

    def test_unauthenticated_user_cannot_update_client(self):
        """Test that unauthenticated user cannot update a client."""
        self.client_tester.logout()
        url = reverse("clients:edit", kwargs={"pk": self.client_obj.pk})
        response = self.client_tester.get(url, follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])


class ClientDeleteTests(TestCase):
    """Tests for client delete functionality."""

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
        self.client_obj = Client.objects.create(
            name="To Delete",
            business=self.business,
        )
        self.client_tester.login(username="testuser", password="TestPassword123!")

    def test_client_delete_page_loads(self):
        """Test that client delete confirmation page loads."""
        url = reverse("clients:delete", kwargs={"pk": self.client_obj.pk})
        response = self.client_tester.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "clients/client_confirm_delete.html")

    def test_delete_client(self):
        """Test deleting a client."""
        client_id = self.client_obj.pk
        url = reverse("clients:delete", kwargs={"pk": client_id})
        response = self.client_tester.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Client.objects.filter(pk=client_id).exists())

    def test_delete_client_shows_success_message(self):
        """Test that success message is shown after deletion."""
        url = reverse("clients:delete", kwargs={"pk": self.client_obj.pk})
        response = self.client_tester.post(url, follow=True)
        messages = list(response.context["messages"])
        self.assertTrue(any("deleted successfully" in str(m) for m in messages))

    def test_cannot_delete_other_users_client(self):
        """Test that user cannot delete another user's client."""
        other_client = Client.objects.create(
            name="Other User's Client",
            business=self.business2,
        )
        url = reverse("clients:delete", kwargs={"pk": other_client.pk})
        response = self.client_tester.get(url, follow=False)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Client.objects.filter(pk=other_client.pk).exists())

    def test_delete_client_redirects_to_list(self):
        """Test that deletion redirects to client list."""
        url = reverse("clients:delete", kwargs={"pk": self.client_obj.pk})
        response = self.client_tester.post(url)
        self.assertRedirects(response, reverse("clients:list"))

    def test_unauthenticated_user_cannot_delete_client(self):
        """Test that unauthenticated user cannot delete a client."""
        self.client_tester.logout()
        url = reverse("clients:delete", kwargs={"pk": self.client_obj.pk})
        response = self.client_tester.get(url, follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])


class ClientOwnershipTests(TestCase):
    """Tests for client ownership and access control."""

    def setUp(self):
        self.client_tester = TestClient()
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="TestPassword123!",
        )
        self.business1 = BusinessProfile.objects.get(
            user=self.user1
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="TestPassword123!",
        )
        self.business2 = BusinessProfile.objects.get(
            user=self.user2
        )
        self.client1 = Client.objects.create(
            name="Client 1",
            business=self.business1,
        )
        self.client2 = Client.objects.create(
            name="Client 2",
            business=self.business2,
        )

    def test_user1_owns_client1(self):
        """Test that client is owned by the correct business."""
        self.assertEqual(self.client1.business, self.business1)

    def test_user1_cannot_edit_user2_client(self):
        """Test that user1 cannot edit user2's client."""
        self.client_tester.login(username="user1", password="TestPassword123!")
        url = reverse("clients:edit", kwargs={"pk": self.client2.pk})
        response = self.client_tester.get(url, follow=False)
        self.assertEqual(response.status_code, 404)

    def test_user1_cannot_delete_user2_client(self):
        """Test that user1 cannot delete user2's client."""
        self.client_tester.login(username="user1", password="TestPassword123!")
        url = reverse("clients:delete", kwargs={"pk": self.client2.pk})
        response = self.client_tester.get(url, follow=False)
        self.assertEqual(response.status_code, 404)

    def test_user1_sees_only_their_clients(self):
        """Test that user1 only sees their own clients in the list."""
        self.client_tester.login(username="user1", password="TestPassword123!")
        response = self.client_tester.get(reverse("clients:list"))
        self.assertContains(response, "Client 1")
        self.assertNotContains(response, "Client 2")

    def test_user2_sees_only_their_clients(self):
        """Test that user2 only sees their own clients in the list."""
        self.client_tester.login(username="user2", password="TestPassword123!")
        response = self.client_tester.get(reverse("clients:list"))
        self.assertContains(response, "Client 2")
        self.assertNotContains(response, "Client 1")

    def test_client_business_relationship(self):
        """Test that client maintains correct business relationship."""
        self.assertEqual(self.client1.business.user, self.user1)
        self.assertEqual(self.client2.business.user, self.user2)
