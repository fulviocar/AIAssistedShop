# Unit Testing Conventions

## Framework

- Use **pytest** for all unit tests.
- Do not introduce another testing framework unless explicitly requested.
- Use pytest fixtures for reusable test setup and data.

## Test Location

Keep unit tests under:

```text
tests/unit/
```

Organize tests to mirror the application structure where practical.

Example:

```text
app/
    services/
        customer_service.py
        order_service.py

tests/
    unit/
        services/
            test_customer_service.py
            test_order_service.py
```

## Test Naming

Test files must start with `test_`:

```text
test_customer_service.py
test_order_service.py
```

Test functions must start with `test_` and describe the behavior being tested:

```python
def test_create_customer_with_valid_data():
    ...

def test_create_customer_rejects_empty_email():
    ...
```

Prefer:

```text
test_<behavior>_<condition>
```

over generic names such as:

```python
def test_customer():
    ...
```

## Test Structure

Use the **Arrange–Act–Assert (AAA)** pattern:

```python
def test_create_customer_with_valid_data():
    # Arrange
    name = "John Doe"
    email = "john@example.com"

    # Act
    customer = CustomerService.create_customer(name, email)

    # Assert
    assert customer.name == name
    assert customer.email == email
```

Keep tests focused on one behavior.

## Unit Test Isolation

Unit tests must be isolated from external systems.

Do not use real:

- databases
- HTTP APIs
- payment providers
- message brokers
- cloud services

Mock or stub external dependencies when necessary.

## Mocking

- Do not mock the unit being tested.
- Mock external dependencies only when required for isolation.
- Prefer dependency injection over excessive mocking.
- Verify behavior rather than implementation details.

## Exceptions

Use `pytest.raises()` to test expected exceptions:

```python
with pytest.raises(ValueError):
    CustomerService.create_customer("John", "")
```

Check the exception message when the message is part of the expected behavior.

## Parametrization

Use `pytest.mark.parametrize` when testing the same behavior with multiple inputs:

```python
@pytest.mark.parametrize(
    "email,expected",
    [
        ("USER@example.com", "user@example.com"),
        (" user@example.com ", "user@example.com"),
    ],
)
def test_email_is_normalized(email, expected):
    ...
```

## Test Data

- Keep test data simple and readable.
- Use fixtures for data reused across multiple tests.
- Avoid unnecessary global test state.
- Do not depend on the execution order of tests.

## E-commerce Business Rules

Unit tests should cover important business behavior such as:

- customer creation and validation
- product validation
- product pricing
- shopping cart operations
- order creation
- order totals
- discounts
- inventory rules
- invalid operations
- business-rule exceptions

## Test Quality

Tests should be:

- readable
- deterministic
- isolated
- fast
- independent
- focused on observable behavior

Do not write tests only to increase code coverage.

## Integration Testing

Integration tests may use real external dependencies or dedicated test instances, such as test databases, HTTP services, or message brokers.

Integration tests must be isolated from other tests.

When an integration test creates persistent state, it must explicitly provide teardown logic to remove that state after the test.

Examples of persistent state include:

- database records
- files
- queued messages
- external resources

Prefer pytest fixtures with `yield` for setup and teardown:

```python
@pytest.fixture
def customer(test_db):
    customer = create_customer(test_db)

    yield customer

    delete_customer(test_db, customer.id)
```

Teardown must run even when the test fails.

Do not rely on test execution order or on another test to clean up persistent state.

Integration tests must not leave persistent test data in the development or production environment.

## Running Tests

Run all tests:

```bash
pytest
```

Run unit tests:

```bash
pytest tests/unit/
```

Run with verbose output:

```bash
pytest -v
```

Run a specific test:

```bash
pytest tests/unit/services/test_customer_service.py::test_create_customer_with_valid_data
```

## Rule for Code Changes

When modifying application code:

1. Add or update the relevant unit tests.
2. Run the affected tests.
3. Run the complete unit test suite.
4. Do not change a test simply to make it pass unless the expected behavior has changed.
5. Preserve existing tests unless they are no longer valid.
