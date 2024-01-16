import json
import logging
import os
from typing import Tuple

import grpc

from pytest_zeebe.client.client_grpc.pytest_zeebe_gateway_pb2 import CreateProcessInstanceRequest, \
    CreateProcessInstanceWithResultRequest, CancelProcessInstanceRequest, DeployProcessResponse, DeployResourceRequest, \
    Resource, PublishMessageResponse, PublishMessageRequest, \
    BroadcastSignalResponse, BroadcastSignalRequest, EvaluateDecisionRequest, EvaluateDecisionResponse, \
    ActivateJobsRequest, ActivatedJob, CompleteJobRequest, CompleteJobResponse, \
    ThrowErrorResponse, ThrowErrorRequest, FailJobResponse, FailJobRequest, CreateProcessInstanceResponse
from pytest_zeebe.client.client_grpc.pytest_zeebe_gateway_pb2_grpc import GatewayStub
from pytest_zeebe.engine.zeebe_test_engine import ZeebeTestEngine

logger = logging.getLogger(__name__)


class ZeebeTestClient:

    def __init__(self, engine: ZeebeTestEngine) -> None:
        self.engine = engine
        self._channel = grpc.insecure_channel(f"{engine.host}:{engine.engine_port}")
        self._gateway_stub = GatewayStub(self._channel)

    def stop(self):
        try:
            self._channel.close()
        except Exception as exception:
            logger.exception("Failed to close channel, %s exception was raised", type(exception).__name__)

    def create_process_instance(
            self,
            bpmn_process_id: str,
            version: int = -1,
            variables: dict | None = None
    ) -> CreateProcessInstanceResponse:
        return self._gateway_stub.CreateProcessInstance(
            CreateProcessInstanceRequest(
                bpmnProcessId=bpmn_process_id,
                version=version,
                variables=json.dumps(variables)
            )
        )

    def create_process_instance_with_result(
            self,
            bpmn_process_id: str,
            version: int = -1,
            variables: dict | None = None,
            timeout: int = 0,
            variables_to_fetch: list | None = None
    ) -> Tuple[int, dict]:
        response = self._gateway_stub.CreateProcessInstanceWithResult(
            CreateProcessInstanceWithResultRequest(
                request=CreateProcessInstanceRequest(
                    bpmnProcessId=bpmn_process_id,
                    version=version,
                    variables=json.dumps(variables or {})
                ),
                requestTimeout=timeout,
                fetchVariables=variables_to_fetch or [],
            )
        )
        return response.processInstanceKey, json.loads(response.variables)

    def cancel_process_instance(self, process_instance_key: int) -> None:
        self._gateway_stub.CancelProcessInstance(
            CancelProcessInstanceRequest(
                processInstanceKey=process_instance_key
            )
        )

    def deploy_process(self, *process_file_path: str) -> DeployProcessResponse:
        return self._gateway_stub.DeployResource(
            DeployResourceRequest(
                resources=[result for result in map(_create_resource, process_file_path)]
            )
        )

    def publish_message(
            self,
            name: str,
            correlation_key: str,
            time_to_live_in_milliseconds: int = 60000,
            variables: dict | None = None,
            message_id: str | None = None,
    ) -> PublishMessageResponse:
        return self._gateway_stub.PublishMessage(
            PublishMessageRequest(
                name=name,
                correlationKey=correlation_key,
                messageId=message_id,
                timeToLive=time_to_live_in_milliseconds,
                variables=json.dumps(variables or {}),
            )
        )

    def broadcast_signal(self, name: str, variables: dict | None = None) -> BroadcastSignalResponse:
        return self._gateway_stub.BroadcastSignal(
            BroadcastSignalRequest(
                signalName=name,
                variables=json.dumps(variables or {}),
            )
        )

    def evaluate_decision(
            self,
            decision_key: int,
            decision_id: str,
            variables: dict | None = None
    ) -> EvaluateDecisionResponse:
        return self._gateway_stub.EvaluateDecision(
            EvaluateDecisionRequest(
                decisionKey=decision_key,
                decisionId=decision_id,
                variables=json.dumps(variables or {}),
            )
        )

    def complete_task(self, task_type: str, variables: dict | None = None):
        jobs = self._activate_jobs(task_type)
        if not jobs:
            raise Exception(f"No jobs found for task type {task_type}")
        for job in jobs:
            self._complete_job(job.key, variables)
        self.engine.wait_for_idle_state()

    def complete_user_task(self, element_id: str, variables: dict | None = None):
        user_tasks = self._activate_jobs(
            'io.camunda.zeebe:userTask',
            max_jobs_to_activate=100
        )
        for user_task in user_tasks:
            if user_task.elementId == element_id:
                self._complete_job(user_task.key, variables)
            else:
                self._fail_job(user_task.key, retries=max(user_task.retries, 1))
        self.engine.wait_for_idle_state()

    def _activate_jobs(
            self,
            task_type: str,
            worker: str = "zeebe_test_worker",
            timeout: int = 60000,
            max_jobs_to_activate: int = 1,
            variables_to_fetch: list[str] | None = None,
            request_timeout: int = 0,
    ) -> list[ActivatedJob]:
        for response in self._gateway_stub.ActivateJobs(
                ActivateJobsRequest(
                    type=task_type,
                    worker=worker,
                    timeout=timeout,
                    maxJobsToActivate=max_jobs_to_activate,
                    fetchVariable=variables_to_fetch,
                    requestTimeout=request_timeout,
                )
        ):
            return response.jobs

    def _complete_job(self, job_key: int, variables: dict | None = None) -> CompleteJobResponse:
        return self._gateway_stub.CompleteJob(
            CompleteJobRequest(
                jobKey=job_key,
                variables=json.dumps(variables or {})
            )
        )

    def _fail_job(self, job_key: int, retries: int, message: str | None = None) -> FailJobResponse:
        return self._gateway_stub.FailJob(
            FailJobRequest(
                jobKey=job_key,
                retries=retries,
                errorMessage=message
            )
        )

    def _throw_error(self, job_key: int, error_code: str, message: str = "") -> ThrowErrorResponse:
        return self._gateway_stub.ThrowError(
            ThrowErrorRequest(
                jobKey=job_key,
                errorMessage=message,
                errorCode=error_code
            )
        )


def _create_resource(process_file_path: str) -> Resource:
    with open(process_file_path, "rb") as file:
        return Resource(name=os.path.basename(process_file_path), content=file.read())
