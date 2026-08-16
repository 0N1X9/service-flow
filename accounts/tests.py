"""
Test suite for accounts app.
Covers: registration, login, and access control.
"""

from django.contrib.auth.models import User
from django.test import Client as TestClient
from django.test import TestCase
from django.urls import reverse

from core.models import BusinessProfile

from .forms import RegistrationForm, LoginForm


class RegistrationTests(TestCase):
    """Tests for user registration functionality."""

    def setUp(self):
        self.client = TestClient()
        self.register_url = reverse("accounts:register")

    def test_registration_page_loads(self):
        """Test that registration page loads successfully."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")
        self.assertIsInstance(response.context["form"], RegistrationForm)

    def test_registration_form_valid_data(self):
        """Test registration with valid data."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "john@example.com",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="johndoe").exists())

    def test_registration_creates_user(self):
        """Test that registration creates a new user."""
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "username": "janesmith",
            "email": "jane@example.com",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
        }
        self.client.post(self.register_url, data)
        user = User.objects.get(username="janesmith")
        self.assertEqual(user.email, "jane@example.com")
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Smith")

    def test_registration_creates_business_profile(self):
        """Test that registration creates a business profile."""
        data = {
            "first_name": "Bob",
            "last_name": "Builder",
            "username": "bobbuilder",
            "email": "bob@example.com",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
        }
        self.client.post(self.register_url, data)
        user = User.objects.get(username="bobbuilder")
        self.assertTrue(BusinessProfile.objects.filter(user=user).exists())

    def test_registration_form_password_mismatch(self):
        """Test registration form with mismatched passwords."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe2",
            "email": "john2@example.com",
            "password1": "TestPassword123!",
            "password2": "DifferentPassword123!",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="johndoe2").exists())

    def test_registration_form_duplicate_username(self):
        """Test registration with duplicate username."""
        User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="TestPassword123!",
        )
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "existing",
            "email": "newemail@example.com",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="existing").count(), 1)

    def test_registration_form_invalid_email(self):
        """Test registration with invalid email."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe3",
            "email": "invalid-email",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="johndoe3").exists())

    def test_registration_form_weak_password(self):
        """Test registration with weak password."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe4",
            "email": "john4@example.com",
            "password1": "123",
            "password2": "123",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="johndoe4").exists())

    def test_registered_user_is_logged_in(self):
        """Test that user is logged in after successful registration."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe5",
            "email": "john5@example.com",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
        }
        response = self.client.post(self.register_url, data, follow=True)
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class LoginTests(TestCase):
    """Tests for user login functionality."""

    def setUp(self):
        self.client = TestClient()
        self.login_url = reverse("accounts:login")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
        )
        self.business_profile = BusinessProfile.objects.get(
            user=self.user
        )

    def test_login_page_loads(self):
        """Test that login page loads successfully."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_login_with_username(self):
        """Test login with username."""
        data = {
            "username": "testuser",
            "password": "TestPassword123!",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_email(self):
        """Test login with email address."""
        data = {
            "username": "test@example.com",
            "password": "TestPassword123!",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_username_containing_at_symbol(self):
        """Test login with a username containing an @ symbol."""
        self.user = User.objects.create_user(
            username="user@company",
            email="realemail@example.com",
            password="TestPassword123!",
        )
        self.business_profile = BusinessProfile.objects.get(
            user=self.user
        )

        data = {
            "username": "user@company",
            "password": "TestPassword123!",
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_incorrect_password(self):
        """Test login with incorrect password."""
        data = {
            "username": "testuser",
            "password": "WrongPassword123!",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_with_nonexistent_user(self):
        """Test login with non-existent username."""
        data = {
            "username": "nonexistent",
            "password": "TestPassword123!",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_form_has_custom_placeholder(self):
        """Test that login form has custom username placeholder."""
        response = self.client.get(self.login_url)
        self.assertContains(response, "Enter your username or email")

    def test_login_case_insensitive_username(self):
        """Test that login is case-insensitive for username."""
        data = {
            "username": "TestUser",
            "password": "TestPassword123!",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)

    def test_login_case_insensitive_email(self):
        """Test that login is case-insensitive for email."""
        data = {
            "username": "TEST@example.com",
            "password": "TestPassword123!",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        """Test user logout."""
        self.client.login(username="testuser", password="TestPassword123!")
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class AccessControlTests(TestCase):
    """Tests for access control and authentication requirements."""

    def setUp(self):
        self.client = TestClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
        )
        self.business_profile = BusinessProfile.objects.get(
            user=self.user
        )

    def test_unauthenticated_user_redirected_from_dashboard(self):
        """Test that unauthenticated user is redirected from dashboard."""
        response = self.client.get(reverse("core:dashboard"), follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])

    def test_authenticated_user_can_access_dashboard(self):
        """Test that authenticated user can access dashboard."""
        self.client.login(username="testuser", password="TestPassword123!")
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_cannot_access_clients_list(self):
        """Test that unauthenticated user cannot access clients list."""
        response = self.client.get(reverse("clients:list"), follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])

    def test_authenticated_user_can_access_clients_list(self):
        """Test that authenticated user can access clients list."""
        self.client.login(username="testuser", password="TestPassword123!")
        response = self.client.get(reverse("clients:list"))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_cannot_access_services_list(self):
        """Test that unauthenticated user cannot access services list."""
        response = self.client.get(reverse("services:list"), follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])

    def test_authenticated_user_can_access_services_list(self):
        """Test that authenticated user can access services list."""
        self.client.login(username="testuser", password="TestPassword123!")
        response = self.client.get(reverse("services:list"))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_cannot_create_client(self):
        """Test that unauthenticated user cannot create a client."""
        response = self.client.get(reverse("clients:add"), follow=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])

    def test_authenticated_user_can_create_client(self):
        """Test that authenticated user can access client creation form."""
        self.client.login(username="testuser", password="TestPassword123!")
        response = self.client.get(reverse("clients:add"))
        self.assertEqual(response.status_code, 200)
