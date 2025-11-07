import pytest

import yaml
import requests
from pathlib import Path

from uos_api import UOSApi


@pytest.fixture(scope="session")
def api():
    return UOSApi()


@pytest.fixture(scope="session")
def config():
    path = Path(__file__).parent.parent / "config/uos.yaml"
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data

@pytest.fixture(scope="session")
def auth_header(config):
    token = config["api_token"]
    return {'Accept': 'application/json', 'X-API-Key': f'{token}'}


@pytest.fixture(scope="session")
def verify_ssl(config):
    return bool(config.get("verify_ssl", True))


@pytest.fixture(scope="session")
def http(auth_header, verify_ssl):
    """Zwraca gotową sesję z autoryzacją"""
    s = requests.Session()
    s.headers.update(auth_header)
    s.verify = verify_ssl
    yield s
    s.close()
