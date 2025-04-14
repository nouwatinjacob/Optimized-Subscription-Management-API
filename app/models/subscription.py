from app.extensions import db
from datetime import datetime
from sqlalchemy import Numeric, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
import enum

class BillingFrequency(enum.Enum):
    monthly = 'monthly'
    yearly = 'yearly'
    
class Status(enum.Enum):
    active = 'active'
    cancel = 'cancel'
    expire = 'expire'
    
class Subscription(db.Model):

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer(), ForeignKey('user.id'), nullable=False)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey('plans.id'), nullable=False)
    frequency: Mapped[BillingFrequency] = mapped_column(
        Enum(BillingFrequency), nullable=False, default=BillingFrequency.monthly)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    status: Mapped[Status] = mapped_column(
        Enum(Status), nullable=False, default=Status.active)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=func.now())
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship('User', back_populates='subscriptions', lazy='selectin')
    plan: Mapped["Plan"] = relationship('Plan')

    def __repr__(self):
        return f"<Subscription {self.user_id} -> {self.plan.name} ({self.frequency})>"