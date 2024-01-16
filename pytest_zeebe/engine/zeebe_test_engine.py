import json

import grpc

from pytest_zeebe.engine.engine_control_grpc import pytest_zeebe_engine_control_pb2, \
    pytest_zeebe_engine_control_pb2_grpc
from pytest_zeebe.engine.engine_control_grpc.pytest_zeebe_engine_control_pb2_grpc import EngineControlStub


class ZeebeTestEngine:

    def __init__(self, host, control_port, engine_port):
        self.host = host
        self.control_port = control_port
        self.engine_port = engine_port

    def _control_channel(self) -> grpc.Channel:
        return grpc.insecure_channel(f'{self.host}:{self.control_port}')

    def start(self):
        with self._control_channel() as channel:
            stub = _create_stub(channel)
            stub.StartEngine(pytest_zeebe_engine_control_pb2.StartEngineRequest())

    def stop(self):
        with self._control_channel() as channel:
            stub = _create_stub(channel)
            stub.StopEngine(pytest_zeebe_engine_control_pb2.StopEngineRequest())

    def reset(self):
        with self._control_channel() as channel:
            stub = _create_stub(channel)
            stub.ResetEngine(pytest_zeebe_engine_control_pb2.ResetEngineRequest())

    def wait_for_idle_state(self, timeout_seconds: int = 60):
        with self._control_channel() as channel:
            stub = _create_stub(channel)
            stub.WaitForIdleState(pytest_zeebe_engine_control_pb2.WaitForIdleStateRequest(timeout=timeout_seconds * 1000))

    def get_records(self):
        records = []
        with self._control_channel() as channel:
            stub = _create_stub(channel)
            for r in stub.GetRecords(pytest_zeebe_engine_control_pb2.GetRecordsRequest()):
                records.append(json.loads(r.recordJson))
        return records


def _create_stub(channel: grpc.Channel) -> EngineControlStub:
    return pytest_zeebe_engine_control_pb2_grpc.EngineControlStub(channel)
