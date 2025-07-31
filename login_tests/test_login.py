import os
import pytest
from dotenv import load_dotenv
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()  # 从.env文件加载环境变量

# =========== 1. 创建Page类（工具包）============
class LoginPage:
    """封装登录页面的所有元素和操作（页面对象模型-POM设计模式），创建登录页对象"""
    # 公用的元素定位器
    USERNAME_INPUT = (By.CSS_SELECTOR, "#username") # 用户名输入的元素定位器.定位器使用By.CSS_SELECTOR
    PASSWORD_INPUT = (By.CSS_SELECTOR, "#password") # 密码输入定位器
    VERIFY_CODE_INPUT = (By.CSS_SELECTOR, "#verify_code") # 验证码输入定位器
    LOGIN_BUTTON = (By.CSS_SELECTOR, "#loginform > div > div.login_bnt > a") # 登录按钮的定位器
    LOGIN_SUCCESS_INDICATER = (By.CSS_SELECTOR, "body > div.tpshop-tm-hander.home-index-top.p > div > div > div >"
                                                " div.fl.islogin.hide > a:nth-child(2)") # 登录成功后的提示元素定位器,"安全退出"
    ERROE_MESSAGE_CONTEXT = (By.CSS_SELECTOR, ".layui-layer-content.layui-layer-padding") # 错误提示信息元素文本定位器
    ERROR_CONFIRM_BUTTON = (By.CSS_SELECTOR, ".layui-layer-btn0") # 错误提示信息确认按钮的定位器
    LOGOUT_LINK = LOGIN_SUCCESS_INDICATER # 退出登录的元素定位器
    LOGIN_ENTER= (By.LINK_TEXT, "登录") # 登录入口的元素定位器,定位器使用By.LINK_TEXT

    def __init__(self, driver):
        # 初始化方法，接收WebDriver实例
        self.driver = driver  # 将浏览器驱动保存为实例变量
        self.is_logged_in = False  # 登录状态追踪

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
        # 仅当未提供参数时使用环境变量（保留显式空字符串）
        if username is None:  # 仅处理None情况
            username = os.getenv("TEST_USERNAME")
        if password is None:  # 仅处理None情况
            password = os.getenv("TEST_PASSWORD")
        #封装登录操作：依次输入凭证并提交
        self.enter_username(username)
        self.enter_password(password)
        self.enter_verify_code(verify_code)
        self.click_login_button()
        #登录成功则更新登录状态
        try:
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(self.LOGIN_SUCCESS_INDICATOR)
            )
            self.is_logged_in = True  # 仅当登录成功时才更新状态
        except TimeoutException:
            self.is_logged_in = False  # 登录失败保持原状态

    def logout(self):
        """安全登出：仅在需要时执行"""
        if not self.is_logged_in:  # 状态检查避免不必要操作
            return
        try:
            # 执行实际登出操作
            WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(self.LOGOUT_LINK)
            ).click()
            # 点击进入登录页面
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(self.LOGIN_ENTRY)
            ).click()
            self.is_logged_in = False  # 更新状态
        except TimeoutException:
            # 即使超时也确保状态重置
            self.is_logged_in = False
            print("登出流程超时，但状态已重置")

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
    yield page  # 测试执行阶段
    # 后置清理 - 核心优化点
    page.logout()  # 确保每个测试后都清理状态

def test_successful_login(login_page):
    """测试成功登录"""
    login_page.login()
    success_element = WebDriverWait(login_page.driver, 3).until(
        EC.visibility_of_element_located(LoginPage.LOGIN_SUCCESS_INDICATOR)
    )
    assert '安全退出' in success_element.text

def test_wrong_password_login(login_page):
    """测试密码错误时的提示"""
    # 使用错误密码登录
    login_page.login(password="654321")
    # 处理错误提示框并验证消息
    error_msg = login_page.handle_error_popup(expected_message="密码错误")
    assert error_msg is not None, "未收到错误提示"

def test_username_required(login_page):
    """测试用户名为空时的提示"""
    # 使用空用户名登录
    login_page.login(username="")
    # 处理错误提示框并验证消息
    error_msg = login_page.handle_error_popup(expected_message="用户名不能为空")
    assert error_msg is not None, "未收到用户名空提示"

def test_password_required(login_page):
    """测试密码为空时的提示"""
    # 使用空密码登录
    login_page.login(password="")
    # 处理错误提示框并验证消息
    error_msg = login_page.handle_error_popup(expected_message="密码不能为空")
    assert error_msg is not None, "未收到密码空提示"

def test_verify_code_required(login_page):
    """测试验证码为空时的提示"""
    # 使用空验证码登录
    login_page.login(verify_code="")
    # 处理错误提示框并验证消息
    error_msg = login_page.handle_error_popup(expected_message="验证码不能为空")
    assert error_msg is not None, "未收到验证码空提示"

