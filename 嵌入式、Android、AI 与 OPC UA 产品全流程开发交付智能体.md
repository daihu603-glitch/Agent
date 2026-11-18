# 嵌入式、Android、AI 与 OPC UA 产品全流程开发交付智能体

项目现状、使用入口、验证记录、已知限制和持续迭代记录统一维护在 [项目说明.md](项目说明.md)。每次迭代完成后都应同步更新该文件；维护规则见 [Agent 项目的持续维护规则.md](Agent 项目的持续维护规则.md)。首次装机与分平台环境配置指引见 [环境配置与使用说明.md](环境配置与使用说明.md)。

基于可插拔模型 API（DeepSeek、Anthropic、OpenAI 兼容接口）工具调用 + YAML 工作流，面向真实客户项目：

```
客户需求 → 可测验收基线 → 硬件/固件/APP/AI/OPC UA 设计 → 编码 → SDK/APP/后端构建
→ 烧录/安装/部署/互联 → 故障定位 → 功能/异常/长稳/模型评测 → 需求追踪 → 哈希交付包
```

支持 **STM32、Linux 内核驱动、Linux 应用、ESP32/ESP-IDF、RK3588/Rockchip SDK、Android APP、AI 智能体应用、设备＋APP＋AI 联调和 OPC UA 工业互联**。系统不会把“代码已生成”“编译成功”、单次模型回答或本地协议仿真冒充“客户验收通过”。

## 快速开始

> 交接给新使用者时，直接附带 [环境配置与使用说明.md](环境配置与使用说明.md)。

```bash
pip install -r requirements.txt
# 国内网络较慢时可改用清华镜像加速：
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
set DEEPSEEK_API_KEY=新的有效密钥

# 检查当前提供商和配置，不调用模型、不回显密钥
python agent.py --doctor

# 交互开发，工具自动注册
python agent.py

# 离线自检，不调用模型或硬件
python selftest.py

# 新增可靠性回归测试（无网络、无硬件）
python -m unittest test_improvements -v

# 完整可靠性回归（无真实设备或模型 API）
python -m unittest test_execution_hardening test_privacy_serial test_evidence test_improvements test_delivery_hardening -v

# 建立客户需求基线
python workflow.py workflows/requirements_intake.yaml \
  --var project_name="servo-controller" \
  --var customer="客户A" \
  --var platform="stm32" \
  --var raw_requirements="18 路舵机控制，24 小时连续运行……"
```

## 改进后的推荐入口

在 `D:\Agent` 的 PowerShell 中执行：

```powershell
# 按平台新建项目，需求始终是待客户评审的草案；禁止覆盖已有目录
python manage.py init my-new-opcua --platform opc_ua

# 枚举串口、USB 调试器及已安装 SDK，不打开串口、不连接目标、不改 config.yaml
python manage.py discover

# 真实模型：两条受限评测 + 一条计算器工具工作流；会消耗 API Token
$env:DEEPSEEK_API_KEY = "你的有效密钥"
python manage.py smoke

# 读取已保存的工作流、需求和证据，另存可离线打开的进度报告
python manage.py status workspace/my_opcua/project.yaml --html
```

`init` 支持全部九个平台，每个平台使用独立需求模板，避免把舵机需求复制进 OPC UA。模板指标只是起点，需修改并评审；正式交付要求显式把新模板的 `baseline_status` 设为 `approved`。OPC UA 若确实桥接串口、执行器或 MCU，需在需求文件的 `project.interfaces` 中声明 `serial`、`actuator`、`mcu` 中实际需要的项。

`smoke` 的成功条件包括真实工具调用与回传结果校验，随后执行带工具白名单和调用证据的工作流。没有 Key 时只生成 `BLOCKED` 报告，不调用模型；模拟模型测试不能代替真实模型验证。报告位于 `workspace/model_smoke/`。

`discover` 只报告实际可见的设备和路径，不把“安装了 SDK”当成“连接了硬件”；USB 枚举失败会报告未知，不会假称没有调试器。多串口时仍需明确选择目标。

HTML 报告是保存时快照，重复运行 `status --html` 刷新，不会启动服务、调用模型或继续工作流。新工具默认自动注册，工具数量以 `python agent.py --list-tools` 为准。

### 模型配置

当前 `config.yaml` 默认使用 DeepSeek：

