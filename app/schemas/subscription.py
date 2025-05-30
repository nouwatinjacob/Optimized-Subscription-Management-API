from marshmallow import Schema, fields, validate
from app.models.subscription import BillingFrequency
from .plan import ListPlanSchema
from .user import UserSchema

class SubscriptionSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    plan_id = fields.Int()
    plan = fields.Nested(ListPlanSchema)
    frequency = fields.Method("get_frequency")
    amount = fields.Decimal(as_string=True, places=2)
    status = fields.Method("get_status")
    started_at = fields.DateTime()
    ended_at = fields.DateTime()
    
    def get_status(self, obj):
        return obj.status.value if obj.status else None

    def get_frequency(self, obj):
        return obj.frequency.value if obj.frequency else None
    
class CreateSubscriptionSchema(Schema):
    plan_id = fields.Int(required=True)
    frequency = fields.Str(
        required=True,
        validate=validate.OneOf([freq.value for freq in BillingFrequency])
    )
    
    