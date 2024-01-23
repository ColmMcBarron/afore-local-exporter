from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import loguru
from pysolarmanv5 import PySolarmanV5
from .config import AforeLocalConfig, ModbusConfig

LOGGER = loguru.logger

@dataclass
class ModbusValue:
    key: str
    value: int

    def to_dict(self) -> Dict:
        return {
            'key': self.key,
            'value': self.value
        }

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

    def query_registers(self) -> List[ModbusValue]:
        if not self._modbus:
            LOGGER.warning('unable to scrape this time, due to connection problem')
            return []
        registers = []
        multi_registers: Dict[str, List[ModbusValue]] = {}
        for bundle in self._address_bundles:
            regs = self._modbus.read_input_registers(register_addr=bundle[0], quantity=len(bundle))
            LOGGER.info(f'query: {bundle[0]}: {len(bundle)}')
            for (idx, item) in enumerate(regs):
                address = bundle[idx]
                mbus = self._address_map[address]
                if mbus.multi:
                    if mbus.key not in multi_registers:
                        multi_registers[mbus.key] = []
                    multi_registers[mbus.key].append(ModbusValue(key=mbus.key, value=item))
                else:
                    registers.append(ModbusValue(key=mbus.key, value=item))

            for k, mbus_list in multi_registers.items():
                if len(mbus_list) == 1:
                    raise Exception('must have more than 1 multi modbus')
                elif len(mbus_list) == 2:
                    LOGGER.info(f'combining: {mbus_list}')
                    complete = mbus_list[1].value | (mbus_list[0].value << 16)
                    registers.append(ModbusValue(key=k, value=complete))
                else:
                    raise Exception('invalid number of registers')

        return registers


