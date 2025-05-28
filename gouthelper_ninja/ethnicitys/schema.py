from ninja import ModelSchema

from gouthelper_ninja.ethnicitys.models import Ethnicity


class EthnicityNestedSchema(ModelSchema):
    class Meta:
        model = Ethnicity
        fields = ["ethnicity"]


class EthnicitySchema(EthnicityNestedSchema):
    class Meta(EthnicityNestedSchema.Meta):
        fields = [
            *EthnicityNestedSchema.Meta.fields,
            "patient",
            "id",
            "created",
            "modified",
        ]
