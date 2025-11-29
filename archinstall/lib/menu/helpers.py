from collections.abc import Awaitable, Callable
from typing import Literal, TypeVar, override

from textual.validation import ValidationResult, Validator

from archinstall.lib.translationhandler import tr
from archinstall.tui.menu_item import MenuItemGroup
from archinstall.tui.ui.components import (
	ConfirmationScreen,
	InputScreen,
	LoadingScreen,
	NotifyScreen,
	OptionListScreen,
	SelectListScreen,
	TableSelectionScreen,
	tui,
)
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
		show_frame: bool = False,
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
				show_frame=self._show_frame,
			).run()
		else:
			result = await SelectListScreen[ValueT](
				self._group, header=self._header, allow_skip=self._allow_skip, allow_reset=self._allow_reset, preview_location=self._preview_orientation
			).run()

		if result.type_ == ResultType.Reset:
			confirmed = await _confirm_reset()

			if confirmed.get_value() is False:
				return await self._run()

		tui.exit(result)


class Confirmation:
	def __init__(
		self,
		header: str | None = None,
		allow_skip: bool = True,
		allow_reset: bool = False,
		preset: bool = False,
	):
		self._header = header
		self._allow_skip = allow_skip
		self._allow_reset = allow_reset
		self._preset = preset

		self._group: MenuItemGroup = MenuItemGroup.yes_no()
		self._group.set_focus_by_value(preset)

	def show(self) -> Result[bool]:
		result = tui.run(self)
		return result

	async def _run(self) -> None:
		result = await ConfirmationScreen[bool](
			self._group,
			header=self._header,
			allow_skip=self._allow_skip,
			allow_reset=self._allow_reset,
		).run()

		if result.type_ == ResultType.Reset:
			confirmed = await _confirm_reset()

			if confirmed.get_value() is False:
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


class GenericValidator(Validator):
	def __init__(self, validator_callback: Callable[[str | None], str | None]) -> None:
		super().__init__()

		self._validator_callback = validator_callback

	@override
	def validate(self, value: str) -> ValidationResult:
		result = self._validator_callback(value)

		if result is not None:
			return self.failure(result)

		return self.success()


class Input:
	def __init__(
		self,
		header: str | None = None,
		placeholder: str | None = None,
		password: bool = False,
		default_value: str | None = None,
		allow_skip: bool = True,
		allow_reset: bool = False,
		validator_callback: Callable[[str | None], str | None] | None = None,
	):
		self._header = header
		self._placeholder = placeholder
		self._password = password
		self._default_value = default_value
		self._allow_skip = allow_skip
		self._allow_reset = allow_reset
		self._validator_callback = validator_callback

	def show(self) -> Result[ValueT]:
		result = tui.run(self)
		return result

	async def _run(self) -> None:
		validator = GenericValidator(self._validator_callback) if self._validator_callback else None

		result = await InputScreen(
			header=self._header,
			placeholder=self._placeholder,
			password=self._password,
			default_value=self._default_value,
			allow_skip=self._allow_skip,
			allow_reset=self._allow_reset,
			validator=validator,
		).run()

		if result.type_ == ResultType.Reset:
			confirmed = await _confirm_reset()

			if confirmed.get_value() is False:
				return await self._run()

		tui.exit(result)


class Loading[ValueT]:
	def __init__(
		self,
		header: str | None = None,
		timer: int = 3,
		data_callback: Callable[[], Awaitable[ValueT]] | None = None,
	):
		self._header = header
		self._timer = timer
		self._data_callback = data_callback

	def show(self) -> ValueT | None:
		result = tui.run(self)

		match result.type_:
			case ResultType.Selection:
				if result.has_value() is False:
					return None
				return result.get_value()
			case _:
				return None

	async def _run(self) -> None:
		if self._data_callback:
			result = await LoadingScreen(header=self._header, data_callback=self._data_callback).run()
			tui.exit(result)
		else:
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
			multi=self._multi,
		).run()

		if result.type_ == ResultType.Reset:
			confirmed = await _confirm_reset()

			if confirmed.get_value() is False:
				return await self._run()

		tui.exit(result)


async def _confirm_reset() -> Result[bool]:
	return await ConfirmationScreen[bool](
		MenuItemGroup.yes_no(),
		header=tr('Are you sure you want to reset this setting?'),
		allow_skip=False,
		allow_reset=False,
	).run()
