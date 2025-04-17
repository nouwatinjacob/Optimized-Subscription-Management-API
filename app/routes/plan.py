from flask import request
from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError
from app.models.plan import Plan
from app.schemas.plan import PlanSchema, ListPlanSchema
from app.services.plan import plan_creation


plan_schema = PlanSchema()
list_plan_schema = ListPlanSchema()

plan_ns = Namespace('plan', description='Plan operations')

plan_model = plan_ns.model('CreatePlan', {
    'name': fields.String(required=True),
    'price': fields.Float(required=True),
    'description': fields.String(),
})


@plan_ns.route('/create')
class CreatePlan(Resource):
    """
    Creates a new subscription plan based on the provided data. 
    Validates the input, creates the plan, and returns it if successful. 
    If there are validation errors or creation issues, appropriate error messages are returned.
    """
    @plan_ns.expect(plan_model)
    @plan_ns.response(201, 'Plan created')
    def post(self):
        try:
            data = plan_schema.load(request.get_json())
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        plan, error, status = plan_creation(data)
        if error:
            return {"error": error}, status
        
        return list_plan_schema.dump(plan), status


@plan_ns.route('/')
class ListPlans(Resource):
    """
    Retrieves a list of all available subscription plans.
    Returns a serialized list of plans.
    """
    @plan_ns.response(200, "List of plans")
    def get(self):
        plans = Plan.query.all()
        return list_plan_schema.dump(plans, many=True)
