"""
ANORA-V2 Configuration
Semua konfigurasi dari environment variable
DENGAN WEBHOOK SUPPORT UNTUK RAILWAY
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


# =============================================================================
# DATABASE SETTINGS
# =============================================================================
class DatabaseSettings(BaseSettings):
    """Konfigurasi database"""
    model_config = SettingsConfigDict(env_prefix="DB_", extra="ignore")
    
    type: str = Field("sqlite", alias="DB_TYPE")
    path: Path = Field(Path("data/anora_v2.db"), alias="DB_PATH")
    
    @property
    def url(self) -> str:
        return f"sqlite+aiosqlite:///{self.path}"
    
    @field_validator('path', mode='before')
    @classmethod
    def validate_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v


# =============================================================================
# AI SETTINGS
# =============================================================================
class AISettings(BaseSettings):
    """Konfigurasi AI DeepSeek"""
    model_config = SettingsConfigDict(env_prefix="AI_", extra="ignore")
    
    temperature: float = Field(0.85, alias="AI_TEMPERATURE")
    max_tokens: int = Field(1200, alias="AI_MAX_TOKENS")
    timeout: int = Field(45, alias="AI_TIMEOUT")
    model: str = Field("deepseek-chat", alias="AI_MODEL")
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError(f'Temperature must be between 0 and 2, got {v}')
        return v


# =============================================================================
# WEBHOOK SETTINGS (UNTUK RAILWAY)
# =============================================================================
class WebhookSettings(BaseSettings):
    """Konfigurasi webhook untuk Railway"""
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")
    
    port: int = Field(8080, alias="PORT")
    path: str = Field("/webhook", alias="WEBHOOK_PATH")
    secret_token: Optional[str] = Field(None, alias="WEBHOOK_SECRET")
    railway_domain: Optional[str] = Field(None, alias="RAILWAY_PUBLIC_DOMAIN")
    railway_static_url: Optional[str] = Field(None, alias="RAILWAY_STATIC_URL")
    
    @property
    def url(self) -> Optional[str]:
        if self.railway_domain:
            return f"https://{self.railway_domain}{self.path}"
        if self.railway_static_url:
            return f"https://{self.railway_static_url}{self.path}"
        return None
    
    @property
    def is_railway(self) -> bool:
        return bool(self.railway_domain or self.railway_static_url)


# =============================================================================
# LOGGING SETTINGS
# =============================================================================
class LoggingSettings(BaseSettings):
    """Konfigurasi logging untuk Railway"""
    model_config = SettingsConfigDict(env_prefix="LOG_", extra="ignore")
    
    level: str = Field("INFO", alias="LOG_LEVEL")
    json_format: bool = Field(True, alias="LOG_JSON_FORMAT")
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}, got {v}')
        return v.upper()


# =============================================================================
# FEATURE SETTINGS
# =============================================================================
class FeatureSettings(BaseSettings):
    """Feature toggles untuk ANORA-V2"""
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")
    
    vulgar_mode_enabled: bool = Field(True, alias="VULGAR_MODE_ENABLED")
    aftercare_enabled: bool = Field(True, alias="AFTERCARE_ENABLED")
    flashback_enabled: bool = Field(True, alias="FLASHBACK_ENABLED")
    proactive_chat_enabled: bool = Field(True, alias="PROACTIVE_CHAT_ENABLED")
    auto_backup_enabled: bool = Field(True, alias="AUTO_BACKUP_ENABLED")


# =============================================================================
# MAIN SETTINGS CLASS
# =============================================================================
class Settings(BaseSettings):
    """
    ANORA-V2 - Virtual Human dengan Jiwa
    Main Settings with Railway Support
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ===== API KEYS (WAJIB) =====
    deepseek_api_key: str = Field(..., alias="DEEPSEEK_API_KEY")
    telegram_token: str = Field(..., alias="TELEGRAM_TOKEN")
    admin_id: int = Field(..., alias="ADMIN_ID")
    
    # ===== COMPONENT SETTINGS =====
    database: DatabaseSettings = DatabaseSettings()
    ai: AISettings = AISettings()
    webhook: WebhookSettings = WebhookSettings()
    logging: LoggingSettings = LoggingSettings()
    features: FeatureSettings = FeatureSettings()
    
    # ===== BASE DIRECTORY =====
    base_dir: Path = Path(__file__).parent
    
    # ===== VALIDATORS =====
    @field_validator('deepseek_api_key')
    @classmethod
    def validate_deepseek_key(cls, v):
        if not v or v == "your_deepseek_api_key_here":
            raise ValueError("DEEPSEEK_API_KEY tidak boleh kosong. Set di Railway Variables atau .env")
        if len(v) < 10:
            raise ValueError("DEEPSEEK_API_KEY seems invalid (too short)")
        return v
    
    @field_validator('telegram_token')
    @classmethod
    def validate_telegram_token(cls, v):
        if not v or v == "your_telegram_bot_token_here":
            raise ValueError("TELEGRAM_TOKEN tidak boleh kosong. Set di Railway Variables atau .env")
        return v
    
    @field_validator('admin_id')
    @classmethod
    def validate_admin_id(cls, v):
        if v == 0:
            logger.warning("⚠️ ADMIN_ID = 0. Admin commands won't work. Set from @userinfobot")
        return v
    
    # ===== HELPER METHODS =====
    def create_directories(self):
        """Create all necessary directories"""
        dirs = [
            Path("data"),
            Path("data/backups"),
            Path("data/memory"),
        ]
        for dir_path in dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Could not create directory {dir_path}: {e}")
        return self
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate all settings and return status"""
        status = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'railway_mode': self.webhook.is_railway
        }
        
        if not self.deepseek_api_key:
            status['valid'] = False
            status['errors'].append("DeepSeek API Key missing")
        
        if not self.telegram_token:
            status['valid'] = False
            status['errors'].append("Telegram Token missing")
        
        if self.admin_id == 0:
            status['warnings'].append("Admin ID not set")
        
        return status
    
    def log_configuration(self):
        """Log configuration to Railway console"""
        logger.info("=" * 70)
        logger.info("💜 ANORA-V2 - Configuration Loaded")
        logger.info("=" * 70)
        logger.info(f"🗄️  Database: {self.database.type} @ {self.database.path}")
        logger.info(f"🤖 AI Model: {self.ai.model} | Temperature: {self.ai.temperature}")
        logger.info(f"👑 Admin ID: {self.admin_id}")
        logger.info(f"🌍 Railway Mode: {self.webhook.is_railway}")
        if self.webhook.railway_domain:
            logger.info(f"🌐 Webhook URL: https://{self.webhook.railway_domain}{self.webhook.path}")
        logger.info(f"💋 Vulgar Mode: {'ON' if self.features.vulgar_mode_enabled else 'OFF'}")
        logger.info(f"💕 Aftercare Mode: {'ON' if self.features.aftercare_enabled else 'OFF'}")
        logger.info(f"💬 Proactive Chat: {'ON' if self.features.proactive_chat_enabled else 'OFF'}")
        logger.info(f"💾 Auto Backup: {'ON' if self.features.auto_backup_enabled else 'OFF'}")
        logger.info("=" * 70)


# =============================================================================
# GLOBAL SETTINGS INSTANCE
# =============================================================================

_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance with caching"""
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
            _settings.create_directories()
            _settings.log_configuration()
            
            status = _settings.validate_all()
            if not status['valid']:
                for err in status['errors']:
                    logger.error(f"❌ Configuration error: {err}")
                raise ValueError("Invalid configuration")
            
            for warn in status['warnings']:
                logger.warning(f"⚠️ {warn}")
                
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            raise
    
    return _settings


settings = get_settings()


__all__ = ['settings', 'get_settings', 'Settings']
