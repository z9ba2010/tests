import base64
import pytest
import requests
from appium import webdriver
from core.config import config

def pytest_addoption(parser):
    """CLI options for pytest execution."""
    parser.addoption(
        "--app",
        action="store",
        default="wardrobe",
        help="Mobile app target: wardrobe, maxfunfit, matreshka"
    )
    parser.addoption(
        "--env",
        action="store",
        default="staging",
        help="Test environment: staging, production"
    )

@pytest.fixture(scope="session")
def test_env(request):
    """Return selected test environment."""
    return request.config.getoption("--env")

@pytest.fixture(scope="session")
def api_session():
    """
    HTTP session fixture for API tests.
    Pre-configures default headers, authorization token, and base connection pooling.
    """
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {config.API_AUTH_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "QA-Hub-Automation/1.0 (Lead: Igor)"
    })
    
    yield session
    
    session.close()

@pytest.fixture(scope="function")
def appium_driver(request):
    """
    Appium WebDriver fixture for mobile Android testing (Appium 2.x).
    Instantiates UiAutomator2 session and guarantees cleanup on teardown.
    """
    app_key = request.config.getoption("--app")
    options = config.get_android_options(app_key=app_key)
    
    driver = webdriver.Remote(
        command_executor=config.APPIUM_SERVER_URL,
        options=options
    )
    driver.implicitly_wait(config.IMPLICIT_WAIT)
    
    # Store driver in node for screenshot-on-failure hook
    request.node.driver = driver

    yield driver

    driver.quit()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook: on failure, capture mobile screenshot and embed in pytest-html report.
    """
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])

    if report.when == "call" and report.failed:
        driver = getattr(item, "driver", None)
        if driver:
            try:
                screenshot_base64 = driver.get_screenshot_as_base64()
                html = f'<div><img src="data:image/png;base64,{screenshot_base64}" style="width:300px;height:auto;border:1px solid #ccc;" align="right"/></div>'
                
                # Check if pytest-html plugin is active
                pytest_html = item.config.pluginmanager.getplugin("html")
                if pytest_html is not None:
                    extra.append(pytest_html.extras.html(html))
            except Exception as e:
                # Driver might already be closed or unresponsive
                print(f"Failed to capture screenshot: {e}")
                
        report.extra = extra