```yaml
agent:
  provider: deepseek
  model: deepseek-chat
  base_url: "https://api.deepseek.com"
  api_key_env: DEEPSEEK_API_KEY
```

`api_key_env` 只能填写**环境变量名称**，不能填写真实密钥。切换提供商时修改 `provider/model/base_url/api_key_env`：Anthropic 使用 `anthropic` 和 `ANTHROPIC_API_KEY`；OpenAI 使用 `openai` 和 `OPENAI_API_KEY`；其他兼容服务使用 `openai-compatible`，并填写实际模型、兼容接口地址和密钥环境变量名。也可用 `AGENT_PROVIDER`、`AGENT_MODEL`、`AGENT_BASE_URL`、`AGENT_API_KEY_ENV` 做进程级覆盖。

OpenAI Python SDK 只负责协议通信，`model_client.py` 统一转换系统提示、工具 schema、多轮工具结果、结束原因和 Token 用量。不同厂商对工具调用、最大 Token、流式响应和错误格式的兼容程度并不完全一致，接入新服务后必须先做最小连通测试和真实评测，不能仅凭“OpenAI 兼容”声明全部能力通过。

## 客户项目使用

1. 复制 `project.example.yaml` 到项目目录，填写平台、源码、SDK、硬件与验收参数。
2. 复制 `requirements.example.yaml` 为 `requirements.yaml`，替换为真实客户需求。
3. 执行环境检查与工作流：

```bash
python product.py doctor path/to/project.yaml
python product.py run path/to/project.yaml --dry-run
python product.py run path/to/project.yaml

# 中断后从最近状态续跑
python product.py run path/to/project.yaml --resume workspace/workflow_results/<workflow>/latest.yaml

# 独立复核交付门禁
python product.py gate path/to/project.yaml
```

`--yes` 会跳过烧录、ADB 安装、后端部署、真实模型评测、OPC UA 真实端点连接/写入、执行器测试和正式交付确认，仅限用户明确授权的自动化场景；真实 API 评测仍需要当前提供商对应的 API Key 环境变量并会产生调用费用。`--yes` 不绕过 OPC UA endpoint、证书和写节点白名单。

Android 项目将 `project.platform` 设为 `android_app`，AI 后端设为 `ai_agent_app`，三端统一项目设为 `device_app_ai`。Android 的 `build.method` 可选 `auto/gradle/custom`，自定义构建使用项目内 `build.ps1`；AI 项目复制 `agent_design.example.yaml` 和 `agent_eval.example.yaml` 后按实际权限与评测场景修改。

## OPC UA 快速验证

无需模型 API Key 或 PLC，即可运行真实环回协议测试：

```bash
# 自动启动本地服务器，执行浏览、读取、白名单写入回读和订阅
python tools_opcua.py

# 或单独启动演示服务器，供 agent.py 或其他 OPC UA 客户端联调
python tools_opcua.py server
```

演示证据保存到 `workspace/opcua/demo_evidence.json`，明确标记 `LOCAL_SIMULATION_NOT_DEVICE_OR_CUSTOMER_ACCEPTANCE`。服务器仅绑定环回、Anonymous 和 NoSecurity，不能用于生产。温度节点为 `ns=2;s=Demo.Temperature`，可写测试节点为 `ns=2;s=Demo.Setpoint`。

`workspace/my_opcua` 还包含独立客户端实现 `gateway.py` 和可重复协议测试。进入该目录运行 `python run_protocol_tests.py`，会实际验证浏览、读写回读、10 次越权写入拒绝、无效节点、类型错误、订阅及服务端重启后的重连恢复，证据写入项目 `evidence/local_protocol_tests.json`。该客户端当前只允许环回 IP；项目设计、需求追踪和未执行的真实硬件/长稳阻塞项分别记录在同目录 `design.md` 与 `traceability_report.md`。

OPC UA 客户项目将 `project.platform` 设为 `opc_ua`，然后使用统一的 `product.py doctor/run/gate`。真实远程连接前，在 `config.yaml` 配置精确 endpoint、客户端证书/私钥、固定服务器证书和最小写节点集合：

