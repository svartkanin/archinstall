from typing import Dict, Any, List

from .blockdevice import BlockDevice


class PartitioningVisualizer:
	def __init__(self, blockdevice: BlockDevice, width: int = 150, heeight: int = 20):
		self._blockdevice = blockdevice
		self._width = width

	def _center_text(self, text: str, available_width: int) -> str:
		# we'll put at least a space left and right
		available_width = available_width - 2

		# if the text doesn't fit in the available box
		# we'll cut it off, leaving a space left and right
		possible_text_len = available_width - len(text)
		if possible_text_len < 0:
			text = text[:available_width]

		left_spacing = int((available_width - len(text)) / 2) * ' '
		right_spacing = (available_width - len(left_spacing) - len(text)) * ' '

		return f' {left_spacing}{text}{right_spacing} '

	def _header_line(self) -> str:
		path = self._blockdevice.path
		return self._center_text(path, self._width)

	def _horizontal_boarder(self) -> str:
		return '+' + (self._width - 2) * '-' + '+'

	# def _horizontal_filler(self) -> str:
	# 	return '|' + (self._width - 2) * ' ' + '|'

	def _process_partition_sizes(self) -> List[Dict[str, Any]]:
		block_size = self._blockdevice.size
		display_data = []

		from archinstall import log
		log(self._blockdevice.partitions.values())

		for partition in self._blockdevice.partitions.values():
			block_percentage = partition.size / block_size
			entry = {
				'path': partition.path,
				'size': f'{partition.size}GB',
				'filesystem_type': partition.filesystem,
				'block_percent': block_percentage
			}

			entry['min_width'] = max([len(str(v)) for v in entry.values()])
			display_data.append(entry)

		log(display_data)
		return display_data

	def _create_attr_line(self, data: List[Dict[str, Any]], attr: str) -> str:
		line = '|'
		available_space = self._width - 2

		for entry in data:
			box_width = int(self._width * entry['block_percent'])
			proposed_width = max([box_width, entry['min_width']])
			width = min([available_space, proposed_width])

			line += self._center_text(str(entry[attr]), width) + '|'
			available_space -= width

		return line

	def _partition_lines(self) -> str:
		lines = ''
		partition_attr = self._process_partition_sizes()
		data = sorted(partition_attr, key=lambda x: x['path'])

		lines += self._create_attr_line(data, 'path') + '\n'
		lines += self._create_attr_line(data, 'size') + '\n'
		lines += self._create_attr_line(data, 'filesystem_type') + '\n'

		return lines

	def paint(self) -> str:
		output = self._header_line() + '\n'
		output += self._horizontal_boarder() + '\n'

		output += self._partition_lines()

		output += self._horizontal_boarder() + '\n'

		return output


