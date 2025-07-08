# my-automation-tests

## 项目简介
本项目是基于Selenium和Pytest的Web自动化测试框架，采用**页面对象模型（POM）** 设计模式，专注于登录功能的自动化测试。通过封装页面操作与测试逻辑分离，提升代码复用性和可维护性。


## 项目结构
```
my-automation-tests/
├── .gitignore          # 忽略不必要提交的文件（如环境变量、截图等）
└── login_tests/
    └── test_login_POM.py  # 登录功能测试用例（核心文件，包含POM实现）
```


## 核心技术与设计
1. **页面对象模型（POM）**  
   - 封装登录页面所有元素（用户名输入框、登录按钮等）和操作（输入、点击、登录流程）到`LoginPage`类中  
   - 优势：测试用例与页面操作解耦，页面元素变更时仅需修改POM类，无需改动所有测试用例

2. **测试框架与工具**  
   - `pytest`：提供测试用例组织、fixture（测试前置/后置）、断言等功能  
   - `Selenium`：实现浏览器自动化操作（打开页面、元素交互等）  
   - `python-dotenv`：通过`.env`文件管理环境变量（安全存储用户名/密码等敏感信息）

3. **架构图**  
   ```mermaid
   graph TD
   A[pytest测试框架] --> B[fixture管理浏览器]
   C[LoginPage类] --> D[元素定位器]
   C --> E[登录方法封装]
   C --> F[错误处理机制]
   G[.env文件] --> H[安全存储凭证]
   ```
   - 说明：pytest通过fixture管理浏览器生命周期，LoginPage类封装核心页面逻辑，.env文件保障敏感数据安全，各模块分工明确、低耦合。


## 测试用例说明
核心测试场景包含：
- 成功登录验证（使用环境变量中的正确账号密码）
- 密码错误场景验证（断言错误提示信息）
- （可扩展）例如用户名错误或为空，验证码为空，用户名超长，密码中含不合规特殊字符等。


## 运行步骤
1. 克隆仓库
   ```bash
   git clone <仓库地址>
   cd my-automation-tests
   ```

2. 安装依赖
   ```bash
   pip install selenium pytest python-dotenv
   ```

3. 配置环境变量  
   在项目根目录创建`.env`文件，添加测试账号：
   ```env
   TEST_USERNAME=your_test_username
   TEST_PASSWORD=your_test_password
   ```

4. 运行测试
   ```bash
   pytest login_tests/test_login_POM.py -v
   ```


## 注意事项
- 验证码处理：测试环境使用固定验证码`8888`（实际项目可扩展为自动识别）
- 浏览器：默认使用Edge浏览器，如需切换其他浏览器，修改`browser` fixture中的`webdriver`实例化逻辑
- 环境依赖：确保已安装对应浏览器驱动（如EdgeDriver）并配置到系统PATH


通过POM模式的设计，本框架可快速扩展至其他页面的自动化测试，同时通过环境变量隔离敏感数据，符合测试工程最佳实践。