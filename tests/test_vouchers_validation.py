import uuid
import pytest


def assert_validation_error(resp):
    assert resp.status_code in (400, 422), f"Expected validation error, got {resp.status_code} {resp.text}"


@pytest.fixture
def base_payload():
    return {
        "count": 1,
        "name": f"e2e-validate-{uuid.uuid4().hex}",
        "authorizedGuestLimit": 1,
        "timeLimitMinutes": 10,
        "dataUsageLimitMBytes": 1,
        "rxRateLimitKbps": 2,
        "txRateLimitKbps": 2,
    }


@pytest.mark.parametrize("missing_field", ["timeLimitMinutes", "name"])
def test_missing_required_field(api, base_payload, missing_field):
    payload = dict(base_payload)
    payload.pop(missing_field)
    r = api.generate_vouchers(payload)
    assert_validation_error(r)


@pytest.mark.parametrize("field,bad_value", [
    ("count", "ten"),
    ("authorizedGuestLimit", "one"),
    ("timeLimitMinutes", True),
    ("dataUsageLimitMBytes", "1GB"),
    ("rxRateLimitKbps", "fast"),
    ("txRateLimitKbps", '100001'),
])
def test_wrong_types(api, base_payload, field, bad_value):
    payload = dict(base_payload)
    payload[field] = bad_value
    r = api.generate_vouchers(payload)
    assert_validation_error(r)


@pytest.mark.parametrize("field,bad_value", [
    ("count", 0),
    ("count", -1),
    ("authorizedGuestLimit", -1),
    ("timeLimitMinutes", 0),
    ("timeLimitMinutes", -5),
    ("dataUsageLimitMBytes", -1),
    ("rxRateLimitKbps", -100),
    ("txRateLimitKbps", -100),
])
def test_invalid_boundaries(api, base_payload, field, bad_value):
    payload = dict(base_payload)
    payload[field] = bad_value
    r = api.generate_vouchers(payload)
    assert_validation_error(r)
