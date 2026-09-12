from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models import conversation, customer, delivery, message, order, payment  # noqa: E402,F401
