import pytest
from fastapi.testclient import TestClient
from todo_service.main import app
from todo_service.core.auth import get_current_user
from todo_service.todos.schemas import UserRead

# 创建测试客户端
client = TestClient(app)


# 模拟一个认证用户
@pytest.fixture
def mock_user():
    return UserRead(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="test@example.com",
        is_active=True,  # ✅ 必须提供
        is_superuser=False,  # ✅ 必须提供
        is_verified=True,  # ✅ 必须提供
    )


# 测试 /server-status 路由
def test_health_check_valid_token():
    response = client.get("/server-status", params={"token": "Ace"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok 👍 "


def test_health_check_invalid_token():
    response = client.get("/server-status", params={"token": "Invalid"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found ❌"}


# 测试受保护路由
def test_protected_route(mock_user):
    # 覆盖 get_current_user 依赖项，确保测试时不需要真正的认证
    app.dependency_overrides[get_current_user] = lambda: mock_user
    response = client.get("/protected-route")
    assert response.status_code == 200
    assert response.json() == {
        "message": "This is a protected route",
        "user": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "test@example.com",
            "is_active": True,
            "is_superuser": False,
            "is_verified": True
        },
    }
