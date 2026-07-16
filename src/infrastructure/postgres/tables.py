from sqlalchemy import MetaData, Table, Column, UUID

metadata = MetaData()

tickets_table = Table(
    "tickets", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
)

messages_table = Table(
    "messages", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),

)
