# STM32F103VET6 芯片摘要

## 基本参数
- 内核: ARM Cortex-M3, 72MHz
- Flash: 512KB
- SRAM: 64KB
- 封装: LQFP100
- 工作电压: 2.0V ~ 3.6V
- GPIO: 80 个（PA0-PA15, PB0-PB15, PC0-PC15, PD0-PD7, PE0-PE15）

## 开发板
- 野火指南者 STM32F103VET6
- 板载: LED(PC13), KEY1(PA0), KEY2(PC13 复用注意)
- SWD 调试: PA13(SWDIO), PA14(SWCLK)
- 外部晶振: 8MHz HSE, 32.768kHz LSE

## 外设资源
- USART: 5 路 (USART1-3, UART4-5)
- I2C: 2 路 (I2C1: PB6/PB7, I2C2: PB10/PB11)
- SPI: 3 路 (SPI1: PA5/PA6/PA7, SPI2: PB13/PB14/PB15)
- ADC: 3 个 (ADC1/2/3), 12bit, 最快 1μs
- DMA: 2 个控制器, DMA1(7通道), DMA2(5通道)
- TIM: 8 个 (TIM1-8), 高级定时器 TIM1/TIM8
- USB: 1 个全速 USB
- CAN: 1 个 bxCAN

## 时钟树
- HSE = 8MHz → PLL ×9 → SYSCLK = 72MHz
- AHB = 72MHz, APB1 = 36MHz (max), APB2 = 72MHz
- ADC CLK = APB2 / 6 = 12MHz (max 14MHz)

## 特殊引脚约束
| 引脚 | 约束 |
|------|------|
| PC13, PC14, PC15 | 最大灌电流 2mA，仅低速输出，不能做 ADC 输入 |
| PA13, PA14 | SWD 调试占用，用作 GPIO 会丢失调试 |
| PD0, PD1 | 外部 HSE 晶振占用（指南者板已焊） |
| PB2 | BOOT1，启动模式选择 |
| PA11, PA12 | USB DM/DP（使用 USB 时不可做 GPIO） |
| PB3, PB4, PA15 | JTAG 引脚，需 remap 才能做 GPIO |

## 引脚复用重映射
- I2C1: 默认 PB6(SCL)/PB7(SDA)，可 remap 到 PB8/PB9
- USART1: 默认 PA9(TX)/PA10(RX)，可 remap 到 PB6/PB7
- SPI1: 默认 PA5/PA6/PA7，可 remap 到 PB3/PB4/PB5
- TIM2: 默认 PA0-PA3，可 partial/full remap

## Flash 烧录
- 起始地址: 0x08000000
- Bootloader: 系统存储器 0x1FFFF000
- BOOT0=0 从 Flash 启动, BOOT0=1 从 Bootloader 启动