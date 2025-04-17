from app.extensions import db
from datetime import datetime
from sqlalchemy import Numeric, Integer, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
import enum
from app.utils.time_util import utc_now

class BillingFrequency(enum.Enum):
    monthly = 'monthly'
    yearly = 'yearly'
    
class Status(enum.Enum):
    active = 'active'
    cancel = 'cancel'
    expire = 'expire'
    pending = 'pending'
    
class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer(), ForeignKey('user.id'), nullable=False)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey('plans.id'), nullable=False)
    frequency: Mapped[BillingFrequency] = mapped_column(
        Enum(BillingFrequency), nullable=False, default=BillingFrequency.monthly)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    status: Mapped[Status] = mapped_column(
        Enum(Status), nullable=False, default=Status.active)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=utc_now)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships to User and Plan
    user: Mapped["User"] = relationship(
        "User", back_populates="subscriptions", lazy="joined"
    )
    plan: Mapped["Plan"] = relationship(
        "Plan", back_populates="subscriptions", lazy="joined"
    )
    
    __table_args__ = (
        Index("ix_user_status", "user_id", "status"),
    )

    def __repr__(self):
        return f"<Subscription {self.user_id} -> {self.plan.name} ({self.frequency})>"