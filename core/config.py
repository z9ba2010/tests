import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
from appium.options.android import UiAutomator2Options

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

@dataclass(frozen=True)
class AppConfig:
    """Mobile app parameters."""
    app_package: str
    app_activity: str
    apk_path: str | None = None

class Config:
    """Central configuration for QA Hub."""
    
    # Environment
    ENV = os.getenv("TEST_ENV", "staging").lower()
    
    # Backend Services
    PARSER_API_BASE_URL = os.getenv(
        "PARSER_API_BASE_URL",
        "https://api.staging.internal/parser" if ENV == "staging" else "https://api.internal/parser"
    )
    API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "test-auth-token-xyz")
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))

    # Appium Server
    APPIUM_SERVER_URL = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
    DEVICE_NAME = os.getenv("DEVICE_NAME", "Android Emulator")
    PLATFORM_VERSION = os.getenv("PLATFORM_VERSION", "13.0")
    IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "10"))
    EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "15"))

    # Mobile Applications Registry
    APPS = {
        "wardrobe": AppConfig(
            app_package=os.getenv("WARDROBE_PACKAGE", "com.sportwardrobe.app"),
            app_activity=os.getenv("WARDROBE_ACTIVITY", "com.sportwardrobe.app.MainActivity"),
            apk_path=os.getenv("WARDROBE_APK", str(BASE_DIR / "apps" / "wardrobe.apk"))
        ),
        "maxfunfit": AppConfig(
            app_package=os.getenv("MAXFUNFIT_PACKAGE", "com.maxfunfit.app"),
            app_activity=os.getenv("MAXFUNFIT_ACTIVITY", "com.maxfunfit.app.MainActivity"),
            apk_path=os.getenv("MAXFUNFIT_APK", str(BASE_DIR / "apps" / "maxfunfit.apk"))
        ),
        "matreshka": AppConfig(
            app_package=os.getenv("MATRESHKA_PACKAGE", "com.matreshka.app"),
            app_activity=os.getenv("MATRESHKA_ACTIVITY", "com.matreshka.app.MainActivity"),
            apk_path=os.getenv("MATRESHKA_APK", str(BASE_DIR / "apps" / "matreshka.apk"))
        ),
    }

    @classmethod
    def get_android_options(cls, app_key: str = "wardrobe") -> UiAutomator2Options:
        """Construct UiAutomator2Options for modern Appium 2.x."""
        app = cls.APPS.get(app_key)
        if not app:
            raise ValueError(f"Application '{app_key}' not found in registry. Options: {list(cls.APPS.keys())}")

        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = cls.DEVICE_NAME
        options.platform_version = cls.PLATFORM_VERSION
        options.automation_name = "UiAutomator2"
        options.app_package = app.app_package
        options.app_activity = app.app_activity
        options.no_reset = False
        options.auto_grant_permissions = True
        
        # If APK file exists locally, pass it for installation; otherwise use installed app
        if app.apk_path and Path(app.apk_path).is_file():
            options.app = app.apk_path
            
        return options

config = Config()
