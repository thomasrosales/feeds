from feeds_for_sendcloud.users.models import User


def test_user_str_representation(user: User):
    assert str(user) == f"{user.first_name} {user.last_name} with email {user.email}"
