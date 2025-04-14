from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.models.plan import Plan
from app.schemas.plan import PlanSchema, ListPlanSchema
from app.services.plan import plan_creation



plan_bp = Blueprint('plan', __name__)
plan_schema = PlanSchema()
list_plan_schema = ListPlanSchema()


@plan_bp.post('/create')
def create_plan():
    data = request.get_json()
    try:
        validated_data = plan_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    plan, error, status = plan_creation(validated_data)
    
    if error:
        return jsonify({"error": error}), status
    
    return list_plan_schema.dump(plan), status


@plan_bp.get('/')
def list_plan():
    plans = Plan.query.all()
    return list_plan_schema.dump(plans, many=True)