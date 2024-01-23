import argparse
import asyncio
import os
from asyncio import AbstractEventLoop
from os.path import expanduser

import loguru
from aiohttp import web
from ruamel.yaml import YAML

from afore_local_exporter.config import AforeLocalConfig
from afore_local_exporter.http_server import AforeHttpServer
from afore_local_exporter.modbus import AforeModbus

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='config file', type=str, default='config/config.yaml')
    parser.add_argument('--http_port', help='port', type=int, default=18000)

    args = parser.parse_args()

    fname = os.path.expanduser(args.config)
    yaml = YAML()
    config_file = expanduser(args.config)
    with open(config_file, 'r') as f:
        d = yaml.load(f)
        config = AforeLocalConfig(**d)

    modbus = AforeModbus(config=config)

    http_server = AforeHttpServer(modbus=modbus, config=config)
    app = web.Application()
    app.router.add_get('/api/registers', http_server.get_registers)
    app.router.add_get('/metrics', http_server.get_metrics)

    web.run_app(app, port=args.http_port)