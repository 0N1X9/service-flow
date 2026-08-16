# Test Suite Documentation

This document describes the comprehensive test suite generated for the Service Flow project following the test map specification.

## Overview

The test suite covers all major functionality across the project's five main apps:
- **Accounts**: User registration, login, and access control
- **Clients**: CRUD operations and ownership validation
- **Services**: Create, update, delete, and status management
- **Quotes**: Generation, regeneration, and usage limits
- **Payments**: Subscription management and premium behavior

## Test Structure

### Accounts App (`accounts/tests.py`)

#### RegistrationTests (9 tests)
Tests for user account registration:
- Valid registration flow
- User creation with all fields
- Business profile auto-creation
- Password validation (matching, strength)
- Email validation
- Duplicate username/email prevention
- Automatic login after registration
- Success message display

#### LoginTests (10 tests)
Tests for user login functionality:
- Login with username and email support
- Case-insensitive authentication
- Login with username containing "@" symbol
- Password validation
- Form custom placeholders
- Session management
- Logout functionality

#### AccessControlTests (8 tests)
Tests for authentication and access control:
- Login requirements for protected views
- Dashboard access control
- Clients list access control
- Services list access control
- Client creation access control

**Total: 27 tests**

---

### Clients App (`clients/tests.py`)

#### ClientCreateTests (9 tests)
Tests for client creation:
- Form page loads correctly
- Creation with required fields only
- Creation with all fields
- Email validation
- Required field validation
- Business relationship creation
- Success message display
- Authentication requirement

#### ClientReadTests (7 tests)
Tests for viewing client lists:
- List page loads
- Only user's clients shown
- Other users' clients hidden
- Alphabetical sorting
- Empty list handling
- Authentication requirement

#### ClientUpdateTests (8 tests)
Tests for updating clients:
- Update form loads
- Update individual fields (name, email, etc.)
- Update all fields simultaneously
- Email validation on update
- Business relationship maintained
- Ownership verification (can't update other users' clients)
- Success message display
- Authentication requirement

#### ClientDeleteTests (6 tests)
Tests for deleting clients:
- Delete confirmation page loads
- Delete functionality
- Success message display
- Ownership verification
- Proper redirect after deletion
- Authentication requirement

#### ClientOwnershipTests (6 tests)
Tests for client ownership and isolation:
- Business relationship validation
- User isolation in edit operations
- User isolation in delete operations
- List filtering by business
- Cross-user access prevention

**Total: 36 tests**

---

### Services App (`services/tests.py`)

#### ServiceCreateTests (9 tests)
Tests for service request creation:
- Form page loads
- Creation with required fields
- Creation with optional fields (estimated_price)
- Default status (NEW)
- Client queryset filtered to user's clients
- Title and description validation
- Success message display
- Authentication requirement

#### ServiceReadTests (6 tests)
Tests for service list viewing:
- List page loads
- Only user's services shown
- Other users' services hidden
- Reverse chronological sorting
- Empty list handling
- Authentication requirement

#### ServiceUpdateTests (8 tests)
Tests for updating service requests:
- Update form loads
- Update title, description, price
- Client queryset filtering
- Ownership verification
- Success message display
- Cross-user access prevention
- Authentication requirement

#### ServiceDeleteTests (5 tests)
Tests for deleting service requests:
- Delete confirmation page loads
- Delete functionality
- Success message display
- Ownership verification
- Authentication requirement

#### ServiceStatusChangeTests (10 tests)
Tests for service status management:
- Default status (NEW)
- All status choices available
- Status transitions (QUOTED, SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED)
- Status persistence on updates
- Quote marked outdated when service fields change
- Multiple sequential status transitions

**Total: 38 tests**

---

### Quotes App (`quotes/tests.py`)

#### QuoteGenerationTests (9 tests)
Tests for AI quote generation:
- Quote creation on generation
- Content, provider, and price assignment
- Service status updated to QUOTED
- Provider information recorded
- Price from estimated service price
- Success message display
- New quotes not marked outdated
- Ownership verification
- Authentication requirement

#### QuoteRegenerationTests (9 tests)
Tests for quote regeneration and editing:
- Quote detail page loads and displays
- Edit quote content
- Update quote via regeneration
- Success message on edit
- Ownership verification for edits
- Quote list page shows correct quotes
- Cross-user access prevention

#### QuoteUsageLimitTests (8 tests)
Tests for monthly quota and premium features:
- Free tier monthly limit (3 quotes)
- Limit enforcement
- Upgrade message when limit exceeded
- Premium users have unlimited quotes
- Monthly reset (separate months counted separately)
- Multiple quotes in same month counted
- Inactive subscription treated as free tier
- Usage statistics on upgrade page
- Limit counting accuracy

**Total: 26 tests**

---

### Payments App (`payments/tests.py`)

#### SubscriptionModelTests (6 tests)
Tests for subscription model:
- Subscription creation
- Stripe customer ID storage
- Expiration date tracking
- One-to-one relationship with User
- Default plan (free)
- Default active status

#### PremiumBehaviorTests (6 tests)
Tests for premium subscription features:
- Premium status detection
- Premium/free user differentiation
- Inactive subscription treated as free
- Premium unlimited quote generation
- Free tier quota limitation(2 tests)

