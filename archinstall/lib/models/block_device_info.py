import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict


@dataclass
class AbstractBlockInfo:
	path: Path
	PATH: Path
	type: str
	TYPE: str
	DEVTYPE: Optional[str] = None
	DEVNAME: Optional[str] = None
	dmcrypt_name: Optional[str] = None
	PARTUUID: Optional[str] = None
	PART_ENTRY_NUMBER: Optional[str] = None
	PTTYPE: Optional[bool] = None
	pkname: Optional[str] = None

	def set_attr(self, attr: str, val: str):
		if '-' in attr:
			attr = attr.replace('-', '_')

		if hasattr(self, attr):
			setattr(self, attr, val)

	def set_attrs(self, attrs: Dict[str, str]):
		for k, v in attrs.items():
			self.set_attr(k, v)

	@property
	def device(self) -> Optional[str]:
		"""
		Returns the device file of the BlockDevice.
		If it's a loop-back-device it returns the /dev/X device,
		If it's a ATA-drive it returns the /dev/X device
		And if it's a crypto-device it returns the parent device
		"""

		from ... import DiskError
		from archinstall import log

		if not self.DEVTYPE:
			raise DiskError(f'Could not locate backplane info for "{self.path}"')

		if self.DEVTYPE in ['disk','loop']:
			return str(self.path)
		elif self.DEVTYPE[:4] == 'raid':
			# This should catch /dev/md## raid devices
			return str(self.path)
		elif self.DEVTYPE == 'crypt':
			if not self.pkname:
				raise DiskError(f'A crypt device ({self.path}) without a parent kernel device name.')
			return f"/dev/{self.pkname}"
		else:
			log(f"Unknown blockdevice type for {self.path}: {self.DEVTYPE}", level=logging.DEBUG)

		return None
