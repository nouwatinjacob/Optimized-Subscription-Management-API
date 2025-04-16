from datetime import datetime
from sqlalchemy import Numeric, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from app.extensions import db
from app.utils.time_util import utc_now
from typing import List


class Plan(db.Model):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    description: Mapped[str] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    
    # Relationship to Subscription
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription", back_populates="plan", lazy=True
    )
    
    def __repr__(self):
        return f"<Plan {self.name}>"