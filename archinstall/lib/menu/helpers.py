from typing import Literal, TypeVar

from archinstall.lib.output import debug
from archinstall.lib.translationhandler import tr
from archinstall.tui.menu_item import MenuItemGroup
from archinstall.tui.ui.components import ConfirmationScreen, OptionListScreen, tui
from archinstall.tui.ui.result import Result, ResultType

ValueT = TypeVar('ValueT')


class SingleSelection[ValueT]:
	def __init__(
		self,
		group: MenuItemGroup,
		header: str | None = None,
		allow_skip: bool = True,
		allow_reset: bool = False,
		preview_orientation: Literal['right', 'bottom'] | None = None
	):
		self._header = header
		self._group: MenuItemGroup = group
		self._allow_skip = allow_skip
		self._allow_reset = allow_reset
		self._preview_orientation = preview_orientation

	def show(self) -> Result[ValueT]:
		result = tui.run(self)
		return result

	async def _run(self) -> None:
		debug('Running single selection menu')

		result = await OptionListScreen[ValueT](
			self._group,
			header=self._header,
			allow_skip=self._allow_skip,
			allow_reset=self._allow_reset,
			preview_location=self._preview_orientation
		).run()

		if result.type_ == ResultType.Reset:
			confirmed = await ConfirmationScreen[bool](
				MenuItemGroup.yes_no(),
				header=tr('Are you sure you want to reset this setting?'),
				allow_skip=False,
				allow_reset=False,
			).run()

			if confirmed.value() is False:
				return await self._run()

		tui.exit(result)

