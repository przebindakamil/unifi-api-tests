from requests import Response
import time
import pytest


def get_voucher_by_name(r: Response, name: str):
    data = r.json()
    for v in data.get("data", []):
        if v.get("name") == name:
            return v
    return None


def wait_until_list_contains(api, ids, timeout_sec=3, interval_sec=0.5):
    end = time.time() + timeout_sec
    ids_set = set(ids)
    while time.time() < end:
        vouchers_resp = api.list_vouchers()
        if vouchers_resp.status_code == 200:
            listed_ids = {v["id"] for v in vouchers_resp.json().get("data", [])}
            if ids_set.issubset(listed_ids):
                return
        time.sleep(interval_sec)
    pytest.fail(f"Vouchers are not visible after {timeout_sec}s: {ids}")


def fetch_ids_by_name_with_poll(api, name, timeout_sec=10, interval_sec=0.5):
    end = time.time() + timeout_sec
    while time.time() < end:
        lr = api.list_vouchers()
        if lr.status_code == 200:
            ids = [v["id"] for v in lr.json().get("data", []) if v.get("name") == name]
            if ids:
                return ids
        time.sleep(interval_sec)
    return []
