"""my-opcua-gateway 的环回 OPC UA 客户端与受控写入实现。"""
from __future__ import annotations

import argparse
import asyncio
import ipaddress
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.parse import urlsplit

from asyncua import Client, ua

for _stream in (sys.stdout, sys.stderr):
    if not _stream.isatty() and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

DEMO_ENDPOINT = "opc.tcp://127.0.0.1:4840/agent/demo"
DEMO_SETPOINT = "ns=2;s=Demo.Setpoint"


@dataclass(frozen=True)
class GatewayConfig:
    endpoint: str = DEMO_ENDPOINT
    writable_nodes: tuple[str, ...] = (DEMO_SETPOINT,)
    timeout: float = 5.0
    reconnect_delay: float = 0.5
    max_reconnects: int = 5
    poll_interval: float = 0.2


class _ChangeHandler:
    def __init__(self, gateway: "OpcuaGateway", callback: Callable[[str, Any], None]):
        self.gateway = gateway
        self.callback = callback

    def datachange_notification(self, node, value, data):
        self.gateway.metrics["changes"] += 1
        self.callback(node.nodeid.to_string(), value)

    def status_change_notification(self, status):
        self.gateway.subscription_status = str(status)


class OpcuaGateway:
    def __init__(self, config: GatewayConfig):
        self.config = config
        self._client: Client | None = None
        self._subscription = None
        self._handle = None
        self.metrics = {"connections": 0, "reconnections": 0, "changes": 0, "errors": 0}
        self.last_error = ""
        self.subscription_status = ""
        self._validate_endpoint(config.endpoint)

    @staticmethod
    def _validate_endpoint(endpoint: str) -> None:
        parsed = urlsplit(endpoint)
        if parsed.scheme != "opc.tcp" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("仅允许不含 URL 凭据的 opc.tcp endpoint")
        try:
            address = ipaddress.ip_address(parsed.hostname)
        except ValueError:
            raise ValueError("当前项目客户端仅允许环回 IP；远程设备需使用证书安全配置") from None
        if not address.is_loopback:
            raise ValueError("当前项目客户端仅允许环回 IP；远程设备需使用证书安全配置")

    @property
    def connected(self) -> bool:
        return self._client is not None

    def _require_client(self) -> Client:
        if self._client is None:
            raise RuntimeError("OPC UA 客户端尚未连接")
        return self._client

    async def connect(self) -> None:
        if self._client is not None:
            return
        client = Client(self.config.endpoint, timeout=self.config.timeout)
        try:
            await client.connect()
        except Exception:
            try:
                await client.disconnect()
            except Exception:
                pass
            raise
        self._client = client
        self.metrics["connections"] += 1

    async def close(self) -> None:
        client, self._client = self._client, None
        subscription, self._subscription = self._subscription, None
        self._handle = None
        errors = []
        if subscription is not None:
            try:
                await subscription.delete()
            except Exception as exc:
                errors.append(exc)
        if client is not None:
            try:
                await client.disconnect()
            except Exception as exc:
                errors.append(exc)
        if errors:
            raise RuntimeError(f"OPC UA 资源释放失败: {type(errors[0]).__name__}: {errors[0]}")

    async def __aenter__(self) -> "OpcuaGateway":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        await self.close()

    async def browse(self, node_id: str = "i=85", max_nodes: int = 100) -> list[dict[str, str]]:
        client = self._require_client()
        children = await client.get_node(node_id).get_children()
        rows = []
        for child in children[:max(1, min(max_nodes, 500))]:
            display = await child.read_display_name()
            rows.append({
                "node_id": child.nodeid.to_string(),
                "name": display.Text or child.nodeid.to_string(),
                "class": str(await child.read_node_class()),
            })
        return rows

    async def read(self, node_id: str) -> Any:
        return await self._require_client().get_node(node_id).read_value()

    async def write(self, node_id: str, value: Any, confirmed: bool = False) -> Any:
        if not confirmed:
            raise PermissionError("写操作必须显式 confirmed=true")
        if node_id not in self.config.writable_nodes:
            raise PermissionError(f"节点不在写白名单: {node_id}")
        if isinstance(value, (dict, list)) or value is None:
            raise TypeError("仅支持布尔、数字和字符串标量")
        client = self._require_client()
        node = client.get_node(node_id)
        variant_type = await node.read_data_type_as_variant_type()
        await node.write_value(ua.DataValue(ua.Variant(value, variant_type)))
        readback = await node.read_value()
        if readback != value:
            raise RuntimeError(f"写入回读不一致: expected={value!r}, actual={readback!r}")
        return readback

    async def subscribe(self, node_id: str, callback: Callable[[str, Any], None], period_ms: int = 100) -> None:
        if self._subscription is not None:
            raise RuntimeError("当前实现同时只支持一个订阅")
        client = self._require_client()
        handler = _ChangeHandler(self, callback)
        subscription = await client.create_subscription(max(50, min(period_ms, 10000)), handler)
        try:
            handle = await subscription.subscribe_data_change(client.get_node(node_id))
        except Exception:
            await subscription.delete()
            raise
        self._subscription = subscription
        self._handle = handle

    async def monitor(self, node_id: str, callback: Callable[[str, Any], None], stop: asyncio.Event) -> None:
        while not stop.is_set():
            try:
                await self.connect()
                await self.subscribe(node_id, callback)
                while not stop.is_set():
                    try:
                        await asyncio.wait_for(stop.wait(), timeout=self.config.poll_interval)
                    except asyncio.TimeoutError:
                        pass
                    if not stop.is_set():
                        await self._require_client().get_node("i=2255").read_value()
                await self.close()
                return
            except asyncio.CancelledError:
                try:
                    await self.close()
                except Exception:
                    pass
                raise
            except Exception as exc:
                self.metrics["errors"] += 1
                self.last_error = f"{type(exc).__name__}: {exc}"
                try:
                    await self.close()
                except Exception as close_error:
                    self.last_error += f"; close={type(close_error).__name__}: {close_error}"
                if stop.is_set():
                    return
                if self.metrics["reconnections"] >= self.config.max_reconnects:
                    raise RuntimeError(f"OPC UA 重连次数已用尽: {self.last_error}") from exc
                self.metrics["reconnections"] += 1
                await asyncio.sleep(self.config.reconnect_delay)


