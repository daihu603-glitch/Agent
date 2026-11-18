# ESP32 / ESP-IDF 产品开发与交付

## 基线
- 芯片（S3/C3 等）、模组、Flash/PSRAM 容量与模式、IDF 版本、sdkconfig、分区表、原理图和射频/天线约束。
- 保存 bootloader、partition-table、app、ota_data、flasher_args、ELF/map、sdkconfig 和 Git SHA。

## 功能开发
- 组件化 CMake 依赖清晰，不在 ISR 调用非 ISR 安全 API；Flash 写期间注意 Cache disabled。
- Wi-Fi/BLE 状态机覆盖扫描失败、认证失败、DHCP 超时、断连、重连、服务端重启和凭据变更。
- NVS 写入有版本、校验、默认值和迁移；限制擦写频率，处理掉电和写满。
- 队列/环形缓冲设置上限并统计丢包；每个任务有栈高水位和看门狗策略。
- 低功耗需定义唤醒源、modem/light/deep sleep 电流、外设保持状态和唤醒后重连时间。

## OTA 与量产
- 分区表不能重叠，ota_0/ota_1 容纳最大固件并留余量，ota_data 与 PHY/NVS 布局不被覆盖。
- OTA 包校验版本/target/SHA256，HTTPS 校验服务器；测试下载中断、校验失败、启动失败、回滚与防回滚。
- Secure Boot、Flash Encryption、eFuse 防回滚属于高风险量产操作，先验证密钥保管和救砖流程，不由智能体自动执行。
- 量产固件默认关闭不必要调试接口和详细敏感日志，Core Dump 保留可恢复读取方案。

## 验收
功能、射频实际环境、重连、OTA、功耗、内存余量、任务栈、Core Dump、长稳和反复上下电。崩溃必须保留 backtrace 与匹配 ELF，验收不能只看“设备能启动”。