```yaml
opcua:
  demo_endpoint: "opc.tcp://127.0.0.1:4840/agent/demo"
  allowed_endpoints: ["opc.tcp://192.0.2.10:4840"]  # 示例地址，替换为已授权端点
  writable_nodes: ["ns=2;s=Demo.Setpoint", "ns=3;s=Test.Setpoint"]
  security_policy: Basic256Sha256
  certificate: "C:/secure/opcua/client.der"
  private_key: "C:/secure/opcua/client-key.pem"
  server_certificate: "C:/secure/opcua/server.der"
  username_env: OPCUA_USERNAME
  password_env: OPCUA_PASSWORD
```

```bash
set OPCUA_USERNAME=实际账号
set OPCUA_PASSWORD=实际密码
python product.py doctor path/to/opcua-project.yaml
```

远程模式强制 SignAndEncrypt、固定服务器证书并检查有效期，不会自动信任连接时返回的未知证书。证书轮换需同步更新固定证书；生产环境还应按现场规范配置 CA/信任列表、CRL、ApplicationURI 和服务端授权。真实端点连接与写入均有工作流确认，写入还要求 `confirmed=true` 和节点白名单；本地演示始终使用独立匿名配置。

## 产品工作流

| 工作流 | 覆盖范围 |
|---|---|
| `requirements_intake.yaml` | 原始需求分解、歧义清单、量化验收矩阵 |
| `stm32_product.yaml` | CubeMX/HAL、驱动/RTOS、构建、SWD、HardFault、HIL、长稳、交付 |
| `linux_driver_product.yaml` | Kbuild、DTS、并发/DMA、交叉编译、加载卸载、Oops、压力、交付 |
| `linux_app_product.yaml` | CMake、IPC、服务、部署、异常恢复、资源/时延长稳、交付 |
| `esp32_product.yaml` | ESP-IDF、Wi-Fi/BLE、分区、NVS、OTA/回滚、Core Dump、交付 |
| `rk3588_product.yaml` | BoardConfig、U-Boot/kernel/rootfs、update.img、外设/MPP/RGA/NPU、交付 |
| `android_app_product.yaml` | BLE/配网/协议、构建、Lint/单测/仪器测试、ADB、签名、真机验收、APK/AAB 交付 |
| `ai_agent_app_product.yaml` | 模型/工具/记忆/RAG、安全审计、受限真实评测、后端部署、质量与成本验收 |
| `device_app_ai_product.yaml` | 三端统一契约、版本绑定、人工确认、本地安全限位、故障注入和统一交付 |
| `opc_ua_product.yaml` | 节点模型、浏览/读写/订阅、本地仿真、证书固定、真实端点联调、异常/长稳与交付 |
| `customer_acceptance.yaml` | 独立证据复核、正式打包和 SHA256 校验 |

`workflows/` 也保留快速开发、代码审查、原理图审查、回归测试和学习工作流。

## 关键工具

| 领域 | 能力 |
|---|---|
| 通用 | 文件、计算、HTTP、Git、知识库、PDF/原理图 |
| STM32 | IOC/引脚、ARM GCC/CubeIDE、ST-Link/OpenOCD、ELF 容量、OpenOCD 故障快照、addr2line |
| Linux | 驱动/应用构建、DTS、驱动静态风险、SSH/SCP、设备健康、加载卸载、日志采集 |
| ESP32 | IDF 构建/烧录/尺寸、分区重叠/容量、sdkconfig、OTA 文件与哈希、Xtensa/RISC-V 符号化 |
| RK3588 | SDK 检测、分组件构建、镜像完整性、整包烧录、运行时/媒体/NPU 验收清单 |
| Android | SDK/JDK/ADB 检测、Gradle/PowerShell 构建、Lint、单测、指定设备仪器测试、安装、logcat、APK/AAB 签名验证 |
| AI 智能体 | 设计校验、工具权限审计、后端/APP 静态安全扫描、真实 API 评测与逐条证据；执行层安全白名单 |
| OPC UA | 环境检查、节点浏览/读取、白名单写入回读、数据变化订阅、环回演示服务器与本地协议证据 |
| 串口/HIL | 命令响应、关键词等待、后台异常监控、版本绑定、循环压力、崩溃日志分析 |
| 代码生成 | GPIO、I2C、UART 命令、Makefile Jinja2 模板 |
| 需求交付 | 需求规格、设计/代码/测试追踪、验收记录、交付门禁、构建环境、ZIP/SHA256 验证 |

