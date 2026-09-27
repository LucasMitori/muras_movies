import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Profile, User


@pytest.mark.django_db
def test_register_creates_user_and_profile_and_logs_in():
    client = APIClient()
    response = client.post(
        "/api/accounts/register/",
        {"username": "newuser", "email": "new@example.com", "password": "a-strong-password-1"},
    )
    assert response.status_code == 201
    assert User.objects.filter(username="newuser").exists()
    assert Profile.objects.filter(user__username="newuser").exists()

    me = client.get("/api/accounts/me/")
    assert me.status_code == 200
    assert me.data["username"] == "newuser"


@pytest.mark.django_db
def test_register_rejects_duplicate_email_case_insensitively():
    User.objects.create_user(username="existing", email="taken@example.com", password="whatever-password-1")
    client = APIClient()
    response = client.post(
        "/api/accounts/register/",
        {"username": "someoneelse", "email": "TAKEN@example.com", "password": "another-password-1"},
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_then_logout_clears_session():
    User.objects.create_user(username="loginuser", email="login@example.com", password="a-strong-password-1")
    client = APIClient()

    login = client.post("/api/accounts/login/", {"username": "loginuser", "password": "a-strong-password-1"})
    assert login.status_code == 200

    me = client.get("/api/accounts/me/")
    assert me.status_code == 200

    logout = client.post("/api/accounts/logout/")
    assert logout.status_code == 204

    me_after_logout = client.get("/api/accounts/me/")
    assert me_after_logout.status_code in (401, 403)


@pytest.mark.django_db
def test_login_with_wrong_password_is_rejected():
    User.objects.create_user(username="someone", email="someone@example.com", password="correct-password-1")
    client = APIClient()
    response = client.post("/api/accounts/login/", {"username": "someone", "password": "wrong-password"})
    assert response.status_code == 401
