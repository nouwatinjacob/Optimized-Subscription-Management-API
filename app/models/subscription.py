from app.extensions import db
from datetime import datetime 
from sqlalchemy import Numeric
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
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)

    frequency = db.Column(db.Enum(BillingFrequency), nullable=False, default=BillingFrequency.monthly)
    amount = db.Column(Numeric(10, 2), nullable=False, default=Decimal('0.00'))

    status = db.Column(db.Enum(Status), nullable=False, default=Status.active)
    started_at = db.Column(db.DateTime, default=datetime.now)
    ended_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', back_populates='subscriptions', lazy='selectin')
    plan = db.relationship('Plan')

    def __repr__(self):
        return f"<Subscription {self.user_id} -> {self.plan.name} ({self.frequency})>"