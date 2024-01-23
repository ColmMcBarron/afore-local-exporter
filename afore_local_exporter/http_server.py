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
        self._modbus.connect()
        values = self._modbus.query_registers()
        return web.json_response({
            'values': [r.to_dict() for r in values]
        })

    async def get_metrics(self, request: Request) -> Response:
        self._modbus.connect()
        values = self._modbus.query_registers()
        metrics = []
        for m in values:
            meta = self._modbus_meta_map[m.key]
            metrics.append(f'#HELP {m.key} {meta.label} | unit: {meta.unit}')
            metrics.append(f'afore_modbus_{m.key} {m.value}')
        return web.Response(text='\n'.join(metrics), content_type='text/plain')

