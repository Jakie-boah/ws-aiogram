from faker import Faker

from src.domain.entities.admin_message import AdminMessage
from src.domain.values import MessageIdInt, Text

fake = Faker()


def test_as_dict():
    message_id, text = MessageIdInt(fake.pyint(min_value=1, max_value=999999)), Text(fake.text())
    message = AdminMessage(message_id=message_id, text=text)

    assert message.as_dict() == {"message_id": message_id.value, "text": text.value}
