from typing import Dict

from aiohttp import web
from aiohttp.abc import Request
from aiohttp.web_response import Response

from afore_local_exporter.config import AforeLocalConfig, ModbusConfig
from afore_local_exporter.modbus import AforeModbus


class AforeHttpServer:

    _modbus: AforeModbus
    _config: AforeLocalConfig
    _modbus_meta_map: Dict[str, ModbusConfig]

    def __init__(self, modbus: AforeModbus, config: AforeLocalConfig):
        self._modbus = modbus
        self._config = config
        self._modbus_meta_map = {}
        for c in config.modbus:
            self._modbus_meta_map[c.key] = c

    async def get_registers(self, request: Request) -> Response:
        await self._modbus.connect()
        registers = await self._modbus.query_registers()
        await self._modbus.disconnect()
        return web.json_response(registers.to_dict())

    async def get_metrics(self, request: Request) -> Response:
        await self._modbus.connect()
        registers = await self._modbus.query_registers()
        await self._modbus.disconnect()
        metrics = []
        for m in registers.values:
            meta = self._modbus_meta_map[m.key]
            metrics.append(f'#HELP {m.key} {meta.label} | unit: {meta.unit}')
            metrics.append(f'afore_modbus_{m.key} {m.value}')

        metrics.append(f'afore_modbus_has_connection_error {int(registers.connection_error)}')
        metrics.append(f'afore_modbus_n_query_errors {registers.query_errors}')

        return web.Response(text='\n'.join(metrics), content_type='text/plain')

