import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.config import config

class WardrobeLocators:
    """Centralized UI locators for 'Спортивный Гардероб' Android app."""
    # Home Screen
    SEARCH_ICON_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "btn_nav_search")
    SEARCH_INPUT_FIELD = (AppiumBy.ID, f"{config.APPS['wardrobe'].app_package}:id/input_search_query")
    
    # Search Results
    SEARCH_RESULT_FIRST_ITEM = (AppiumBy.XPATH, f"//android.widget.TextView[contains(@resource-id, 'text_item_title')]")
    
    # Product Card
    BTN_ADD_TO_WARDROBE = (AppiumBy.ID, f"{config.APPS['wardrobe'].app_package}:id/btn_add_to_wardrobe")
    SNACKBAR_SUCCESS = (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'добавлен') or contains(@text, 'Добавлено')]")
    
    # Wardrobe Screen / Cart
    BTN_NAV_WARDROBE = (AppiumBy.ACCESSIBILITY_ID, "btn_nav_my_wardrobe")
    WARDROBE_ITEMS_LIST = (AppiumBy.ID, f"{config.APPS['wardrobe'].app_package}:id/recycler_wardrobe_items")


@pytest.mark.e2e
@pytest.mark.mobile
class TestWardrobeFlow:
    """E2E flow test for 'Спортивный Гардероб' mobile application."""

    def test_search_and_add_item_to_wardrobe(self, appium_driver):
        """
        Scenario:
        1. Open 'Спортивный Гардероб' app.
        2. Click Search button/field.
        3. Enter search term (e.g. 'Беговые кроссовки') and submit.
        4. Select first product card from search results.
        5. Click 'Добавить в гардероб' button.
        6. Verify item successfully added (confirmation toast/snackbar & item in wardrobe).
        """
        driver = appium_driver
        wait = WebDriverWait(driver, config.EXPLICIT_WAIT)

        # Step 1 & 2: Click on search button
        search_btn = wait.until(
            EC.element_to_be_clickable(WardrobeLocators.SEARCH_ICON_BUTTON),
            message="Search icon button not found on home screen"
        )
        search_btn.click()

        # Step 3: Type search query
        search_input = wait.until(
            EC.visibility_of_element_located(WardrobeLocators.SEARCH_INPUT_FIELD),
            message="Search query input field did not appear"
        )
        search_term = "Беговые кроссовки"
        search_input.clear()
        search_input.send_keys(search_term)
        
        # Trigger search on mobile keyboard (ENTER / Done)
        driver.execute_script("mobile: performEditorAction", {"action": "search"})

        # Step 4: Click on the first search result item
        first_product = wait.until(
            EC.element_to_be_clickable(WardrobeLocators.SEARCH_RESULT_FIRST_ITEM),
            message="No products found in search results"
        )
        selected_product_name = first_product.text
        first_product.click()

        # Step 5: Click 'Добавить в гардероб'
        add_btn = wait.until(
            EC.element_to_be_clickable(WardrobeLocators.BTN_ADD_TO_WARDROBE),
            message="'Добавить в гардероб' button is not clickable"
        )
        add_btn.click()

        # Step 6: Verify confirmation snackbar/toast
        success_toast = wait.until(
            EC.visibility_of_element_located(WardrobeLocators.SNACKBAR_SUCCESS),
            message="Success feedback message after adding item did not appear"
        )
        assert success_toast.is_displayed(), "Confirmation message is not displayed"

        # Step 7: Navigate to 'My Wardrobe' tab and check the item
        nav_wardrobe = wait.until(
            EC.element_to_be_clickable(WardrobeLocators.BTN_NAV_WARDROBE),
            message="My Wardrobe navigation tab not accessible"
        )
        nav_wardrobe.click()

        wardrobe_list = wait.until(
            EC.presence_of_element_located(WardrobeLocators.WARDROBE_ITEMS_LIST),
            message="Wardrobe items list container not found"
        )
        assert wardrobe_list.is_displayed(), "Wardrobe list container is not displayed"
        
        # Verify added item title appears in wardrobe list
        item_in_wardrobe = driver.find_elements(
            AppiumBy.XPATH,
            f"//android.widget.TextView[contains(@text, '{selected_product_name}')]"
        )
        assert len(item_in_wardrobe) > 0, (
            f"Item '{selected_product_name}' was not found in wardrobe collection"
        )
