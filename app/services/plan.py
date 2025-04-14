from app.extensions import db
from app.models.plan import Plan


def plan_creation(validated_data):
    if Plan.query.filter_by(name=validated_data['name']).first():
        return None, "Plan with this name already exists", 409
    
    plan = Plan(
        name=validated_data['name'],
        price=validated_data['price'],
        description=validated_data['description']
    )
    db.session.add(plan)
    db.session.commit()
    return plan, None, 201