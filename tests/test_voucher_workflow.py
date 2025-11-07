import pytest

from helpers.vouchers import wait_until_list_contains, fetch_ids_by_name_with_poll


@pytest.fixture
def unique_name():
    import uuid
    return f"uos-{uuid.uuid4().hex}"


@pytest.fixture
def voucher_payload(unique_name):
    return {
        "count": 1,
        "name": unique_name,
        "authorizedGuestLimit": 1,
        "timeLimitMinutes": 10,
        "dataUsageLimitMBytes": 1,
        "rxRateLimitKbps": 2,
        "txRateLimitKbps": 2,
    }


@pytest.fixture
def created_vouchers(api, voucher_payload, request):
    resp = api.generate_vouchers(voucher_payload)
    assert resp.status_code == 201, f"Create failed: {resp.status_code} {resp.text}"

    data = resp.json()
    ids = [v["id"] for v in data.get("data", [])] if isinstance(data, dict) else []
    if not ids:
        ids = fetch_ids_by_name_with_poll(api, voucher_payload["name"])

    assert len(ids) == voucher_payload["count"], (
        f"Expected {voucher_payload['count']} vouchers, got {len(ids)}"
    )

    wait_until_list_contains(api, ids, timeout_sec=10)
    yield ids

    for vid in ids:
        try:
            del_resp = api.delete_voucher(vid)
            if del_resp.status_code not in (200, 204):
                pass
        except Exception:
            pass


def test_create_vouchers_returns_valid_payload(api, voucher_payload):
    resp = api.generate_vouchers(voucher_payload)
    assert resp.status_code == 201, f"Unexpected status: {resp.status_code} {resp.text}"
    body = resp.json()
    assert isinstance(body, dict), "Response should be JSON object"
    vouchers = body.get("vouchers", [])
    assert len(vouchers) == voucher_payload["count"], (
        f"Expected {voucher_payload['count']} vouchers, got {len(vouchers)}"
    )
    for v in vouchers:
        assert {"id", "name"} <= v.keys(), f"Missing fields in voucher: {v}"
        assert v["name"] == voucher_payload["name"], "Wrong name in created voucher"


def test_list_contains_created_vouchers(api, created_vouchers):
    resp = api.list_vouchers()
    assert resp.status_code == 200, f"List failed: {resp.status_code} {resp.text}"
    listed_ids = {v["id"] for v in resp.json().get("data", [])}
    missing = set(created_vouchers) - listed_ids
    assert not missing, f"Missing vouchers on list: {missing}"


def test_delete_single_voucher_and_verify_absence(api, created_vouchers):
    voucher_id = created_vouchers[0]
    del_resp = api.delete_voucher(voucher_id)
    assert del_resp.status_code == 200, f"Delete failed: {del_resp.status_code} {del_resp.text}"
    body = del_resp.json()
    assert body.get("vouchersDeleted", 0) == 1, f"Delete counter mismatch: {body}"

    listed_vouchers_resp = api.list_vouchers()
    assert listed_vouchers_resp.status_code == 200
    listed_ids = {v["id"] for v in listed_vouchers_resp.json().get("data", [])}
    assert voucher_id not in listed_ids, f"Voucher {voucher_id} still listed after deletion"
