# Linux 内核驱动产品开发

## 输入基线
- 板卡原理图、芯片手册、内核确切版本与配置、交叉工具链、设备树、rootfs、启动日志。
- 客户接口约定：字符设备/IIO/input/net/custom IOCTL/sysfs，结构体布局、32/64 位兼容、错误码和并发语义。
- KDIR 必须与目标运行内核一致；保留 vmlinux、System.map、.config、模块符号和 GKHID/kabi 信息（如适用）。

## 实现检查
- probe/remove 对称，所有资源按获取逆序释放；优先 devm，但不能忽略 probe deferral。
- 设备树核对 compatible、reg、interrupts、clocks、resets、pinctrl、regulator、DMA 和电源域。
- 用户拷贝检查 copy_to/from_user 返回值；IOCTL 做命令号、长度、权限、边界和 compat 处理。
- 明确睡眠上下文：spinlock 内不能睡眠；工作队列处理耗时任务；等待队列支持超时与信号。
- DMA 使用一致映射或正确 streaming map/unmap，处理 Cache 一致性、地址宽度和缓冲区生命周期。
-  sysfs 默认最小权限，debugfs 不作为客户正式接口；日志限流且不带敏感数据。

## 验证
1. 静态检查 + 交叉编译（W=1，按项目需要 sparse/smatch）。
2. insmod → probe 成功 → 功能/边界/并发 → rmmod → 重复加载卸载；任何 tainted/Oops 必须记录。
3. 异常测试：设备不存在、资源占用、热插拔、错误 DTS、打开/关闭竞争、读写超时和进程被杀。
4. KASAN/KCSAN/lockdep/UBSAN（内核支持时）以及长稳压力，检查内存、句柄和 IRQ 计数。
5. 记录 `/proc/interrupts`、dmesg、测试日志、模块 vermagic、SHA256 和版本。

## 交付
模块 `.ko`、源码、Kbuild/Makefile、DTS 示例、用户态测试程序、接口文档、部署/卸载说明、内核配置和验收报告。禁止把“能编译”当作“能交付”。