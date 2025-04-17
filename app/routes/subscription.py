from flask import request
from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload
from app.models.plan import Plan
from app.models.user import User
from app.models.subscription import Subscription, BillingFrequency, Status
from app.schemas.subscription import SubscriptionSchema, CreateSubscriptionSchema
from app.services.subscription import create_subscription, upgrade_sub
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.utils.time_util import utc_now
from app import db


sub_schema = SubscriptionSchema()
create_sub_schema = CreateSubscriptionSchema()

sub_ns = Namespace('subscription', description='Subscription operations')

subscription_input = sub_ns.model("SubscriptionInput", {
    "plan_id": fields.Integer(required=True),
    "frequency": fields.String(required=True)
})

subscription_output = sub_ns.model("Subscription", {
    "id": fields.Integer,
    "plan_id": fields.Integer,
    "user_id": fields.Integer,
    "frequency": fields.String,
    "amount": fields.Float,
    "status": fields.String,
    "started_at": fields.DateTime,
    "ended_at": fields.DateTime
})

cancel_input = sub_ns.model("CancelSubscription", {
    "subscription_id": fields.Integer(required=True)
})

pagination_model = sub_ns.model("SubscriptionPagination", {
    "total": fields.Integer,
    "pages": fields.Integer,
    "current_page": fields.Integer,
    "per_page": fields.Integer,
    "items": fields.List(fields.Nested(subscription_output))
})

@sub_ns.route('/subscribe')
class Subscribe(Resource):
    """
    Allows a user to create a new subscription.
    Requires a valid JWT token, validates subscription data, and creates the subscription.
    """
    @jwt_required()
    @sub_ns.expect(subscription_input)
    @sub_ns.response(201, "Subscription created successfully")
    @sub_ns.response(400, "Bad request")
    def post(self):
        user_id = get_jwt_identity()
        try:
            data = create_sub_schema.load(request.get_json())
        except ValidationError as err:
             return {"errors": err.messages}, 400

        user = db.session.get(User, user_id)
        plan = db.session.get(Plan, data["plan_id"])
        frequency = data["frequency"].lower()

        subscription, error, status = create_subscription(user, plan, frequency)
        if error:
            return {"error": error}, status
        
        return sub_schema.dump(subscription), 201


@sub_ns.route('/upgrade')
class Upgrade(Resource):
    """
    Allows a user to upgrade their current subscription to a new plan.
    Requires a valid JWT token, validates the upgrade data, and processes the upgrade.
    """
    @sub_ns.expect(subscription_input)
    @sub_ns.response(400, "Bad request")
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        try:
            data = create_sub_schema.load(request.get_json())
        except ValidationError as err:
            return {"errors": err.messages}, 400

        user = db.session.get(User, user_id)
        plan = db.session.get(Plan, data["plan_id"])
        frequency = data["frequency"].lower()
        
        if not plan:
            return {"error": "Invalid plan ID"}, 400

        subscription, error, status = upgrade_sub(user, plan, frequency)
        if error:
            return {"error": error}, status

        return sub_schema.dump(subscription), 201


@sub_ns.route('/cancel')
class Cancel(Resource):
    """
    Allows a user to cancel an active subscription.
    Requires a valid JWT token, validates the cancellation data, and processes the cancellation.
    """
    @sub_ns.expect(cancel_input)
    @sub_ns.response(200, "Subscription cancelled")
    @sub_ns.response(400, "Bad request")
    @jwt_required()
    def patch(self):
        user_id = get_jwt_identity()
        data = request.get_json()

        subscription = Subscription.query.filter_by(
            id=data['subscription_id'], user_id=user_id
        ).first()

        if not subscription or subscription.status != Status.active:
            return {"error": "Subscription not found or not active"}, 404

        subscription.status = Status.cancel
        subscription.ended_at = utc_now()
        db.session.commit()
        return {"message": "Subscription cancelled"}, 200


@sub_ns.route('/')
class UserSubscriptions(Resource):
    """
    Fetches a list of subscriptions for the authenticated user, with optional filters for status, 
    and supports pagination. Requires a valid JWT token.
    """
    @sub_ns.marshal_list_with(pagination_model)
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        status_filter = request.args.get("status", None)
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Eager load related user and plan
        query = Subscription.query.options( joinedload(
            Subscription.plan)).filter_by(user_id=user_id)

        if status_filter:
            query = query.filter(Subscription.status == status_filter)

        pagination = query.order_by(Subscription.started_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "per_page": pagination.per_page,
            "items": sub_schema.dump(pagination.items, many=True),
        }, 200


@sub_ns.route('/<int:subscription_id>')
class SubscriptionDetail(Resource):
    """
    Retrieves detailed information about a specific subscription for the authenticated user.
    Requires a valid JWT token. Returns a 404 error if the subscription is not found.
    """
    @sub_ns.marshal_with(subscription_output)
    @sub_ns.response(400, "Bad request")
    @jwt_required()
    def get(self, subscription_id):
        user_id = get_jwt_identity()
        
        subscription = Subscription.query.options(joinedload(Subscription.plan)).filter_by(
            id=subscription_id, user_id=user_id).first()

        if not subscription:
            return {"error": "Subscription not found"}, 404
        
        return sub_schema.dump(subscription), 200
