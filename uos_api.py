from pathlib import Path
from urllib.parse import urljoin

import requests
import yaml

CONFIG_PATH = Path(__file__).parent / "config/uos.yaml"


class UOSApi:
    def __init__(self, config_path: str = CONFIG_PATH):
        self.cfg = self._load_config(config_path)
        self.s = self._init_session()
        self.base = self.cfg["base_url"].rstrip("/")
        self.site = self.cfg["site_id"]
        self.url = f"{self.base}/proxy/network/integration/v1/sites/{self.site}/hotspot/vouchers"

    @staticmethod
    def _load_config(path: str):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _init_session(self):
        s = requests.Session()
        token = self.cfg["api_token"]
        s.headers.update({'Accept': 'application/json', 'X-API-Key': f'{token}'})
        s.verify = bool(self.cfg.get("verify_ssl", True))
        return s

    def list_vouchers(self):
        return self.s.get(self.url)

    def generate_vouchers(self, payload: dict):
        print(self.url)
        print(payload)
        return self.s.post(self.url, json=payload)

    def get_voucher(self, voucher_id: str):
        url = urljoin(self.url, voucher_id)
        return self.s.get(url)

    def delete_voucher(self, voucher_id: str):
        url = urljoin(self.url,f"vouchers/{voucher_id}")
        print(url)
        return self.s.delete(url)
