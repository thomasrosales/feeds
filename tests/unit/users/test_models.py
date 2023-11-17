from feeds_for_sendcloud.users.models import User


def test_user_str_representation(user: User):
    assert str(user) == f"{user.username} with email {user.email}"
