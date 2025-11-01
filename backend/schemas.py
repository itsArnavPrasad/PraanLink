from marshmallow import Schema, fields, validate
from datetime import datetime


class CheckInSchema(Schema):
    id = fields.Int(dump_only=True)
    recording_path = fields.Str(required=True)
    recording_transcript = fields.Dict(allow_none=True)
    summary = fields.Str(allow_none=True)
    timestamp = fields.DateTime(dump_only=True)


class PrescriptionSchema(Schema):
    id = fields.Int(dump_only=True)
    file_path = fields.Str(required=True)
    summary = fields.Str(allow_none=True)
    timestamp = fields.DateTime(dump_only=True)


class ReportSchema(Schema):
    id = fields.Int(dump_only=True)
    file_path = fields.Str(required=True)
    summary = fields.Str(allow_none=True)
    timestamp = fields.DateTime(dump_only=True)


class HospitalSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    speciality = fields.Str(required=True)
    location = fields.Str(required=True)
    reviews = fields.Float(allow_none=True)
    contact_info = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)


class InsuranceSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    coverage = fields.Str(required=True)
    premium = fields.Float(required=True, validate=validate.Range(min=0))
    key_features = fields.Dict(allow_none=True)
    provider = fields.Str(required=True)

