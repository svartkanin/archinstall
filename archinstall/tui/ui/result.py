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
	_item: MenuItem | None = None

	def has_data(self) -> bool:
		return self._data is not None

	def item(self) -> MenuItem:
		if self._item is not None:
			return self._item

		raise ValueError('No item found')

	def value(self) -> ValueT:
		if self._item is not None and self._item.value is not None:
			return self._item.value
		elif type(self._data) is not list and self._data is not None:
			return cast(ValueT, self._data)

		raise ValueError('No value found')

	def values(self) -> list[ValueT]:
		assert type(self._data) is list
		return cast(list[ValueT], self._data)
