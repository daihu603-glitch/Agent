# 需求追踪与验收报告

项目: my-opcua-gateway
平台: opc_ua

| 需求 | 设计 | 代码 | 测试 | 验收 | 证据 |
|---|---|---|---|---|---|
| FR-001 节点浏览读取与受控写回读 | design.md | gateway.py | test_gateway.py::test_browse_read_and_confirmed_write_readback | pass | evidence/local_protocol_tests.json |
| IF-001 订阅与服务端重启恢复 | design.md | gateway.py | test_gateway.py::test_subscription_receives_changes_and_releases_resources, test_gateway.py::test_server_restart_reconnects_and_restores_subscription | pass | evidence/local_protocol_tests.json |
| SAFE-001 白名单与异常参数保护 | design.md | gateway.py | test_gateway.py::test_10_unauthorized_writes_are_rejected_without_changes, test_gateway.py::test_invalid_node_and_type_mismatch_fail, test_gateway.py::test_remote_endpoint_is_rejected_before_connection | pass | evidence/local_protocol_tests.json |
| NFR-001 持续运行与资源稳定性 | design.md | gateway.py | 未执行：24小时长稳与资源曲线 | blocked | - |

验收统计: {'not_run': 0, 'fail': 0, 'waived': 0, 'pass': 3, 'blocked': 1}
交付门禁: BLOCKED

## 阻塞项
- 需求基线仍为草案，需客户评审后显式设置 baseline_status: approved
- NFR-001 验收状态为 blocked