# HAL 代码审查清单

## 初始化
- [ ] 所有使用的外设时钟已使能 (__HAL_RCC_xxx_CLK_ENABLE)
- [ ] GPIO 模式与原理图一致（输入/输出/复用/模拟）
- [ ] 上下拉配置正确（按键通常 PULLUP，I2C 通常外部上拉）
- [ ] 中断优先级分组已设置 (HAL_NVIC_SetPriorityGrouping)
- [ ] EXTI 中断已使能且优先级合理

## I2C
- [ ] 地址使用 7 位格式，HAL 函数中左移 1 位 (addr << 1)
- [ ] 超时参数不为 0（避免死等）
- [ ] 通信前检查 HAL_I2C_IsDeviceReady
- [ ] SCL/SDA 引脚配置为 AF_OD（开漏）
- [ ] 外部上拉电阻 4.7kΩ（3.3V 系统）

## UART
- [ ] TX/RX 引脚交叉连接（MCU TX → 设备 RX）
- [ ] 波特率双方一致
- [ ] 接收使用中断或 DMA，不要轮询阻塞主循环
- [ ] printf 重定向的 fputc 使用正确的 huart 句柄

## SPI
- [ ] CPOL/CPHA 与从设备 datasheet 一致
- [ ] CS 引脚软件控制时，通信前后正确拉低/拉高
- [ ] MISO/MOSI 不要接反

## 定时器/PWM
- [ ] 预分频和自动重载值计算正确
- [ ] PWM 频率 = TIM_CLK / (PSC+1) / (ARR+1)
- [ ] 高级定时器 TIM1/TIM8 需要使能 MOE (HAL_TIM_PWM_Start)

## 安全
- [ ] 没有在中断中调用 HAL_Delay
- [ ] 没有在中断中做 printf（除非紧急调试）
- [ ] 全局共享变量用 volatile 修饰
- [ ] 数组访问有边界检查
- [ ] 看门狗已配置（长期运行项目）

## 编译
- [ ] 无 warning（-Wall 下）
- [ ] 固件大小未超过 Flash 容量
- [ ] RAM 使用未超过 64KB（F103VE）
- [ ] 链接脚本中 Flash/RAM 起始地址和大小正确