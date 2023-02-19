from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, TYPE_CHECKING

import parted
from _ped import PartitionException
from parted import Device, Disk, Geometry, FileSystem

from ..exceptions import DiskError, UnknownFilesystemFormat
from ..general import SysCommand, SysCallError
from ..models.subvolume import Subvolume
from ..output import log
from ..luks import Luks2

from .device import DeviceModification, PartitionModification, BDevice, DeviceInfo, PartitionInfo, \
	DiskLayoutConfiguration, DiskLayoutType, FilesystemType, Size, Unit, PartitionType, PartitionFlag, PartitionTable, \
	ModificationStatus, get_lsblk_info, get_lsblk_by_mountpoint

if TYPE_CHECKING:
	_: Any


class DeviceHandler(object):
	def __init__(self):
		self._devices: Dict[Path, BDevice] = {}
		self.load_devices()

	@property
	def devices(self) -> List[BDevice]:
		return list(self._devices.values())

	def load_devices(self):
		block_devices = {}

		for device in parted.getAllDevices():
			disk = Disk(device)
			device_info = DeviceInfo.create(disk)

			partition_info = [PartitionInfo.create(p) for p in disk.partitions]

			block_device = BDevice(disk, device_info, partition_info)
			block_devices[block_device.device_info.path] = block_device

		self._devices = block_devices

	def get_device(self, path: Path) -> Optional[BDevice]:
		return self._devices.get(path, None)

	def get_device_by_partition(self, partition_path: Path) -> Optional[BDevice]:
		partition = self.find_partition(partition_path)
		if partition:
			return partition.disk.device
		return None

	def find_partition(self, path: Path) -> Optional[PartitionInfo]:
		for device in self._devices.values():
			part = next(filter(lambda x: str(x.path) == str(path), device.partition_info), None)
			if part is not None:
				return part
		return None

	def parse_device_arguments(self, disk_layouts: Dict[str, List[Dict[str, Any]]]) -> Optional[DiskLayoutConfiguration]:
		if not disk_layouts:
			return None

		layout_type = disk_layouts.get('layout_type', None)
		if not layout_type:
			raise ValueError('Missing disk layout configuration: layout_type')

		device_modifications: List[DeviceModification] = []
		config = DiskLayoutConfiguration(
			layout_type=DiskLayoutType(layout_type),
			layouts=device_modifications
		)

		for entry in disk_layouts.get('layouts', []):
			device_path = Path(entry.get('device', None)) if entry.get('device', None) else None

			if not device_path:
				continue

			device = self.get_device(device_path)

			if not device:
				continue

			device_modification = DeviceModification(
				wipe=entry.get('wipe', False),
				device=device
			)

			device_partitions: List[PartitionModification] = []

			for partition in entry.get('partitions', []):
				device_partition = PartitionModification(
					status=ModificationStatus(partition['status']),
					fs_type=FilesystemType(partition['fs_type']),
					start=Size.parse_args(partition['start']),
					length=Size.parse_args(partition['length']),
					mount_options=partition['mount_options'],
					mountpoint=Path(partition['mountpoint']) if partition['mountpoint'] else None,
					type=PartitionType(partition['type']),
					flags=[PartitionFlag[f] for f in partition.get('flags', [])],
					btrfs=Subvolume.parse_arguments(partition.get('btrfs', []))
				)
				device_partitions.append(device_partition)

			device_modification.partitions = device_partitions
			device_modifications.append(device_modification)

		return config

	def get_uuid_for_path(self, path: Path) -> Optional[str]:
		partition = self.find_partition(path)
		return partition.partuuid if partition else None

	def _perform_formatting(
		self,
		fs_type: FilesystemType,
		path: Path,
		additional_parted_options: List[str] = []
	):
		options = []
		command = ''

		match fs_type:
			case FilesystemType.Btrfs:
				options += ['-f']
				command += 'mkfs.btrfs'
			case FilesystemType.Fat16:
				options += ['-F16']
				command += 'mkfs.fat'
			case FilesystemType.Fat32:
				options += ['-F32']
				command += 'mkfs.fat'
			case FilesystemType.Ext2:
				options += ['-F']
				command += 'mkfs.ext2'
			case FilesystemType.Ext3:
				options += ['-F']
				command += 'mkfs.ext3'
			case FilesystemType.Ext4:
				options += ['-F']
				command += 'mkfs.ext4'
			case FilesystemType.Xfs:
				options += ['-f']
				command += 'mkfs.xfs'
			case FilesystemType.F2fs:
				options += ['-f']
				command += 'mkfs.f2fs'
			case FilesystemType.Ntfs:
				options += ['-f', '-Q']
				command += 'mkfs.ntfs'
			case FilesystemType.Reiserfs:
				command += 'mkfs.reiserfs'
			case _:
				raise UnknownFilesystemFormat(f'Filetype "{fs_type.value}" is not supported')

		options += additional_parted_options
		options_str = ' '.join(options)

		log(f'Formatting filesystem: /usr/bin/{command} {options_str} {path}')

		try:
			if (handle := SysCommand(f"/usr/bin/{command} {options_str} {path}")).exit_code != 0:
				mkfs_error = handle.decode()
				raise DiskError(f'Could not format {path} with {fs_type.value}: {mkfs_error}')
		except SysCallError as error:
			msg = f'Could not format {path} with {fs_type.value}: {error.message}'
			log(msg, fg='red')
			raise DiskError(msg)

	def _perform_enc_formatting(
		self,
		part_mod: PartitionModification,
		enc_conf: 'DiskEncryption'
	):
		luks_handler = Luks2(
			part_mod.dev_path,
			mapper_name=part_mod.mapper_name,
			password=enc_conf.encryption_password
		)

		log(f'luks2 encrypting device: {part_mod.dev_path}', level=logging.INFO)
		key_file = luks_handler.encrypt()

		log(f'luks2 unlocking device: {part_mod.dev_path}', level=logging.INFO)
		luks_handler.unlock(key_file=key_file)

		if not luks_handler.mapper_dev:
			raise DiskError('Failed to unlock luks device')

		log(f'luks2 formatting mapper dev: {luks_handler.mapper_dev}', level=logging.INFO)
		self._perform_formatting(part_mod.fs_type, luks_handler.mapper_dev)

		log(f'luks2 locking device: {part_mod.dev_path}', level=logging.INFO)
		luks_handler.lock()

	def format(
		self,
		modification: DeviceModification,
		enc_conf: Optional['DiskEncryption'] = None
	):
		"""
		Format can be given an overriding path, for instance /dev/null to test
		the formatting functionality and in essence the support for the given filesystem.
		"""

		# verify that all partitions have a path set (which implies that they have been created)
		missing_path = next(filter(lambda x: x.dev_path is None, modification.partitions), None)
		if missing_path is not None:
			raise ValueError('When formatting, all partitions must have a path set')

		# crypto luks is not known to parted and can therefore not
		# be used as a filesystem type in that sense;
		invalid_fs_type = next(filter(lambda x: x.fs_type is FilesystemType.Crypto_luks, modification.partitions), None)
		if invalid_fs_type is not None:
			raise ValueError('Crypto luks cannot be set as a filesystem type')

		# make sure all devices are unmounted
		self._umount_all_existing(modification)

		for part_mod in modification.partitions:
			# partition will be encrypted
			if enc_conf is not None and part_mod in enc_conf.partitions:
				self._perform_enc_formatting(part_mod, enc_conf)
			else:
				self._perform_formatting(part_mod.fs_type, part_mod.dev_path)

	def _perform_partitioning(
		self,
		part_mod: PartitionModification,
		block_device: BDevice,
		disk: Disk,
		requires_delete: bool
	):
		# when we require a delete and the partition to be (re)created
		# already exists then we have to delete it first
		if requires_delete and part_mod.status in [ModificationStatus.Modify, ModificationStatus.Delete]:
			log(f'Delete existing partition: {part_mod.dev_path}', level=logging.INFO)
			part_info = self.find_partition(part_mod.dev_path)
			disk.deletePartition(part_info.partition)
			disk.commit()

		if part_mod.status == ModificationStatus.Delete:
			return

		start_sector = part_mod.start.convert(
			Unit.sectors,
			block_device.device_info.sector_size
		)
		length_sector = part_mod.length.convert(
			Unit.sectors,
			block_device.device_info.sector_size
		)

		geometry = Geometry(
			device=block_device.disk.device,
			start=start_sector.value,
			length=length_sector.value
		)

		filesystem = FileSystem(type=part_mod.fs_type.value, geometry=geometry)

		partition = parted.Partition(
			disk=disk,
			type=part_mod.type.get_partition_code(),
			fs=filesystem,
			geometry=geometry
		)

		for flag in part_mod.flags:
			partition.setFlag(flag.value)

		log(f'\tType: {part_mod.type.value}', level=logging.DEBUG)
		log(f'\tFilesystem: {part_mod.fs_type.value}', level=logging.DEBUG)
		log(f'\tGeometry: {start_sector.value} start sector, {length_sector.value} length', level=logging.DEBUG)

		try:
			disk.addPartition(partition=partition, constraint=disk.device.optimalAlignedConstraint)
			disk.commit()

			# the creation will take a bit of time
			time.sleep(3)

			# the partition has a real path now as it was created
			part_mod.dev_path = Path(partition.path)

			info = get_lsblk_info(part_mod.dev_path)

			if not info.partuuid:
				raise DiskError(f'Unable to determine new partition uuid: {part_mod.dev_path}')

			part_mod.partuuid = info.partuuid
			part_mod.uuid = info.uuid
		except PartitionException as ex:
			raise DiskError(f'Unable to add partition, most likely due to overlapping sectors: {ex}') from ex

	def _umount_all_existing(self, modification: DeviceModification):
		log(f'Unmounting existing partitions: {modification.device_path}', level=logging.INFO)

		existing_partitions = self._devices[modification.device_path].partition_info

		for partition in existing_partitions:
			log(f'Unmounting: {partition.path}', level=logging.INFO)

			# un-mount for existing encrypted partitions
			if partition.fs_type == FilesystemType.Crypto_luks:
				Luks2(partition.path).lock()
			else:
				self.umount(partition.path, recursive=True)

	def partition(
		self,
		modification: DeviceModification,
		partition_table: Optional[PartitionTable] = None
	):
		"""
		Create a partition table on the block device and create all partitions.
		"""

		if modification.wipe and not partition_table:
			raise ValueError('modification is marked as wipe but no partitioning table was provided')

		# TODO this check should probably run in the setup process rather than during the installation
		if modification.wipe and partition_table.MBR and len(modification.partitions) > 3:
			raise DiskError("Too many partitions on disk, MBR disks can only have 3 primary partitions")

		# make sure all devices are unmounted
		self._umount_all_existing(modification)

		# WARNING: the entire device will be wiped and all data lost
		if modification.wipe:
			log(f'Wipe all data: {modification.device_path}')
			self.wipe_dev(modification.device)

			disk = parted.freshDisk(modification.device.disk.device, partition_table.value)
		else:
			log(f'Re-use existing device: {modification.device_path}')
			disk = modification.device.disk

		log(f'Creating partitions: {modification.device_path}')

		# TODO sort by delete first

		for part_mod in modification.partitions:
			# don't touch existing partitions
			if not part_mod.is_exists():
				# if the entire disk got nuked then we don't have to delete
				# any existing partitions anymore because they're all gone already
				requires_delete = modification.wipe is False
				self._perform_partitioning(part_mod, modification.device, disk, requires_delete=requires_delete)

		self.partprobe(modification.device.device_info.path)

	def mount(
		self,
		dev_path: Path,
		target_mountpoint: Path,
		mount_fs: Optional[str] = None,
		create_target_mountpoint: bool = True,
		options: List[str] = []
	):
		if create_target_mountpoint and not target_mountpoint.exists():
			target_mountpoint.mkdir(parents=True, exist_ok=True)

		if not target_mountpoint.exists():
			raise ValueError('Target mountpoint does not exist')

		lsblk_info = get_lsblk_info(dev_path)
		if target_mountpoint in lsblk_info.mountpoints:
			log(f'Device already mounted at {target_mountpoint}')
			return

		log(f'Mounting {dev_path} to {target_mountpoint}', level=logging.INFO)

		options = ','.join(options)
		options = f'-o {options}' if options else ''

		mount_fs = f'-t {mount_fs}' if mount_fs else ''

		command = f'mount {mount_fs} {options} {dev_path} {target_mountpoint}'

		try:
			result = SysCommand(command)
			if result.exit_code != 0:
				raise DiskError(f'Could not mount {dev_path}: {command}\n{result.decode()}')
		except SysCallError as err:
			raise DiskError(f'Could not mount {dev_path}: {command}\n{err.message}')

	def umount(self, path: Path, recursive: bool = False):
		lsblk_info = get_lsblk_info(path)

		if len(lsblk_info.mountpoints) > 0:
			log(f'Partition {path} is currently mounted at: {lsblk_info.mountpoints}')

			for mountpoint in lsblk_info.mountpoints:
				log(f'Attempting to umount: {mountpoint}')

				command = 'umount'

				if recursive:
					command += ' -R'

				try:
					SysCommand(f'{command} {mountpoint}')
				except SysCallError as err:
					# Without to much research, it seams that low error codes are errors.
					# And above 8k is indicators such as "/dev/x not mounted.".
					# So anything in between 0 and 8k are errors (?).
					if err and 0 < err.exit_code < 8000:
						log(f'Unable to umount partition {mountpoint}: {err.message}', level=logging.DEBUG)
						raise DiskError(err.message)

	def discover_modifications_by_mountpoint(self, base_mountpoint: Path) -> List[DeviceModification]:
		lsblk_infos = get_lsblk_by_mountpoint(base_mountpoint, as_prefix=True)
		part_mods = {}

		for lsblk in lsblk_infos:
			# we are looking for the real partition not the mapper
			if lsblk.type == 'crypt':
				parent_lsblk = get_lsblk_info(f'/dev/{lsblk.pkname}')
				part_info = self.find_partition(parent_lsblk.path)
			else:
				part_info = self.find_partition(lsblk.path)

			if not part_info:
				raise DiskError(f'Unable to find partition information: {lsblk.path}')

			part_mods.setdefault(part_info.disk.device.path, []).append(
				PartitionModification.from_existing_partition(part_info)
			)

		mods = []
		for device_path, part_mods in part_mods.items():
			mods.append(
				DeviceModification(self._devices.get(device_path), False, part_mods)
			)

		return mods

	def partprobe(self, path: Optional[Path] = None):
		if path is not None:
			command = f'partprobe {path}'
		else:
			command = 'partprobe'

		try:
			result = SysCommand(command)
			if result.exit_code != 0:
				log(f'Error calling partprobe: {result.decode()}', level=logging.DEBUG)
				raise DiskError(f'Could not perform partprobe on {path}: {result.decode()}')
		except SysCallError as error:
			log(f"partprobe experienced an error for {path}: {error}", level=logging.DEBUG)
			raise DiskError(f'Could not perform partprobe on {path}: {error}')

	def _wipe(self, dev_path: Path):
		"""
		Wipe a device (partition or otherwise) of meta-data, be it file system, LVM, etc.
		@param dev_path:    Device path of the partition to be wiped.
		@type dev_path:     str
		"""
		with open(dev_path, 'wb') as p:
			p.write(bytearray(1024))

	def wipe_dev(self, block_device: BDevice):
		"""
		Wipe the block device of meta-data, be it file system, LVM, etc.
		This is not intended to be secure, but rather to ensure that
		auto-discovery tools don't recognize anything here.
		"""
		log(f'Wiping partitions and metadata: {block_device.device_info.path}')
		for partition in block_device.partition_info:
			self._wipe(partition.path)

		self._wipe(block_device.device_info.path)


device_handler = DeviceHandler()
