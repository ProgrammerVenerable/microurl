from .database import Base
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

class Code(Base):
    __tablename__ = "codes"

    short_code: Mapped[str] = mapped_column(String(6), primary_key=True)
    original_url: Mapped[str] = mapped_column(Text)