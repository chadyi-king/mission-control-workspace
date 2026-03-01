import os
import importlib
import unittest


class TestRuntimeSecretsFallback(unittest.TestCase):
    def test_fallback_loads_runtime_secrets(self):
        # Preserve and clear env vars used by load_settings
        keys = [
            "OANDA_ENVIRONMENT",
            "OANDA_ACCOUNT_ID",
            "OANDA_API_KEY",
            "TELEGRAM_API_ID",
            "TELEGRAM_API_HASH",
            "TELEGRAM_PHONE",
        ]
        saved = {k: os.environ.pop(k, None) for k in keys}
        try:
            # Ensure runtime_secrets is importable from the quanta-v3 folder
            rs = importlib.import_module("runtime_secrets")
            importlib.reload(rs)

            # Import local config and call load_settings()
            cfg = importlib.import_module("config")
            settings = cfg.load_settings()

            # Basic sanity checks: values pulled from runtime_secrets should be present
            self.assertTrue(settings.oanda_account_id)
            self.assertTrue(settings.oanda_api_key)
            self.assertIn(settings.oanda_environment.upper(), {"LIVE", "PRACTICE"})
        finally:
            # restore environment
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v


if __name__ == "__main__":
    unittest.main()
