from typing import Dict, List
import requests


class OandaClient:
    def __init__(self, account_id: str, api_key: str, base_url: str):
        self.account_id = account_id
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})

    def get_account_summary(self) -> Dict:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/summary"
            res = self.session.get(url, timeout=20)
            res.raise_for_status()
            return res.json().get("account", {})
        except Exception:
            raise

    def get_price(self, instrument: str) -> float:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/pricing"
            res = self.session.get(url, params={"instruments": instrument}, timeout=20)
            res.raise_for_status()
            price = res.json().get("prices", [])[0]
            bid = float(price["bids"][0]["price"])
            ask = float(price["asks"][0]["price"])
            return (bid + ask) / 2
        except Exception:
            raise

    def create_market_order(self, instrument: str, units: int, stop_loss: float, client_tag: str) -> Dict:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/orders"
            payload = {
                "order": {
                    "type": "MARKET",
                    "instrument": instrument,
                    "units": str(units),
                    "timeInForce": "FOK",
                    "positionFill": "DEFAULT",
                    "clientExtensions": {"tag": client_tag},
                    "stopLossOnFill": {"price": f"{stop_loss:.3f}"},
                }
            }
            res = self.session.post(url, json=payload, timeout=20)
            res.raise_for_status()
            return res.json()
        except Exception:
            raise

    def close_trade_units(self, trade_id: str, units: str) -> Dict:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/trades/{trade_id}/close"
            res = self.session.put(url, json={"units": units}, timeout=20)
            res.raise_for_status()
            return res.json()
        except Exception:
            raise

    def update_trade_sl(self, trade_id: str, sl_price: float) -> Dict:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/trades/{trade_id}/orders"
            payload = {"stopLoss": {"price": f"{sl_price:.3f}"}}
            res = self.session.put(url, json=payload, timeout=20)
            res.raise_for_status()
            return res.json()
        except Exception:
            raise

    def list_open_trades(self) -> List[Dict]:
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/openTrades"
            res = self.session.get(url, timeout=20)
            res.raise_for_status()
            return res.json().get("trades", [])
        except Exception:
            raise
