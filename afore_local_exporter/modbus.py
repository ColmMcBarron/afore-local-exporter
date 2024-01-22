from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import loguru
from pysolarmanv5 import PySolarmanV5
from .config import AforeLocalConfig, ModbusConfig

LOGGER = loguru.logger

@dataclass
class ModbusValue:
    metric: str
    label: str
    value: int

class AforeModbus:

    _config: AforeLocalConfig
    _address_bundles: List[List[int]]
    _address_map: Dict[int, ModbusConfig]
    _modbus: Optional[PySolarmanV5]

    def __init__(self, config: AforeLocalConfig):
        self._config = config
        self._address_bundles = []
        self._address_map = {}
        self._map_addresses()
        self._modbus = None


    def _map_addresses(self):
        self._config.modbus.sort(key=lambda i: i.address)
        address_bundle = []
        for mbus in self._config.modbus:
            if mbus.address in self._address_map:
                raise Exception('Duplicate address mapping')
            self._address_map[mbus.address] = mbus
            if len(address_bundle) == 0:
                address_bundle = [mbus.address]
                continue
            if address_bundle[-1] + 1 == mbus.address:
                address_bundle.append(mbus.address)
                continue
            self._address_bundles.append(address_bundle)
            address_bundle = [mbus.address]
        if address_bundle:
            self._address_bundles.append(address_bundle)

    def connect(self) -> None:
        try:
            LOGGER.info('Connecting to Modbus')
            self._modbus = PySolarmanV5(self._config.inverter.ip,
                                  self._config.inverter.serial,
                                  port=self._config.inverter.port,
                                  mb_slave_id=1,
                                  verbose=self._config.verbose)
        except Exception as e:
            LOGGER.opt(exception=True).error('Unable to connect to modbus, try next time')
            self._modbus = None

    def query_registers(self) -> Optional[List[Tuple[str, str, int]]]:
        if not self._modbus:
            LOGGER.warning('unable to scrape this time, due to connection problem')
            return None
        registers = []
        multi_registers: Dict[str, List[ModbusValue]] = {}
        for bundle in self._address_bundles:
            regs = self._modbus.read_input_registers(register_addr=bundle[0], quantity=len(bundle))
            for (idx, item) in enumerate(regs):
                address = bundle[idx]
                mbus = self._address_map[address]
                if mbus.multi:
                    if mbus.prom_metric not in multi_registers:
                        multi_registers[mbus.prom_metric] = []
                    multi_registers[mbus.prom_metric].append(ModbusValue(metric=mbus.prom_metric, label=mbus.label, value=item))
                else:
                    registers.append(ModbusValue(metric=mbus.prom_metric, label=mbus.label, value=item))

            for metric, mbus_list in multi_registers.items():
                if len(mbus_list) == 1:
                    raise Exception('must have more than 1 multi modbus')
                if len(mbus_list) == 2:
                    complete = mbus_list[1].value | (mbus_list[0].value << 16)
                    registers.append(ModbusValue(metric=metric, label=mbus_list[0].label, value=complete))

        return registers


