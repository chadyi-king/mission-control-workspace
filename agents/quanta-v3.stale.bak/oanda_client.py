from typing import Dict, List, Optional
import requests
import time
import uuid


class OandaClient:
    def __init__(self, account_id: str, api_key: str, base_url: str, dry_run: bool = False):
        self.account_id = account_id
        self.base_url = base_url.rstrip("/")
        self.dry_run = bool(dry_run)
        # when dry_run, avoid creating a real session to prevent accidental HTTP calls in tests
        if not self.dry_run:
            self.session = requests.Session()
            self.session.headers.update({"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
        else:
            self.session = None

    def _normalize_instrument(self, instrument: str) -> str:
        """Normalize common instrument aliases to OANDA format."""
        value = (instrument or "").strip().upper()
        aliases = {
            "XAUUSD": "XAU_USD",
            "XAGUSD": "XAG_USD",
            "EURUSD": "EUR_USD",
            "GBPUSD": "GBP_USD",
            "USDJPY": "USD_JPY",
        }
        if value in aliases:
            return aliases[value]
        if "_" in value:
            return value
        if len(value) == 6 and value.isalpha():
            return f"{value[:3]}_{value[3:]}"
        return value

    def get_account_summary(self) -> Dict:
        if self.dry_run:
            return {"accountID": self.account_id, "balance": "10000.00", "simulated": True}
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/summary"
            res = self.session.get(url, timeout=20)
            res.raise_for_status()
            return res.json().get("account", {})
        except Exception:
            raise

    def get_price(self, instrument: str) -> float:
        instrument = self._normalize_instrument(instrument)
        if self.dry_run:
            # return a safe default simulated price
            return 1.2345
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
        """
        If dry_run=True, return a simulated order response and do not perform HTTP calls.
        """
        instrument = self._normalize_instrument(instrument)
        if self.dry_run:
            return {
                "orderCreateTransaction": {
                    "id": f"DRY-{uuid.uuid4()}",
                    "instrument": instrument,
                    "units": str(units),
                    "type": "MARKET",
                    "clientExtensions": {"tag": client_tag},
                },
                "relatedTransactionIDs": [],
                "lastTransactionID": f"DRY-{int(time.time())}",
                "success": True,
                "simulated": True,
            }
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

    def create_limit_order(
        self,
        instrument: str,
        units: int,
        price: float,
        stop_loss: float,
        client_tag: str,
    ) -> Dict:
        """
        If dry_run=True, return a simulated LIMIT order response and do not perform HTTP calls.
        """
        instrument = self._normalize_instrument(instrument)
        if self.dry_run:
            return {
                "orderCreateTransaction": {
                    "id": f"DRY-{uuid.uuid4()}",
                    "instrument": instrument,
                    "units": str(units),
                    "type": "LIMIT",
                    "price": f"{price:.3f}",
                    "clientExtensions": {"tag": client_tag},
                },
                "relatedTransactionIDs": [],
                "lastTransactionID": f"DRY-{int(time.time())}",
                "success": True,
                "simulated": True,
            }
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/orders"
            payload = {
                "order": {
                    "type": "LIMIT",
                    "instrument": instrument,
                    "units": str(units),
                    "timeInForce": "GTC",
                    "positionFill": "DEFAULT",
                    "price": f"{price:.3f}",
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
        if self.dry_run:
            return {"closedUnits": units, "tradeID": trade_id, "simulated": True}
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/trades/{trade_id}/close"
            res = self.session.put(url, json={"units": units}, timeout=20)
            res.raise_for_status()
            return res.json()
        except Exception:
            raise

    def update_trade_sl(self, trade_id: str, sl_price: float) -> Dict:
        if self.dry_run:
            return {"tradeID": trade_id, "stopLossPrice": f"{sl_price:.3f}", "simulated": True}
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/trades/{trade_id}/orders"
            payload = {"stopLoss": {"price": f"{sl_price:.3f}"}}
            res = self.session.put(url, json=payload, timeout=20)
            res.raise_for_status()
            return res.json()
        except Exception:
            raise

    def list_open_trades(self) -> List[Dict]:
        if self.dry_run:
            return []
        try:
            url = f"{self.base_url}/v3/accounts/{self.account_id}/openTrades"
            res = self.session.get(url, timeout=20)
            res.raise_for_status()
            return res.json().get("trades", [])
        except Exception:
            raise

    def get_trade_ids_by_tag_prefix(self, tag_prefix: str) -> List[str]:
        """
        Return trade IDs of all open trades whose client extension tag starts
        with tag_prefix.  Used to resolve filled limit-order IDs → trade IDs.
        e.g. tag_prefix="qv3-52654" matches tags qv3-52654-tier1/tier2/tier3.
        """
        if self.dry_run:
            return []
        try:
            trades = self.list_open_trades()
            result = []
            for t in trades:
                tag = (t.get("clientExtensions") or {}).get("tag", "")
                if tag.startswith(tag_prefix):
                    result.append(str(t["id"]))
            return result
        except Exception:
            raise
