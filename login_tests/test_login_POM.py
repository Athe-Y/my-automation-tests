# 新增
from dotenv import load_dotenv
load_dotenv()  # 从.env文件加载环境变量
# 导入pytest测试框架，用于编写和运行测试用例
import pytest
# 导入selenium的webdriver模块，用于自动化浏览器操作
from selenium import webdriver
# 导入By类，用于支持多种元素定位策略（如CSS选择器、ID等）
from selenium.webdriver.common.by import By
import time  # 导入时间模块，用于等待
import os  # 新增：导入os模块读取环境变量

# =========== 1. 创建Page类（工具包）============
class LoginPage:
    """封装登录页面的所有元素和操作（页面对象模型-POM设计模式），创建登录页对象"""
    # 元素定位器（使用CSS选择器），元组格式
    USERNAME_INPUT = (By.CSS_SELECTOR, "#username")  # 用户名输入框
    PASSWORD_INPUT = (By.CSS_SELECTOR, "#password")  # 密码输入框
    VERIFY_CODE_INPUT = (By.CSS_SELECTOR, "#verify_code")  # 验证码输入框
    LOGIN_BUTTON = (By.CSS_SELECTOR, "#loginform > div > div.login_bnt > a")  # 登录按钮
    # 错误信息选择器 - 使用Layer弹出框的通用选择器
    LOGIN_ERROR_MSG = (By.CSS_SELECTOR, "[id^='layui-layer'] > div.layui-layer-content")
    # 新增：登录成功后显示的登录成功元素（用于断言登录成功）
    LOGIN_SUCCESS_INDICATOR = (By.CSS_SELECTOR,
                               "body > div.tpshop-tm-hander.home-index-top.p > div > div > div > div.fl.islogin.hide > a:nth-child(2)")

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

    def get_error_message(self):
        """获取动态生成的所有Layer错误提示文本"""
        # 等待错误提示显示
        time.sleep(2)
        try:
            # 查找页面中所有可见的错误提示框
            error_elements = self.driver.find_elements(*self.LOGIN_ERROR_MSG)
            # 提取所有可见的错误提示文本
            return [element.text for element in error_elements if element.is_displayed()]
        except:
            # 如果没有错误提示，返回空列表
            return []


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
    """测试成功登录测试"""
    # 使用一行代码完成登录操作（使用正确的用户名和密码）
    login_page.login()
    # 修改断言：等待登录成功后显示的元素出现
    time.sleep(2)  # 等待页面加载完成
    # 获取登录成功后显示的元素
    success_element = login_page.driver.find_element(*LoginPage.LOGIN_SUCCESS_INDICATOR)
    # 验证该元素显示的文本
    assert '安全退出' in success_element.text

def test_login_with_wrong_password(login_page):
    """测试密码错误场景"""
    # 使用错误密码尝试登录
    # 从环境变量获取正确用户名
    correct_user = os.getenv("TEST_USERNAME")
    login_page.login(correct_user, "wrong_password")
    # 验证页面返回了预期的错误提示
    assert "密码错误!" in login_page.get_error_message()