async def _main(args: argparse.Namespace) -> dict[str, Any]:
    gateway = OpcuaGateway(GatewayConfig(endpoint=args.endpoint, timeout=args.timeout))
    if args.command == "browse":
        async with gateway:
            return {"rows": await gateway.browse(args.node)}
    if args.command == "read":
        async with gateway:
            return {"node_id": args.node, "value": await gateway.read(args.node)}
    if args.command == "write":
        async with gateway:
            value = json.loads(args.value)
            return {"node_id": args.node, "readback": await gateway.write(args.node, value, confirmed=args.yes)}
    changes = []
    stop = asyncio.Event()
    task = asyncio.create_task(gateway.monitor(args.node, lambda node, value: changes.append({
        "node_id": node,
        "value": value,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }), stop))
    await asyncio.sleep(args.duration)
    stop.set()
    await task
    return {"changes": changes, "metrics": gateway.metrics, "last_error": gateway.last_error}


def main() -> int:
    parser = argparse.ArgumentParser(description="环回 OPC UA 客户端；不连接真实远程设备")
    parser.add_argument("--endpoint", default=DEMO_ENDPOINT)
    parser.add_argument("--timeout", type=float, default=5.0)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("browse", "read", "monitor"):
        sub = commands.add_parser(name)
        sub.add_argument("--node", default="i=85" if name == "browse" else "ns=2;s=Demo.Temperature")
    write = commands.add_parser("write")
    write.add_argument("--node", default=DEMO_SETPOINT)
    write.add_argument("--value", required=True, help="JSON 标量，例如 25.5 或 true")
    write.add_argument("--yes", action="store_true", help="明确确认本次白名单写入")
    monitor = commands.choices["monitor"]
    monitor.add_argument("--duration", type=float, default=5.0)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(_main(args)), ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
