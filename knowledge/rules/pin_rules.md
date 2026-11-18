# STM32F103 引脚分配规则

## 绝对约束（违反会损坏硬件或无法工作）
1. PC13/PC14/PC15: 最大 2mA，仅低速输出，不能驱动 LED 直连（需三极管）
2. PA13/PA14: SWD 调试口，除非放弃调试否则不要占用
3. PD0/PD1: 指南者板已焊 8MHz 晶振，不可做 GPIO
4. 5V 容忍引脚: 大部分 GPIO 是 FT（5V tolerant），但 ADC 输入引脚不是
5. ADC 输入引脚: PA0-PA7, PB0-PB1, PC0-PC5 做 ADC 时不能接 5V

## 强烈建议
1. I2C 引脚必须开漏 + 外部上拉，不要用内部上拉替代
2. USART1 (PA9/PA10) 留给调试串口，不要分配给其他外设
3. PB3/PB4/PA15 默认是 JTAG，做 GPIO 需要 __HAL_AFIO_REMAP_SWJ_NOJTAG()
4. BOOT0 (PB2 附近) 不要接外设输出，避免启动模式异常
5. 大电流负载（继电器、舵机信号）不要从 PC13-15 出

## 外设引脚默认分配（F103VE）
| 外设 | 默认引脚 | 可重映射 |
|------|----------|----------|
| USART1 | PA9(TX), PA10(RX) | → PB6, PB7 |
| USART2 | PA2(TX), PA3(RX) | → PD5, PD6 |
| USART3 | PB10(TX), PB11(RX) | → PC10, PC11 / PD8, PD9 |
| I2C1 | PB6(SCL), PB7(SDA) | → PB8, PB9 |
| I2C2 | PB10(SCL), PB11(SDA) | 不可 remap |
| SPI1 | PA5(SCK), PA6(MISO), PA7(MOSI) | → PB3, PB4, PB5 |
| SPI2 | PB13(SCK), PB14(MISO), PB15(MOSI) | 不可 remap |
| TIM2 CH1-4 | PA0, PA1, PA2, PA3 | → PA15, PB3, PB10, PB11 |
| TIM3 CH1-4 | PA6, PA7, PB0, PB1 | → PB4, PB5, PB0, PB1 / PC6-PC9 |
| CAN | PA11(RX), PA12(TX) | → PB8, PB9 |
| USB | PA11(DM), PA12(DP) | 与 CAN 冲突 |

## 冲突检测规则
- USART3 和 I2C2 共用 PB10/PB11 → 不能同时使用默认引脚
- CAN 和 USB 共用 PA11/PA12 → 二选一
- SPI1 remap 和 TIM2 partial remap 共用 PB3/PB4 → 注意
- ADC 和 GPIO 输出不能同时配置在同一引脚