## 正式交付门禁

2026-11-10 的九项加固、兼容变化和验证结果见 [NINE_FIXES_2026-11-10.md](NINE_FIXES_2026-11-10.md)。危险工具现在由执行层逐次确认；串口需明确选择，ST-Link 烧录需配置 `probe_serial`；旧日志型 pass 和旧 schema v1 ZIP 需重新生成。

正式包必须同时满足：

- 每条需求有唯一 ID、量化验收标准、验证方法。
- `trace.design/code/tests` 完整。
- 每条需求真实 `pass`，有证据；引用的证据文件必须存在。
- 验收绑定当前需求基线与证据文件 SHA256；修改验收条件、基线版本或证据文件后需重新验证，旧记录缺少绑定也会阻塞。
- 结构化证据的状态、scope、method、需求、逐项 checks 和运行信息必须一致；本地仿真不能证明硬件/客户验收。真实设备验收还要求设备身份和 `project.artifacts` 产物绑定。
- 验收同时绑定源码快照和固件/部署产物；源码修改、新增、删除或产物变化均使旧结果失效。
- 版本、源码、固件和测试证据对应。
- ZIP 内 `manifest.json` 和逐文件 SHA256，独立验证通过。
- schema v2 ZIP 自带证据和源码/产物快照，离开原机器仍能重验；空包、额外文件、重复条目和不在验收版本内的源码/二进制均被拒绝。

`allow_incomplete=true` 只能生成 `WAIVED_INTERNAL_ONLY` 内部调试包，`verify_delivery_package` 不会将其视为正式交付。

工作流仅接受最后一个非空行的完整 `STEP_STATUS: COMPLETED/FAILED/BLOCKED` 标记；没有标记按失败处理。状态采用原子写入，并保存工具调用和 Token 用量。续跑同时检查工作流绝对路径、内容和项目变量，禁止更换项目后复用旧完成状态；旧格式状态需重新运行，脱敏变量需重新提供。可通过步骤 `allowed_tools` 限制工具，`required_tools` 要求实际成功调用，`max_steps` 限制模型轮数。

`required_tools` 检查执行器提供的 `success/status`，以该工具最后一次调用为准。工具公共字符串接口仍兼容，宿主可用 `tools.execute_tool()` 获取结构化结果。独立 Python 宿主使用 `execution_policy.authorization_scope(可信回调)` 授权具体操作；授权回调不能来自模型参数。

## 配置

- `config.yaml`：本机工具链、SDK、Android JDK/ADB、串口、SSH、RK3588 烧录工具和 OPC UA 安全边界；不保存模型密钥或 OPC UA 密码。
- 中文 Windows 下各入口脚本会自动把管道/重定向输出切换为 UTF-8，被 IDE 捕获或写入日志时不再乱码；交互控制台保持系统默认编码，无需手动设置 `PYTHONIOENCODING`。
- Android 的 `jdk_home`、`sdk_root` 等路径建议保持纯 ASCII。本机配置通过 `D:\AndroidStudioNew` 目录联接指向实际安装目录，避免全角字符路径导致 JDK/Gradle 工具链异常；重装 Android Studio 后需更新该联接。
- `project.yaml`：每个客户项目的独立配置；`components` 可分别指定固件、APP 和 AI 后端目录。
- `agent_design.example.yaml` / `agent_eval.example.yaml`：智能体权限设计和真实评测起点。
- `knowledge/`：嵌入式、Android、AI 后端、三端联调和 OPC UA 的设计、调试、量产与验收知识。
- `workspace/`：需求、日志、评测报告、工作流状态和交付包。

当前机器已检测到 STM32CubeIDE/ARM GCC 和 Android SDK 35/JDK/ADB。ESP-IDF、RK3588 SDK、Linux KDIR、设备 SSH/串口/Android 真机需按实际项目配置；未安装 SDK、未连接硬件或未配置模型 Key 时，对应步骤会报告阻塞，不会伪造成功。

## 扩展工具

新增 `tools_*.py` 后会自动导入：

```python
from tools import tool

@tool("my_tool", "描述", {"param": {"type": "string"}}, ["param"])
def my_tool(param: str) -> str:
    return f"结果: {param}"
```

硬件写入、远程变更和正式交付工具应在工作流设置 `confirm: true`，并在函数内做参数与范围校验。
