# ESP8266 AT 指令摘要

## 基本参数
- 接口: UART (默认 115200, 8N1)
- 供电: 3.3V, 峰值电流 300mA
- 当前项目: STM32 通过 USART 发送 AT 指令控制

## 常用指令
| 指令 | 功能 | 响应 |
|------|------|------|
| AT | 测试连接 | OK |
| AT+RST | 重启模块 | OK + 启动信息 |
| AT+GMR | 查看版本 | 版本信息 + OK |
| AT+CWMODE=1 | Station 模式 | OK |
| AT+CWMODE=2 | AP 模式 | OK |
| AT+CWMODE=3 | Station+AP | OK |
| AT+CWJAP="ssid","pwd" | 连接 WiFi | OK / FAIL |
| AT+CIFSR | 查看 IP | IP 地址 |
| AT+CIPSTART="TCP","ip",port | 建立 TCP | OK / ERROR |
| AT+CIPSEND=len | 发送数据 | > 提示后发数据 |
| AT+CIPMUX=1 | 多连接模式 | OK |
| AT+CIPSERVER=1,8888 | 创建 TCP 服务器 | OK |

## 注意事项
- 每条指令以 \r\n 结尾
- 发送 AT+CIPSEND 后等待 ">" 提示再发数据
- 模块启动时会输出乱码（76800 baud），之后切回 115200
- 供电不足会导致频繁重启，确保 3.3V 电源能提供 500mA
- ESP8266 与 ESP32-S3 不同：ESP8266 用 AT 固件，ESP32 用 ESP-IDF