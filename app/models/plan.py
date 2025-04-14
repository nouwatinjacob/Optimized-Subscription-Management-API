from datetime import datetime
from sqlalchemy import Numeric
from decimal import Decimal
from app.extensions import db


class Plan(db.Model):
    __tablename__ = 'plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Plan {self.name}>"