# ESP32-S3 芯片摘要

## 基本参数
- 内核: Xtensa LX7 双核, 240MHz
- Flash: 外挂 (通常 8-16MB)
- SRAM: 512KB
- PSRAM: 可选 8MB (Octal SPI)
- WiFi: 802.11 b/g/n, 2.4GHz
- BLE: Bluetooth 5.0
- 工作电压: 3.3V

## GPIO
- 共 45 个可编程 GPIO
- 支持矩阵映射：任意外设可映射到任意 GPIO
- ADC: 2 个 SAR ADC, 12bit
- 注意: GPIO 35-37 用于 Octal PSRAM（有 PSRAM 时不可用）
- Strapping pins: GPIO0, GPIO3, GPIO45, GPIO46

## 外设
- UART: 3 路
- I2C: 2 路
- SPI: 4 路 (SPI0/1 用于 Flash, SPI2/3 通用)
- I2S: 2 路
- USB: 1 个 OTG (全速)
- LEDC: 8 路高速 + 8 路低速 PWM
- RMT: 4 路 TX + 4 路 RX
- TWAI (CAN): 1 路

## ESP-IDF 开发
- 构建命令: idf.py set-target esp32s3 → idf.py build → idf.py flash
- 菜单配置: idf.py menuconfig
- 监控: idf.py monitor (115200)
- 分区表: partitions.csv

## 与 STM32 通信
- 当前方案: UART 桥接 (115200)
- 已实现: ESP32-S3 热点 + MQTT + 语音控制 → STM32 执行