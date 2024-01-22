from typing import List

from pydantic import BaseModel

class ModbusConfig(BaseModel):
    address: int
    prom_metric: str
    label: str
    multi: bool = False

class InverterConfig(BaseModel):
    serial: int
    ip: str
    port: int

class AforeLocalConfig(BaseModel):
    inverter: InverterConfig
    modbus: List[ModbusConfig]
    verbose: bool = False

