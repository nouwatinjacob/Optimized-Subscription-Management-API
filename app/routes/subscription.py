from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.models.plan import Plan
from app.models.user import User
from app.models.subscription import Subscription, BillingFrequency, Status
from app.schemas.subscription import SubscriptionSchema, CreateSubscriptionSchema
from app.services.subscription import create_subscription, upgrade_sub
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.utils.time_util import utc_now
from app import db


sub_bp = Blueprint('subscription', __name__)
sub_schema = SubscriptionSchema()
create_sub_schema = CreateSubscriptionSchema()

@jwt_required
@sub_bp.post('/subscribe')
def subscribe():
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    try:
        data = create_sub_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    user = db.session.get(User, user_id)
    plan = db.session.get(Plan, data["plan_id"])
    frequency = data["frequency"].lower()
    
    subscription, error, status = create_subscription(user, plan, frequency)
    
    if error:
        return jsonify({"error": error}), status

    return jsonify(sub_schema.dump(subscription)), 201


@jwt_required
@sub_bp.post('/upgrade')
def upgrade_subscription():
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    
    try:
        data = create_sub_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    user = db.session.get(User, user_id)
    plan = db.session.get(Plan, data["plan_id"])
    frequency = data["frequency"].lower()
    
    subscription, error, status = upgrade_sub(user, plan, frequency)
    
    if error:
        return jsonify({"error": error}), status

    return jsonify(sub_schema.dump(subscription)), 201


@jwt_required
@sub_bp.patch('/cancel')
def cancel_subscription():
    verify_jwt_in_request()
    data = request.get_json()
    user_id = get_jwt_identity()
    subscription = Subscription.query.filter_by(id=data['subscription_id'], user_id=user_id).first()
    
    if not subscription or subscription.status != Status.active:
        return {"error": "Subscription not found or not active"}, 404
    
    subscription.status = Status.cancel
    subscription.ended_at = utc_now()
    db.session.commit()
    return jsonify({"error": "Subscription cancelled"}), 200

@jwt_required
@sub_bp.get('/')
def user_subscription_list():
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    
    status_filter = request.args.get("status", None)

    query = Subscription.query.filter_by(user_id=user_id)

    if status_filter:
        query = query.filter(Subscription.status == status_filter)

    subscriptions = query.order_by(Subscription.started_at.desc()).all()
    return  jsonify(sub_schema.dump(subscriptions, many=True)), 200


@jwt_required()
@sub_bp.get('/<int:subscription_id>')
def retrieve_subscription(subscription_id):
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    
    subscription = Subscription.query.filter_by(id=subscription_id, user_id=user_id).first()

    if not subscription:
        return {"error": "Subscription not found"}, 404

    return  jsonify(sub_schema.dump(subscription)), 200