# tests/conftest.py
import logging
import os

import pytest
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    filename="test.log",
    filemode="w",
    format="%(asctime)s %(relativeCreated)6d %(levelname)s %(threadName)s %(message)s",
)

def pytest_addoption(parser):
    parser.addoption("--env-file", action="store", default=".env")

@pytest.fixture(scope="session", autouse=True)
def load_env(request: pytest.FixtureRequest):
    env_file = request.config.getoption("--env-file")
    logging.info(f"Loading environment from {env_file}")
    load_dotenv(env_file)

@pytest.fixture(scope="session")
def config():
    test_device_addresses = os.getenv("TEST_DEVICE_ADDRESSES", "").split(" ")
    return {
        "test_device_addresses": test_device_addresses,
    }
