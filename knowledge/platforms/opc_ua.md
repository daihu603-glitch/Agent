# OPC UA 工业互联产品开发

## 范围与信息模型
- 当前平台是 OPC UA（`opc.tcp`）客户端与本地演示服务器雏形，不是 OPC Classic/DA 实现；Classic 需求应通过独立适配层和 Windows/DCOM 安全评审处理。
- 先明确客户端、服务器或网关角色，以及命名空间 URI、稳定 NodeId、BrowseName、数据类型、单位、读写权限、值等级和验收范围。
- 命名空间数组下标可能在服务端重启后变化，产品代码应以 URI 解析下标；工具白名单中的完整 NodeId 必须与实际会话一致。
- 不把地址空间可浏览理解为可写。控制节点还需现场授权、范围/类型检查、安全联锁和回读核验。

## 会话、订阅与可靠性
- 明确连接、Hello/Acknowledge、OpenSecureChannel、Create/ActivateSession、浏览/读写、CreateSubscription、Publish 和关闭的状态与超时。
- 记录会话 ID、服务端状态、序列号、重连次数和最后一次有效 Publish；断线后区分会话恢复、重新激活和完整重建订阅。
- 订阅需核对 PublishingInterval、SamplingInterval、队列大小、丢弃策略、KeepAlive、LifetimeCount 和通知丢失；无数据变化不能算通过。
- 处理 BadNodeIdUnknown、BadAttributeIdInvalid、BadTypeMismatch、BadUserAccessDenied、BadSessionIdInvalid、BadSecureChannelClosed 和 BadCertificate*，不无限重试确定性错误。
- 网关队列必须有容量与背压策略，保存 SourceTimestamp/ServerTimestamp 和 StatusCode；长稳记录时延、丢失、重复、CPU、RSS、FD 和线程。

## 安全边界
- 内置服务器仅绑定环回、NoSecurity、Anonymous，用于协议工具链验证；不得暴露到生产网络。
- 非环回 endpoint 必须在 `opcua.allowed_endpoints` 精确授权，并使用 Basic256Sha256 等受支持策略的 SignAndEncrypt。
- 客户端必须配置自身 certificate/private_key 和固定 server_certificate；禁止连接时自动信任服务端返回的未知证书，并检查证书有效期。
- 用户名和密码只从指定环境变量读取，不进入命令行、日志、状态文件或交付包。生产部署还需按现场规范配置 CA/信任列表、CRL、ApplicationURI、密钥长度、证书轮换和服务端客户端证书授权。
- 写工具要求 `confirmed=true`、完整 NodeId 白名单和标量类型，写入后回读；回读一致不等于物理动作安全完成。

## 测试与交付
- 本地演示实际覆盖浏览、读取、白名单写入回读和订阅，证据标记 `LOCAL_SIMULATION_NOT_DEVICE_OR_CUSTOMER_ACCEPTANCE`。
- 负例至少覆盖未确认写入、白名单外节点、未授权 endpoint、错误类型、无效 NodeId、认证失败、证书不受信/过期和订阅中断。
- 真实设备验收需记录设备/服务器版本、endpoint、节点映射、证书指纹、配置版本和原始报告；不记录密码或私钥。
- 正式交付包含源码/产物、节点映射、配置、证书部署轮换说明、依赖许可证、异常恢复与长稳报告、安装升级回滚手册。仿真证据不能替代真实 PLC 和客户验收。
