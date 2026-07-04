from faker import Faker

from src.domain.entities.client_message import ClientMessage
from src.domain.values import Text, UserId

fake = Faker()


def test_as_dict():
    user_id, text = UserId(fake.pyint(min_value=1, max_value=999999)), Text(fake.text())
    message = ClientMessage(user_id=user_id, text=text)

    assert message.as_dict() == {"user_id": user_id.value, "text": text.value}
