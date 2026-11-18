# RK3588 / Rockchip Linux SDK 产品开发

## 启动链与 SDK 基线
DDR/init + rkbin/miniloader/SPL → TF-A/OP-TEE（按配置）→ U-Boot → kernel/DTB/ramdisk → Buildroot/Yocto/Debian rootfs。
先记录 SDK 发布版本、板级 BoardConfig、分区 parameter、启动介质（eMMC/SD/SPI NVMe）、安全启动和 A/B 策略。不同 SDK 的 `build.sh` 参数差异很大，必须读脚本和帮助，不能套用其他项目命令。

## 开发顺序
1. 用原厂 EVB/已知好镜像验证下载工具、串口和硬件，再引入客户板差异。
2. 板级 DTS/DTSI、regulator、时钟、复位、pinctrl 按原理图逐项核对；先串口和存储，再显示/camera/PCIe/USB。
3. U-Boot、kernel、rootfs 分组件构建；每次记录修改、配置和产物。设备树变更要核对最终运行 DTB，不只看源码。
4. 外设驱动按 Linux 驱动流程验证，随后接入客户应用与服务。
5. 打包 `update.img` 前核验 parameter、各镜像大小/哈希与目标分区，保留可恢复 Loader/MaskROM 路径。
6. 烧录后核对 model、compatible、cmdline、kernel/SDK 版本、分区和每个外设 probe 日志。

## 多媒体与 NPU（按客户需求）
- Camera：media graph、sensor 驱动、I2C/时钟/lane/速率、ISP 标定、格式与帧率。
- MPP/RGA：明确零拷贝、dmabuf、格式转换、编解码、丢帧和端到端时延。
- NPU：RKNPU2/rknn_server/模型版本一致，记录输入预处理、精度基线、FPS、内存、温度和长稳。
- 性能验收同时记录 CPU/DDR/GPU/NPU 频率、温度和 thermal throttling，不能仅报瞬时帧率。

## 升级与交付
完整 update.img、分区镜像、烧录说明、恢复方法、版本清单、源码补丁/defconfig/DTS、rootfs 包清单、应用与模型、测试证据。升级中断电、镜像损坏、版本回退、存储寿命和恢复分区按需求测试。烧录整包会重写目标存储，必须客户确认并备份。