#### UpgradePageTests (6 tests)
Tests for upgrade/billing page:
- Page loads correctly
- Shows quote usage statistics
- Shows quota limit
- Shows premium status
- Accurate usage reporting
- Authentication requirement

#### CheckoutTests (2 tests)
Tests for Stripe checkout process:
- Checkout redirects to Stripe
- Authentication requirement

#### SuccessAndCancelTests (4 tests)
Tests for checkout completion pages:
- Success page loads
- Cancel page loads
- Authentication requirements
- Proper template usage

#### QuoteGenerationAccessControlTests (2 tests)
Tests for quote limits with premium features:
- Free users see upgrade prompt after limit
- Premium users not blocked by limit

**Total: 26 tests**

---

## Running the Tests

### Run All Tests
```bash
python manage.py test
```

### Run Tests for Specific App
```bash
python manage.py test accounts
python manage.py test clients
python manage.py test services
python manage.py test quotes
python manage.py test payments
```

### Run Specific Test Class
```bash
python manage.py test accounts.tests.RegistrationTests
python manage.py test clients.tests.ClientCreateTests
python manage.py test services.tests.ServiceStatusChangeTests
python manage.py test quotes.tests.QuoteUsageLimitTests
python manage.py test payments.tests.PremiumBehaviorTests
```

### Run Specific Test Method
```bash
python manage.py test accounts.tests.RegistrationTests.test_registration_form_valid_data
```

### Run with Verbosity
```bash
python manage.py test -v 2  # Show test names
python manage.py test -v 3  # Show detailed output
```

### Run with Coverage (requires coverage package)
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

---

## Test Coverage Summary

| App      | Test Classes | Test Methods | Coverage Areas                              |
|----------|--------------|--------------|---------------------------------------------|
| accounts | 3            | 27           | Registration, Login, Access Control        |
| clients  | 5            | 36           | CRUD, Ownership, Business Relationship     |
| services | 5            | 38           | CRUD, Status Changes, Ownership            |
| quotes   | 3            | 26           | Generation, Regeneration, Usage Limits     |
| payments | 6            | 26           | Subscriptions, Premium Behavior, Checkout  |
| **Total**| **22**       | **153**      | **Full Project Coverage**                  |

### Test running results

```bash
> python manage.py test              
Found 153 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..............................................................................
..............................................................................
----------------------------------------------------------------------
Ran 153 tests in 654.083s

OK
Destroying test database for alias 'default'...
```

---

## Key Testing Patterns

### 1. Authentication Testing
All views are tested to ensure:
- Unauthenticated users are redirected to login
- Authenticated users can access protected views
- Test cases explicitly check for 301/302/303/307/308 redirect status codes

### 2. Ownership Validation
Tests verify that:
- Users can only access their own resources
- Users can't edit/delete other users' data
- Queryset filtering prevents cross-user access
- 404 errors returned for unauthorized access attempts

### 3. Form Validation
Tests validate:
- Required fields are enforced
- Email format validation
- Password strength requirements
- Field type conversions (Decimal, DateTime, etc.)

### 4. Business Logic
Tests verify:
- Status transitions work correctly
- Related objects are created/updated properly
- Cascade deletions work as expected
- Relationships are maintained

### 5. Usage Limits
Tests validate:
- Free tier quote limits enforced
- Premium features work correctly
- Monthly quota resets work
- Upgrade paths are available

### 6. User Feedback
Tests check for:
- Success messages after operations
- Error handling and display
- Proper redirects after actions
- Form error displays

---

## Dependencies

The test suite uses:
- Django's built-in `TestCase` class
- `unittest.mock` for mocking external services (Stripe, AI providers)
- Standard Django test client for HTTP testing
- Test database isolation (automatic per test)

---

## Mocking Strategy

Tests that interact with external services use mocks:

### AI Service Mocking
```python
@patch("quotes.views.generate_quote")
def test_generate_quote(self, mock_generate):
    mock_generate.return_value = MagicMock(
        content="Test quote",
        provider="openai"
    )
```

### Stripe Integration Mocking
```python
@patch("payments.stripe_service.stripe.checkout.Session.create")
def test_checkout(self, mock_checkout):
    mock_checkout.return_value = MagicMock(
        url="https://checkout.stripe.com/test"
    )
```

---

## Notes for Developers

1. **Database**: Tests use an isolated test database that's created and destroyed for each test run
2. **Fixtures**: No fixtures are used; data is created in `setUp()` methods for clarity
3. **Isolation**: Each test is independent and can run in any order
4. **Mocks**: External service calls are mocked to prevent actual API calls

---

## Continuous Integration

To integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    python manage.py test --no-migrations
    
- name: Coverage
  run: |
    coverage run --source='.' manage.py test
    coverage report --fail-under=80
```

---

## Troubleshooting

### Import Errors
Ensure all app migrations are run:
```bash
python manage.py migrate
```

### Missing Dependencies
Install test requirements:
```bash
pip install -r requirements.txt
```

### Test Database Issues
Reset test database:
```bash
python manage.py flush
```

### Mock Not Working
Verify the import path in the @patch decorator matches the actual import location in the code being tested.

---

## Contact & Questions

For questions about specific tests or testing patterns, refer to the inline comments in each test file or Django's official testing documentation: https://docs.djangoproject.com/en/stable/topics/testing/

