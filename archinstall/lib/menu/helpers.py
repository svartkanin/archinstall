from typing import Awaitable, Callable, Literal, TypeVar

from archinstall.lib.output import debug
from archinstall.lib.translationhandler import tr
from archinstall.tui.menu_item import MenuItemGroup
from archinstall.tui.ui.components import ConfirmationScreen, InputScreen, LoadingScreen, NotifyScreen, OptionListScreen, SelectListScreen, TableSelectionScreen, tui
from archinstall.tui.ui.result import Result, ResultType

ValueT = TypeVar('ValueT')


class SelectionMenu[ValueT]:
	def __init__(
		self,
		group: MenuItemGroup,
		header: str | None = None,
		allow_skip: bool = True,
		allow_reset: bool = False,
		preview_orientation: Literal['right', 'bottom'] | None = None,
		multi: bool = False,
		search_enabled: bool = False,
		show_frame: bool = True
	):
		self._header = header
		self._group: MenuItemGroup = group
		self._allow_skip = allow_skip
		self._allow_reset = allow_reset
		self._preview_orientation = preview_orientation
		self._multi = multi
		self._search_enabled = search_enabled
		self._show_frame = show_frame

	def show(self) -> Result[ValueT]:
		result = tui.run(self)
		return result

	async def _run(self) -> None:
		if not self._multi:
			result = await OptionListScreen[ValueT](
				self._group,
				header=self._header,
				allow_skip=self._allow_skip,
				allow_reset=self._allow_reset,
				preview_location=self._preview_orientation,
				show_frame=self._show_frame
			).run()
		else:
			result = await SelectListScreen[ValueT](
				self._group,
				header=self._header,
				allow_skip=self._allow_skip,
				allow_reset=self._allow_reset,
				preview_location=self._preview_orientation
			).run()

		if result.type_ == ResultType.Reset:
			confirmed = await _confirm_reset()

			if confirmed.value() is False:
				return await self._run()

		tui.exit(result)


class Confirmation[ValueT]:
	def __init__(
		self,
		group: MenuItemGroup,
		header: str | None = None,
		allow_skip: bool = True,
		allow_reset: bool = False,
	):
		self._header = header
		self._group: MenuItemGroup = group
		self._allow_skip = allow_skip
		self._allow_reset = allow_reset

	def show(self) -> Result[ValueT]:
		result = tui.run(self)
		return result

	async def _run(self) -> None:
		result = await ConfirmationScreen[ValueT](
			self._group,
			header=self._header,
			allow_skip=self._allow_skip,
			allow_reset=self._allow_reset,
		).run()

		if result.type_ == ResultType.Reset:
			confirmed = await _confirm_reset()

			if confirmed.value() is False:
				return await self._run()

		tui.exit(result)


class Notify[ValueT]:
	def __init__(
		self,
		header: str | None = None,
	):
		self._header = header

	def show(self) -> Result[ValueT]:
		result = tui.run(self)
		return result

	async def _run(self) -> None:
		await NotifyScreen(header=self._header).run()
		tui.exit(True)


class Input[ValueT]:
	def __init__(
		self,
		header: str | None = None,
		placeholder: str | None = None,
		password: bool = False,
		default_value: str | None = None,
		allow_skip: bool = True,
		allow_reset: bool = False,
	):
		self._header = header
		self._placeholder = placeholder
		self._password = password
		self._default_value = default_value
		self._allow_skip = allow_skip
		self._allow_reset = allow_reset

	def show(self) -> Result[ValueT]:
		result = tui.run(self)
		return result

	async def _run(self) -> None:
		result = await InputScreen(
			header=self._header,
			placeholder=self._placeholder,
			password=self._password,
			default_value=self._default_value,
			allow_skip=self._allow_skip,
			allow_reset=self._allow_reset,
		).run()

		if result.type_ == ResultType.Reset:
			confirmed = await _confirm_reset()

			if confirmed.value() is False:
				return await self._run()

		tui.exit(result)


class Loading[ValueT]:
	def __init__(
		self,
		header: str | None = None,
		timer: int = 3
	):
		self._header = header
		self._timer = timer

	def show(self) -> Result[ValueT]:
		result = tui.run(self)
		return result

	async def _run(self) -> None:
		await LoadingScreen(self._timer, self._header).run()
		tui.exit(True)


class TableMenu[ValueT]:
	def __init__(
		self,
		header: str | None = None,
		data: list[ValueT] | None = None,
		data_callback: Callable[[], Awaitable[list[ValueT]]] | None = None,
		allow_reset: bool = False,
		allow_skip: bool = False,
		loading_header: str | None = None,
		multi: bool = False,
		preview_orientation: str = 'right',
	):
		self._header = header
		self._data = data
		self._data_callback = data_callback
		self._loading_header = loading_header
		self._allow_skip = allow_skip
		self._allow_reset = allow_reset
		self._multi = multi
		self._preview_orientation = preview_orientation

		if self._data is None and self._data_callback is None:
			raise ValueError('Either data or data_callback must be provided')

	def show(self) -> Result[ValueT]:
		result = tui.run(self)
		return result

	async def _run(self) -> None:
		result = await TableSelectionScreen[ValueT](
			header=self._header,
			data=self._data,
			data_callback=self._data_callback,
			allow_skip=self._allow_skip,
			allow_reset=self._allow_reset,
			loading_header=self._loading_header,
		).run()

		if result.type_ == ResultType.Reset:
			confirmed = await _confirm_reset()

			if confirmed.value() is False:
				return await self._run()

		tui.exit(result)


async def _confirm_reset() -> Result[bool]:
	return await ConfirmationScreen[bool](
		MenuItemGroup.yes_no(),
		header=tr('Are you sure you want to reset this setting?'),
		allow_skip=False,
		allow_reset=False,
	).run()
