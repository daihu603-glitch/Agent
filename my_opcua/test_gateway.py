from __future__ import annotations

import asyncio
import socket
import unittest

from asyncua import Server, ua
from asyncua.ua import UaStatusCodeError

from gateway import GatewayConfig, OpcuaGateway


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


async def _wait_for(predicate, timeout: float = 8.0) -> None:
    async with asyncio.timeout(timeout):
        while not predicate():
            await asyncio.sleep(0.05)


class GatewayProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.port = _free_port()
        await self._start_server()
        self.gateway = OpcuaGateway(GatewayConfig(
            endpoint=self.endpoint,
            writable_nodes=(self.setpoint_id,),
            reconnect_delay=0.1,
            poll_interval=0.1,
            max_reconnects=8,
        ))

    async def _start_server(self):
        self.endpoint = f"opc.tcp://127.0.0.1:{self.port}/agent/demo"
        self.server = Server()
        self.server.set_security_policy([ua.SecurityPolicyType.NoSecurity])
        self.server.set_identity_tokens([ua.AnonymousIdentityToken])
        await self.server.init()
        self.server.set_endpoint(self.endpoint)
        namespace = await self.server.register_namespace("urn:my-opcua-gateway:test")
        device = await self.server.nodes.objects.add_object(ua.NodeId("DemoDevice", namespace), "DemoDevice")
        self.temperature = await device.add_variable(ua.NodeId("Demo.Temperature", namespace), "Demo.Temperature", 20.0)
        self.setpoint = await device.add_variable(ua.NodeId("Demo.Setpoint", namespace), "Demo.Setpoint", 20.0)
        await self.temperature.set_writable(False)
        await self.setpoint.set_writable()
        self.temperature_id = self.temperature.nodeid.to_string()
        self.setpoint_id = self.setpoint.nodeid.to_string()
        await self.server.start()

    async def asyncTearDown(self):
        try:
            await self.gateway.close()
        except Exception:
            pass
        try:
            await self.server.stop()
        except Exception:
            pass

    async def test_browse_read_and_confirmed_write_readback(self):
        async with self.gateway:
            rows = await self.gateway.browse()
            self.assertIn("DemoDevice", {row["name"] for row in rows})
            self.assertEqual(await self.gateway.read(self.temperature_id), 20.0)
            self.assertEqual(await self.gateway.write(self.setpoint_id, 25.5, confirmed=True), 25.5)
        self.assertFalse(self.gateway.connected)

    async def test_10_unauthorized_writes_are_rejected_without_changes(self):
        async with self.gateway:
            before = await self.gateway.read(self.temperature_id)
            for _ in range(10):
                with self.assertRaises(PermissionError):
                    await self.gateway.write(self.temperature_id, 99.0, confirmed=True)
                self.assertEqual(await self.gateway.read(self.temperature_id), before)
            with self.assertRaises(PermissionError):
                await self.gateway.write(self.setpoint_id, 30.0, confirmed=False)
            self.assertEqual(await self.gateway.read(self.setpoint_id), 20.0)

    async def test_invalid_node_and_type_mismatch_fail(self):
        async with self.gateway:
            with self.assertRaises(UaStatusCodeError):
                await self.gateway.read("ns=2;s=Missing.Node")
            with self.assertRaises(ua.UaError):
                await self.gateway.write(self.setpoint_id, "not-a-double", confirmed=True)
            self.assertEqual(await self.gateway.read(self.setpoint_id), 20.0)

    async def test_subscription_receives_changes_and_releases_resources(self):
        changes = []
        async with self.gateway:
            await self.gateway.subscribe(self.temperature_id, lambda node, value: changes.append(value))
            await self.temperature.write_value(22.0)
            await _wait_for(lambda: 22.0 in changes)
        self.assertFalse(self.gateway.connected)
        self.assertIsNone(self.gateway._subscription)

    async def test_server_restart_reconnects_and_restores_subscription(self):
        changes = []
        stop = asyncio.Event()
        task = asyncio.create_task(self.gateway.monitor(self.temperature_id, lambda node, value: changes.append(value), stop))
        await _wait_for(lambda: self.gateway.metrics["connections"] == 1 and bool(changes))
        await self.server.stop()
        await asyncio.sleep(0.4)
        await self._start_server()
        await self.temperature.write_value(23.5)
        await _wait_for(lambda: self.gateway.metrics["reconnections"] >= 1 and self.gateway.metrics["connections"] >= 2 and 23.5 in changes)
        stop.set()
        await asyncio.wait_for(task, timeout=5)
        self.assertFalse(self.gateway.connected)

    async def test_remote_endpoint_is_rejected_before_connection(self):
        with self.assertRaises(ValueError):
            OpcuaGateway(GatewayConfig(endpoint="opc.tcp://192.0.2.10:4840"))


if __name__ == "__main__":
    unittest.main()
