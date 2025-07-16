import uuid

from gouthelper_ninja.goutdetails.schema import GoutDetailEditSchema
from gouthelper_ninja.goutdetails.schema import GoutDetailSchema


class TestGoutDetailEditSchema:
    def test_defaults(self):
        schema = GoutDetailEditSchema()
        assert schema.at_goal is None
        assert schema.at_goal_long_term is False
        assert schema.flaring is None
        assert schema.on_ppx is False
        assert schema.on_ult is False
        assert schema.starting_ult is False

    def test_values(self):
        schema = GoutDetailEditSchema(
            at_goal=True,
            at_goal_long_term=True,
            flaring=True,
            on_ppx=True,
            on_ult=True,
            starting_ult=True,
        )
        assert schema.at_goal is True
        assert schema.at_goal_long_term is True
        assert schema.flaring is True
        assert schema.on_ppx is True
        assert schema.on_ult is True
        assert schema.starting_ult is True


class TestGoutDetailSchema:
    def test_inherits_and_accepts_patient_id(self):
        patient_uuid = uuid.uuid4()
        gout_detail_uuid = uuid.uuid4()
        schema = GoutDetailSchema(
            at_goal=True,
            at_goal_long_term=False,
            flaring=False,
            on_ppx=True,
            on_ult=False,
            starting_ult=False,
            patient_id=patient_uuid,
            id=gout_detail_uuid,
        )
        assert schema.at_goal is True
        assert schema.patient_id == patient_uuid
        assert schema.id == gout_detail_uuid

    def test_config_example(self):
        example = GoutDetailSchema.Config.json_schema_extra["example"]
        assert example["at_goal"] is True
        assert example["patient_id"] == "patient_id"
        assert example["id"] == "gout_detail_id"
