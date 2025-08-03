# my-automation-tests
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Pytest](https://img.shields.io/badge/tested%20with-pytest-green)


## 项目简介
基于 Selenium + Pytest 的 Web 自动化测试框架，采用页面对象模型（POM）设计模式，集成 Allure 生成可视化测试报告。  
核心目标：实现登录功能的自动化测试覆盖（含正常登录、异常场景验证），通过"元素定位与业务逻辑分离"提升代码复用性和可维护性。

## 环境要求
### 必备组件
1. **Java运行环境 (JDK 11+)**
   - 配置步骤：
     - 添加系统变量 `JAVA_HOME` = JDK安装路径（如 `C:\Program Files\Java\jdk-17`）
     - 在Path中添加 `%JAVA_HOME%\bin`
   - 验证：终端执行 `java -version`

2. **Node.js (用于安装Allure命令行工具)**
   - 官网下载安装包：https://nodejs.org/

3. **Python依赖**
   ```bash
   pip install selenium pytest python-dotenv allure-pytest
   ```
### 可选组件
- 浏览器驱动（EdgeDriver等）配置到系统PATH

## 项目结构
```
   my-automation-tests/
├── .gitignore # 忽略敏感文件（.env、报告、缓存等）
├── login_tests/ # 测试用例目录
│ └── test_login.py # 核心测试用例（基于 POM 模式）
├── .env # 敏感数据存储（账号、密码等，不提交 GitHub）
└── report/ # Allure 测试数据目录（自动生成，不提交）
```
> **说明**：  
> - `report/`：执行测试后自动生成，存放Allure原始数据，需通过`allure serve`转换为HTML报告  
> - `login_tests/`：可扩展添加更多测试模块（如`test_register.py`)

## 核心技术与设计
 1.**技术构架图**
 ```mermaid
   graph TD
   A[pytest] --> B[Allure报告]
   A --> C[Selenium驱动]
   C --> D[POM设计模式]
   D --> E[LoginPage类]
   E --> F[元素定位器]
   E --> G[业务流程封装]
   H[.env安全存储] --> I[敏感数据隔离]
   ```



2. **页面对象模型(POM)**
      - `LoginPage`类封装所有页面操作
      - 元素定位与测试逻辑分离

3. **异常处理流程**

   - 内置TimeoutException处理逻辑：
      ```python
      try:
         WebDriverWait(driver, 10).until(...)
      except TimeoutException:
         print("处理超时流程")
      ```

   - 错误弹窗的双重保障：

      验证消息内容匹配（支持文本片段验证）

      自动点击确认按钮关闭弹窗

4. **Allure在线报告系统流程图**
   ```mermaid
   graph LR
   A[pytest测试执行] --> B[生成原始测试数据]
   B --> C[report目录]
   C --> D[Allure命令行工具]
   D --> E[动态HTML报告]
   ```

## 运行步骤

1. 克隆仓库
   ```bash
   git clone <仓库地址>
   cd my-automation-tests
   ```

2. 安装Allure命令行工具（依赖 Node.js）
   ```bash
   npm install -g allure-commandline
   ```
   - 验证安装：执行 allure --version 显示版本信息

3. 创建环境变量文件（.env）
   
   在项目根目录新建.env文件，添加测试账号：
   ```env
   TEST_USERNAME=your_test_username
   TEST_PASSWORD=your_test_password
   ```

4. 执行测试并生成报告
   ```bash
   # 生成原始测试数据（存于report目录）
   pytest login_tests/test_login_POM.py --alluredir=report
   
   # 启动Allure在线报告服务（自动打开浏览器）
   allure serve report
   ```

## 关键注意事项
1. **Allure服务特性**
   - 报告服务启动后会占用终端（需手动 `Ctrl+C` 终止）
   - `report/`目录存放中间测试数据，每次执行会覆盖
   - 实际报告需通过Allure转换生成，不保存在项目中

2. **浏览器配置**
   - 默认使用Edge，修改`browser` fixture切换驱动
   - 验证码测试使用固定值"8888"

3. **安全规范**
   - 敏感数据必须通过`.env`文件管理
   - 确保.gitignore包含：
     ```
     .env # 环境变量
      report/ # 测试数据
      *.png # 截图
      pycache # Python 缓存
     ```
   - 凭证获取优先级机制:
      ```python
      username = username or os.getenv("TEST_USERNAME")  # 参数优先>环境变量
      ```
   - 敏感参数默认覆盖：

      - 验证码默认值"8888"可被测试用例覆盖

      - 支持临时传入非常规测试账号
   - 凭证优先级：测试用例显式传入的参数 > `.env`环境变量

4. **测试场景覆盖**

   | 测试用例                | 场景描述                | 验证点                          | 参数化配置                          |
   |-------------------------|-------------------------|---------------------------------|-------------------------------------|
   | test_successful_login   | 正常登录                | 登录后显示"安全退出"链接        | -                                   |
   | test_login_failures     | 错误密码                | 弹窗提示"密码错误"              | `(None, "654321", "8888", "密码错误")` |
   | test_login_failures     | 用户名为空              | 弹窗提示"用户名不能为空"        | `("", None, "8888", "用户名不能为空")` |
   | test_login_failures     | 密码为空                | 弹窗提示"密码为空"              | `(None, "", "8888", "密码为空")`     |
   | test_login_failures     | 验证码为空              | 弹窗提示"验证码不能为空"        | `(None, None, "", "验证码不能为空")` |

   > **实现说明**：  
   > 登录失败场景通过 `@pytest.mark.parametrize` 实现参数化测试，将4种异常场景整合到 `test_login_failures` 用例中，通过不同参数组合覆盖各类错误场景。  
   > **登出处理**：每个测试用例执行后自动调用 `logout()` 方法，确保状态隔离，避免测试污染

## 学习心得
- 核心收获：实践POM设计模式提升代码可维护性，掌握Allure报告从生成到展示的完整流程  
- 避坑提示：Allure报告生成依赖Java环境，需提前安装并配置JDK（见环境要求）
