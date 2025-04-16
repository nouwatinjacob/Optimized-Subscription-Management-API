from app.models.subscription import Subscription, BillingFrequency, Status
from app.utils.price_util import calculate_amount
from app.utils.subscription_util import get_subscription_date_bound, get_downgrade_bound
from app import db
from app.models.plan import Plan

def create_subscription(user, plan, frequency):
    if not plan:
        return None, "Invalid Subscription Plan", 404
    
    start_date, end_date =  get_subscription_date_bound(frequency)
    amount = calculate_amount(plan.price, frequency)
    
    # Check if the user have a running subscription
    active_subscription = Subscription.query.filter_by(user_id=user.id,
            status=Status.active).first()
    if active_subscription:
        return None, "You still have an active subscription", 400
        
    subscription = Subscription(
        user_id=user.id,
        plan_id=plan.id,
        frequency=frequency,
        amount=amount,
        status=Status.active,
        started_at=start_date,
        ended_at=end_date
    )
    db.session.add(subscription)
    db.session.commit()
    return subscription, None, 201

def upgrade_sub(user, plan, frequency):
    active_subscription = Subscription.query.filter_by(user_id=user.id, status=Status.active).first()
    start_date, end_date =  get_subscription_date_bound(frequency)
    amount = calculate_amount(plan.price, frequency)
    
    if not active_subscription:
        return None, "You do not have active Subscription", 400
    
    # This part downgrades subscription
    active_plan = db.session.get(Plan, active_subscription.plan_id)
    if active_plan.price < plan.price:
        downgrade_sub(active_subscription, plan, frequency)
    
    # expiry the active subscription before adding new subscription
    active_subscription.status=Status.expire
    
    # create new subscription for the upgraded plan
    subscription = Subscription(
    user_id=user.id,
    plan_id=plan.id,
    frequency=frequency,
    amount=amount,
    status=Status.active,
    started_at=start_date,
    ended_at=end_date
    )
    db.session.add(subscription)
    db.session.commit()
    
    return subscription, None, 201


def downgrade_sub(active_subscription, plan, frequency):
    start_date, end_date =  get_downgrade_bound(active_subscription.ended_at, frequency)
    amount = calculate_amount(plan.price, frequency)
    
    subscription = Subscription(
    user_id=active_subscription.user.id,
    plan_id=plan.id,
    frequency=frequency,
    amount=amount,
    status=Status.pending,
    started_at=start_date,
    ended_at=end_date
    )
    db.session.add(subscription)
    db.session.commit()
    return subscription, None, 201