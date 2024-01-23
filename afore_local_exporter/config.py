from typing import List

from pydantic import BaseModel

class ModbusConfig(BaseModel):
    address: int
    key: str
    label: str
    multi: bool = False
    unit: str = str('unknown')

class InverterConfig(BaseModel):
    serial: int
    ip: str
    port: int

class AforeLocalConfig(BaseModel):
    inverter: InverterConfig
    modbus: List[ModbusConfig]
    verbose: bool = False

