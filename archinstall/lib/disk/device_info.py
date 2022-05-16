from __future__ import annotations

import glob
import json
import logging
import os  # type: ignore
from functools import cached_property
from pathlib import Path
from typing import Dict, Any, TYPE_CHECKING, Optional

# https://stackoverflow.com/a/39757388/929999
from ..models.block_device_info import AbstractBlockInfo

if TYPE_CHECKING:
	from .partition import Partition

from .blockdevice import BlockDevice
from archinstall.lib.models.dmcryptdev import DMCryptDev
from .mapperdev import MapperDev
from ..exceptions import SysCallError
from ..general import SysCommand
from ..output import log


class DeviceInfoHandler:

	def __init__(self):
		self._block_device_path = '/sys/class/block/*'
		self._mappers_path = '/dev/mapper/*'

	@classmethod
	def all_blockdevices(cls, mappers=False, partitions=False) -> Dict[str, Any]:
		cls_ = cls._get_instance()
		device_info = cls_._fetch_blockdevices()
		return device_info

	@classmethod
	def _get_instance(cls) -> 'DeviceInfoHandler':
		if not hasattr(cls, '__instance'):
			cls.__instance = cls()
		return cls.__instance

	@classmethod
	def get_all_device_info(cls) -> Dict[str, AbstractBlockInfo]:
		cls_ = cls._get_instance()
		return cls_._device_info

	@classmethod
	def get_device_info(cls, dev_path: str) -> Optional[AbstractBlockInfo]:
		cls_ = cls._get_instance()
		devices = cls_._device_info
		return devices.get(dev_path, None)

	@cached_property
	def _device_info(self) -> Dict[str, AbstractBlockInfo]:
		"""
		Returns BlockDevice() and Partition() objects for all available devices.
		"""
		# Due to lsblk being highly unreliable for this use case,
		# we'll iterate the /sys/class definitions and find the information
		# from there.
		devices = {}

		for block_device in glob.glob(self._block_device_path):
			path = Path(block_device).readlink().name
			device_path = f"/dev/{path}"

			try:
				device_info = self._get_block_device_info(device_path)
			except SysCallError as ex:
				if ex.exit_code in (512, 2):
					# Assume that it's a loop device, and try to get info on it
					try:
						device_info = self._get_loop_info(device_path)
						if not device_info:
							raise SysCallError("Could not get loop information", exit_code=1)
					except SysCallError:
						device_info = self._get_uevent(path)
				else:
					raise ex

			device_info = self._enrich_blockdevice_information(device_info)
			devices[path] = device_info

		return devices

	def _fetch_blockdevices(self, mappers=False, partitions=False) -> Dict[str, Any]:
		"""
		Returns BlockDevice() and Partition() objects for all available devices.
		"""
		from .partition import Partition
		from ... import get_parent_of_partition
		# Due to lsblk being highly unreliable for this use case,
		# we'll iterate the /sys/class definitions and find the information
		# from there.
		instances = {}
		devices = self._device_info

		for path, device_info in devices.items():
			if device_info.dmcrypt_name:
				instances[path] = DMCryptDev(dev_path=device_info.path)
			elif device_info.PARTUUID or device_info.PART_ENTRY_NUMBER:
				if partitions:
					parent_device = get_parent_of_partition(Path(path))
					instances[path] = Partition(path, device_info)
			elif device_info.PTTYPE is True or device_info.TYPE == 'loop':
				instances[path] = BlockDevice(path, device_info=device_info)
			elif device_info.TYPE == 'squashfs':
				# We can ignore squashfs devices (usually /dev/loop0 on Arch ISO)
				pass
			else:
				log(f"Unknown device found, ignoring: {device_info.path}", level=logging.WARNING, fg="yellow")

		if mappers:
			for block_device in glob.glob(self._mappers_path):
				if (pathobj := Path(block_device)).is_symlink():
					instances[f"/dev/mapper/{pathobj.name}"] = MapperDev(mappername=pathobj.name)

		return instances

	def _get_uevent(self, dev_name: str, populate_device: Optional[AbstractBlockInfo] = None) -> AbstractBlockInfo:
		path = Path(f'/dev/{dev_name}')

		if not populate_device:
			populate_device = AbstractBlockInfo(path=path, PATH=path, type='', TYPE='')

		with open(f"/sys/class/block/{dev_name}/uevent") as fh:
			data = fh.read()
			parsed = self._parse_data(data)
			populate_device.set_attrs(parsed)

		return populate_device

	def _get_loop_info(self, path: str) -> AbstractBlockInfo | None:
		loopdevices = json.loads(SysCommand(['losetup', '--json']).decode('UTF_8'))['loopdevices']
		for drive in loopdevices:
			if drive['name'] != path:
				continue

			loopback_info = AbstractBlockInfo(
				type='loop',
				TYPE='loop',
				DEVTYPE='loop',
				PATH=Path(drive['name']),
				path=Path(drive['name'])
			)

			loopback_info.set_attrs(drive)
			return loopback_info

		return None

	def _get_block_device_info(self, device_path: str) -> AbstractBlockInfo:
		cmd = f'blkid -p -o export {device_path}'

		try:
			raw_data = SysCommand(cmd).decode()
		except SysCallError as error:
			log(f"Could not get block device information with '{device_path}'", level=logging.DEBUG)
			raise error

		data = self._parse_data(raw_data)
		device_path = Path(device_path)
		type_ = data.get('TYPE', '')

		block_info = AbstractBlockInfo(path=device_path, PATH=device_path, type=type_, TYPE=type_)

		block_info.set_attrs(data)

		return block_info

	def _enrich_blockdevice_information(self, dev_info: AbstractBlockInfo) -> AbstractBlockInfo:
		dev_name = Path(dev_info.PATH).name

		if not dev_info.TYPE or not dev_info.DEVTYPE:
			dev_info = self._get_uevent(dev_name, dev_info)

		if (dmcrypt_name := Path(f'/sys/class/block/{dev_name}/dm/name')).exists():
			with dmcrypt_name.open('r') as fh:
				dev_info.dmcrypt_name = fh.read().strip()

		return dev_info

	def _parse_data(self, raw_data: str) -> Dict[str, str]:
		results = {}
		for line in raw_data.split('\r\n'):
			line = line.strip()
			if len(line):
				key, val = line.split('=', 1)
				val = val.replace(r'\ ', ' ')
				results[key] = val

		return results

