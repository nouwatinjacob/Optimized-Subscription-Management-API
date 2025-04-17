from marshmallow import Schema, fields, validate
from decimal import Decimal

class PlanSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    description = fields.Str(required=True, validate=validate.Length(min=5, max=255))
    price = fields.Decimal(as_string=True, required=True, validate=validate.Range(min=Decimal("0.00")))
    
class ListPlanSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str()
    price = fields.Decimal(as_string=True, places=2)
    created_at = fields.DateTime(dump_only=True)