# my-automation-tests
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Pytest](https://img.shields.io/badge/tested%20with-pytest-green)


## 项目简介
本项目是基于Selenium和Pytest的Web自动化测试框架，采用页面对象模型（POM）设计模式，集成Allure报告系统。专注于登录功能的自动化测试，通过封装页面操作与测试逻辑分离，提升代码复用性和可维护性。

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
├── .gitignore          # 忽略环境变量/截图/报告数据
├── login_tests/
│   └── test_login_POM.py  # POM模式测试用例
└── .env                # 敏感数据存储（不提交GitHub）
```

> **重要**：`report/`目录（Allure中间数据）不应提交到GitHub，已在.gitignore中排除

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

2. 安装Allure命令行工具
   ```bash
   npm install -g allure-commandline
   ```

3. 创建环境变量文件（.env）
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
     .env
     report/
     *.png
     __pycache__
     ```
   - 凭证获取优先级机制:
      ```python
      username = username or os.getenv("TEST_USERNAME")  # 参数优先>环境变量
      ```
   - 敏感参数默认覆盖：

      - 验证码默认值"8888"可被测试用例覆盖

      - 支持临时传入非常规测试账号

4. **退出登录的严谨处理**

   - 安全退出流程包含双重等待：
      - 等待退出按钮可点击（10秒）
      - 等待登录入口重新出现（10秒）
   - 超时保护机制：

      ```python
      try:
         # 退出操作
      except TimeoutException:
         print("已处理异常状态")
      ```
5. **验证码处理规范**

   - 验证码输入框明确要求：
      ```python
      elem.clear()  # 强制清空
      elem.send_keys(verify_code)  # 支持参数覆盖
      ```
   - 固定验证码"8888"仅作为默认值

6. **多场景测试覆盖**
   - 正常登录 (test_successful_login)：
      - 凭证获取：环境变量优先
      - 成功标志："安全退出"链接验证
      - 必然执行退出清理

   - 异常登录 (test_wrong_password_login)：
      - 错误密码触发机制
      - 弹窗消息内容验证
      - 错误处理后返回登录页验证


## 学习心得
1. 通过这个项目掌握了：
   - POM设计模式的实际应用
   - Allure在线报告生成流程
2. 遇到的坑：
   - Allure需要Java环境的隐藏依赖
