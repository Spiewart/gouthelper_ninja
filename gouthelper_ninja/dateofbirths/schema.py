from ninja import ModelSchema

from gouthelper_ninja.dateofbirths.models import DateOfBirth


class DateOfBirthNestedSchema(ModelSchema):
    class Meta:
        model = DateOfBirth
        fields = ["dateofbirth"]


class DateOfBirthSchema(DateOfBirthNestedSchema):
    class Meta(DateOfBirthNestedSchema.Meta):
        fields = [
            *DateOfBirthNestedSchema.Meta.fields,
            "patient",
            "id",
        ]
