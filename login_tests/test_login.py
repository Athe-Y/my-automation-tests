from dotenv import load_dotenv
from selenium.common import TimeoutException  # 导入显式等待超时异常类
# 导入pytest测试框架，用于编写和运行测试用例
import pytest
# 导入selenium的webdriver模块，用于自动化浏览器操作
from selenium import webdriver
# 导入By类，用于支持多种元素定位策略（如CSS选择器、ID等）
from selenium.webdriver.common.by import By
import os  # 新增：导入os模块读取环境变量
# 新增导入显式等待相关模块
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()  # 从.env文件加载环境变量

# =========== 1. 创建Page类（工具包）============
class LoginPage:
    """封装登录页面的所有元素和操作（页面对象模型-POM设计模式），创建登录页对象"""
    # 元素定位器（使用CSS选择器），元组格式
    USERNAME_INPUT = (By.CSS_SELECTOR, "#username")  # 用户名输入框
    PASSWORD_INPUT = (By.CSS_SELECTOR, "#password")  # 密码输入框
    VERIFY_CODE_INPUT = (By.CSS_SELECTOR, "#verify_code")  # 验证码输入框
    LOGIN_BUTTON = (By.CSS_SELECTOR, "#loginform > div > div.login_bnt > a")  # 登录按钮
    LOGIN_SUCCESS_INDICATOR = (By.CSS_SELECTOR,
                               "body > div.tpshop-tm-hander.home-index-top.p > div > div > div > div.fl.islogin.hide > a:nth-child(2)")
    # 添加退出方法
    LOGOUT_LINK = (By.LINK_TEXT, "安全退出")  # 安全退出链接
    LOGIN_ENTRY = (By.LINK_TEXT, "登录")    # 登录入口链接
    #错误信息和错误确认按钮元素定位器
    ERROR_MESSAGE_CONTENT = (By.CSS_SELECTOR, ".layui-layer-content.layui-layer-padding")
    ERROR_CONFIRM_BUTTON = (By.CSS_SELECTOR, ".layui-layer-btn0")

    def __init__(self, driver):
        # 初始化方法，接收WebDriver实例
        self.driver = driver  # 将浏览器驱动保存为实例变量

    def load(self, url):
        """打开登录页面"""
        self.driver.get(url)  # 使用浏览器驱动打开指定URL

    def enter_username(self, username):
        """输入用户名"""
        elem = self.driver.find_element(*self.USERNAME_INPUT)  # 在打开的浏览器页面里查找用户名输入框元素（*解包元组）
        elem.clear()  # 清空输入框
        elem.send_keys(username)  # 输入指定的用户名

    def enter_password(self, password):
        """输入密码"""
        elem = self.driver.find_element(*self.PASSWORD_INPUT)  # 查找密码输入框元素
        elem.clear()  # 清空输入框
        elem.send_keys(password)  # 输入指定的密码

    def enter_verify_code(self, verify_code):
        """输入验证码"""
        elem = self.driver.find_element(*self.VERIFY_CODE_INPUT)  # 查找验证码输入框元素
        elem.clear()  # 清空输入框
        elem.send_keys(verify_code)  # 输入指定的验证码

    def click_login_button(self):
        """点击登录按钮"""
        elem = self.driver.find_element(*self.LOGIN_BUTTON)  # 查找登录按钮元素
        elem.click()  # 点击登录按钮

    # 组合操作：完整登录流程
    def login(self, username=None, password=None, verify_code="8888"):
        """支持从环境变量获取凭证"""
        # 若未提供用户名/密码参数，则自动从环境变量中读取
        username = username or os.getenv("TEST_USERNAME")
        password = password or os.getenv("TEST_PASSWORD")
        #封装登录操作：依次输入凭证并提交
        self.enter_username(username)
        self.enter_password(password)
        self.enter_verify_code(verify_code)
        self.click_login_button()

    def logout(self):
        """退出登录并返回登录页面"""
        try:
            # 点击安全退出
            logout_elem = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self.LOGOUT_LINK)
            )
            logout_elem.click()
            # 等待登录入口出现
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.LOGIN_ENTRY)
            )
        except TimeoutException:
            print("退出流程超时，可能已处于未登录状态")

    def handle_error_popup(self, expected_message=None):
        """
        处理错误提示框：验证文本并点击确定
        :param expected_message: 期望的错误消息文本
        """
        # 等待错误提示框内容可见
        try:
            error_content = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.ERROR_MESSAGE_CONTENT)
            )
            actual_message = error_content.text.strip()
            # 如果有预期消息则验证
            if expected_message:
                assert expected_message in actual_message, (
                    f"期望包含 '{expected_message}'，实际得到: '{actual_message}'"
                )
                print(f"错误消息：{actual_message}")

            # 点击确定按钮
            confirm_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.ERROR_CONFIRM_BUTTON)
            )
            confirm_btn.click()
            return actual_message  # 返回实际错误消息
        except TimeoutException:
            print("错误提示框处理超时")
            return None

# =========== 2. 使用Page类的测试用例 ============
@pytest.fixture(scope="module")
def browser():
    """pytest fixture：创建和关闭浏览器实例（模块级共用）"""
    # 初始化微软Edge浏览器
    driver = webdriver.Edge()
    # 返回浏览器驱动实例给测试用例
    yield driver
    # 所有测试结束后关闭浏览器
    driver.quit()

@pytest.fixture
def login_page(browser):
    """pytest fixture：创建登录页面对象（每个测试用例独立）"""
    page = LoginPage(browser)  # 创建LoginPage实例
    # 打开测试登录页面
    page.load("https://hmshop-test.itheima.net/Home/user/login.html")
    return page  # 将页面对象返回给测试用例

def test_successful_login(login_page):
    """测试成功登录"""
    try:
        login_page.login()
        success_element = WebDriverWait(login_page.driver, 10).until(
            EC.visibility_of_element_located(LoginPage.LOGIN_SUCCESS_INDICATOR)
        )
        assert '安全退出' in success_element.text
    finally:
        # 确保无论测试是否通过都执行退出
        login_page.logout()

def test_wrong_password_login(login_page):
    """测试密码错误时的提示"""
    # 使用错误密码登录
    login_page.login(password="654321")
    # 处理错误提示框并验证消息
    error_msg = login_page.handle_error_popup(expected_message="密码错误")
    assert error_msg is not None, "未收到错误提示"
    # 验证返回登录页面
    WebDriverWait(login_page.driver, 5).until(
        EC.visibility_of_element_located(LoginPage.LOGIN_BUTTON)
    )

















