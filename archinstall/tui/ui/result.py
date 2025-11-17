from dataclasses import dataclass
from enum import Enum, auto
from typing import cast

from archinstall.tui import MenuItem


class ResultType(Enum):
	Selection = auto()
	Skip = auto()
	Reset = auto()


@dataclass
class Result[ValueT]:
	type_: ResultType
	_data: ValueT | list[ValueT] | None = None
	_item: MenuItem | list[MenuItem] | None = None

	def has_data(self) -> bool:
		return self._data is not None

	def item(self) -> MenuItem:
		if isinstance(self._item, list) or self._item is None:
			raise ValueError('Invalid item type')
		return self._item

	def items(self) -> list[MenuItem]:
		if isinstance(self._item, list):
			return self._item

		raise ValueError('Invalid item type')

	def value(self) -> ValueT:
		if self._item is not None:
			return self.item().get_value()	# type: ignore[no-any-return]

		if type(self._data) is not list and self._data is not None:
			return cast(ValueT, self._data)

		raise ValueError('No value found')

	def values(self) -> list[ValueT]:
		if self._item is not None:
			return [i.get_value() for i in self.items()]

		assert type(self._data) is list
		return cast(list[ValueT], self._data)
