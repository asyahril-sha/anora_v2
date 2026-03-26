"""
ANORA-V2 Configuration
Semua konfigurasi dari environment variable
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class WebhookConfig:
    """Webhook configuration"""
    port: int = int(os.getenv("WEBHOOK_PORT", "8000"))
    path: str = os.getenv("WEBHOOK_PATH", "/webhook")
    railway_domain: str = os.getenv("RAILWAY_DOMAIN", "")
    railway_static_url: str = os.getenv("RAILWAY_STATIC_URL", "")


@dataclass
class Settings:
    """Main settings for ANORA-V2"""
    telegram_token: str = os.getenv("TELEGRAM_TOKEN", "")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    admin_id: int = int(os.getenv("ADMIN_ID", "0"))
    webhook: WebhookConfig = WebhookConfig()


_settings: Settings = None


def get_settings() -> Settings:
    """Get singleton settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
