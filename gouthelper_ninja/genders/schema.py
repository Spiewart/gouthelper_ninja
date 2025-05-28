from ninja import ModelSchema

from gouthelper_ninja.genders.models import Gender


class GenderNestedSchema(ModelSchema):
    class Meta:
        model = Gender
        fields = ["gender"]


class GenderSchema(GenderNestedSchema):
    class Meta(GenderNestedSchema.Meta):
        fields = [
            *GenderNestedSchema.Meta.fields,
            *[
                "patient",
                "id",
                "created",
                "modified",
            ],
        ]
