import logging
import os

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

from pytest_zeebe.assertion import local
from pytest_zeebe.client.zeebe_test_client import ZeebeTestClient
from pytest_zeebe.engine.zeebe_test_engine import ZeebeTestEngine

logger = logging.getLogger(__name__)

DEFAULT_ZEEBE_TEST_IMAGE = "camunda/zeebe-process-test-engine"
DEFAULT_ZEEBE_TEST_IMAGE_TAG = "latest"

AGENT_PORT = 26501
ENGINE_PORT = 26500

LOG_READY_PREDICATE = "ZeebeProcessTestEngine container has started"


@pytest.fixture(scope="module")
def _container():
    image = os.environ.get("ZEEBE_TEST_IMAGE", DEFAULT_ZEEBE_TEST_IMAGE)
    tag = os.environ.get("ZEEBE_TEST_IMAGE_TAG", DEFAULT_ZEEBE_TEST_IMAGE_TAG)
    container = DockerContainer(f"{image}:{tag}")
    container.with_exposed_ports(AGENT_PORT, ENGINE_PORT)
    container.start()

    wait_for_logs(container, LOG_READY_PREDICATE)
    logger.info("Zeebe container ready")

    yield container

    logger.info("Shutting down zeebe container")
    container.stop()


@pytest.fixture(scope="module")
def _engine(_container):
    engine = ZeebeTestEngine(
        _container.get_container_host_ip(),
        str(_container.get_exposed_port(26501)),
        str(_container.get_exposed_port(26500))
    )
    local.zeebe_test_engine = engine
    return engine


@pytest.fixture
def zeebe_test_engine(_engine):
    logger.info(f"Starting zeebe engine at {_engine.host}:{_engine.engine_port}")
    _engine.start()

    yield _engine

    logger.info("Resetting zeebe engine")
    _engine.reset()


@pytest.fixture
def zeebe_test_client(zeebe_test_engine):
    logger.info("Creating zeebe client")
    client = ZeebeTestClient(zeebe_test_engine)

    yield client

    client.stop()
