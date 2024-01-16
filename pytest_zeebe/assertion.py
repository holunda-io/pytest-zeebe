import threading

from pytest_zeebe.assertions.process_instance_assert import ProcessInstanceAssert
from pytest_zeebe.client.client_grpc.pytest_zeebe_gateway_pb2 import CreateProcessInstanceResponse

local = threading.local()


def assert_that(process_instance: CreateProcessInstanceResponse):
    engine = local.zeebe_test_engine
    engine.wait_for_idle_state()
    return ProcessInstanceAssert(
        process_instance.processInstanceKey,
        engine.get_records()
    )




