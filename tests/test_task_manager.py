import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TaskManagerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.driver.get("http://localhost:5000")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def login(self, username="testuser", password="testpass"):
        self.driver.get("http://localhost:5000/login")
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait.until(EC.url_contains("/dashboard"))

    def test_1_home_page_load(self):
        self.assertIn("Task Manager", self.driver.title)

    def test_2_navigate_to_register(self):
        self.driver.get("http://localhost:5000")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        register_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/register']")))
        register_btn.click()
        self.wait.until(EC.url_contains("/register"))
        self.assertIn("/register", self.driver.current_url)

    def test_3_user_registration(self):
        self.driver.get("http://localhost:5000/register")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        self.driver.find_element(By.NAME, "username").send_keys("testuser")
        self.driver.find_element(By.NAME, "password").send_keys("testpass")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_4_duplicate_user_registration(self):
        self.driver.get("http://localhost:5000/register")
        self.driver.find_element(By.NAME, "username").send_keys("testuser")
        self.driver.find_element(By.NAME, "password").send_keys("testpass")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        error_message = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Username already exists')]"))
        )
        self.assertIn("Username already exists", error_message.text)

    def test_5_navigate_to_login(self):
        self.driver.get("http://localhost:5000")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "button-group")))
        login_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-success")))
        login_btn.click()
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

    def test_6_successful_login(self):
        self.driver.get("http://localhost:5000/login")
        self.driver.find_element(By.NAME, "username").send_keys("testuser")
        self.driver.find_element(By.NAME, "password").send_keys("testpass")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait.until(EC.url_contains("/dashboard"))
        self.assertIn("/dashboard", self.driver.current_url)

    def test_7_invalid_login(self):
        self.driver.get("http://localhost:5000/login")
        self.driver.find_element(By.NAME, "username").send_keys("wronguser")
        self.driver.find_element(By.NAME, "password").send_keys("wrongpass")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        error_message = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Invalid username or password')]"))
        )
        self.assertIn("Invalid username or password", error_message.text)

    def test_8_add_task(self):
        self.login()
        self.driver.get("http://localhost:5000/dashboard")
        self.driver.find_element(By.NAME, "title").send_keys("Test Task")
        self.driver.find_element(By.NAME, "description").send_keys("Test Description")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Test Task')]"))
        )
        task_element = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Test Task')]")
        self.assertIn("Test Task", task_element.text)

    def test_9_update_task(self):
        try:
            self.login()
            self.driver.get("http://localhost:5000/dashboard")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

            try:
                self.driver.find_element(By.NAME, "title").send_keys("Task to Update")
                self.driver.find_element(By.NAME, "description").send_keys("Description to Update")
                self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Task to Update')]")))
            except:
                pass  # Task might already exist

            update_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-warning")))
            update_btn.click()

            title_field = self.wait.until(EC.presence_of_element_located((By.NAME, "title")))
            title_field.clear()
            title_field.send_keys("Updated Task Title")

            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            self.wait.until(EC.url_contains("/dashboard"))

            updated_task = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Updated Task Title')]"))
            )
            self.assertIsNotNone(updated_task)

        except Exception as e:
            self.fail(f"Test failed: {str(e)}")

    def test_10_delete_task(self):
        try:
            self.login()
            self.driver.get("http://localhost:5000/dashboard")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

            self.driver.find_element(By.NAME, "title").send_keys("Test Task")
            self.driver.find_element(By.NAME, "description").send_keys("Test Description")
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            self.wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Test Task')]")))

            delete_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-danger")))
            delete_btn.click()

            self.wait.until_not(EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Test Task')]")))

        except Exception as e:
            self.fail(f"Test failed: {str(e)}")


if __name__ == "__main__":
    unittest.main()
