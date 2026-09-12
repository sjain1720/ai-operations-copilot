from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models import customer, delivery, order, payment  # noqa: E402,F401
