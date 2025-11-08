from typing import TypeVar

from archinstall.lib.output import debug
from archinstall.tui.menu_item import MenuItemGroup
from archinstall.tui.ui.components import OptionListScreen, tui
from archinstall.tui.ui.result import Result, ResultType

ValueT = TypeVar('ValueT')


class SingleSelection[ValueT]:
	def __init__(
		self,
		header: str,
		group: MenuItemGroup,
		allow_skip: bool = True,
		allow_reset: bool = False,
	):
		self._header = header
		self._group: MenuItemGroup = group
		self._allow_skip = allow_skip
		self._allow_reset = allow_reset

	def show(self) -> Result[ValueT]:
		result = tui.run(self)
		if result is None:
			return Result(ResultType.Selection, None)
		return result

	async def run(self) -> None:
		debug('Running single selection menu')

		result = await OptionListScreen[ValueT](
			self._group,
			header=self._header,
			allow_skip=self._allow_skip,
			allow_reset=self._allow_reset,
		).run()

		tui.exit(result)
