from pytest_zeebe.fixtures import zeebe_test_client, zeebe_test_engine, _engine, _container

import pytest

from pytest_zeebe.assertion import assert_that
from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient


@pytest.fixture(autouse=True)
def deploy(zeebe_test_client: ZeebeTestClient):
    zeebe_test_client.deploy_process("test.bpmn")


def test_happy_path(zeebe_test_client: ZeebeTestClient):
    # given
    variables = {
        "var": "A"
    }

    # when
    # -> start
    process_instance = zeebe_test_client.create_process_instance("TestProcess", variables=variables)

    # -> complete Task A
    zeebe_test_client.complete_task("taskA")

    assert_that(process_instance).is_waiting_at_elements("TaskC")

    # -> complete Task C
    zeebe_test_client.complete_task("taskC", variables={"resultC": True})

    # then
    assert_that(process_instance) \
        .is_completed() \
        .has_passed_elements_in_order("StartEvent_1", "TaskA", "TaskC", "EndEvent_1") \
        .has_variable_with_value("var", "A") \
        .has_variable_with_value("resultC", True) \
        .has_no_incidents()
