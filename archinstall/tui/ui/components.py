from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, ClassVar, Literal, TypeVar, override

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.events import Key
from textual.screen import Screen
from textual.validation import Validator
from textual.widgets import Button, DataTable, Footer, Input, LoadingIndicator, OptionList, Rule, SelectionList, Static
from textual.widgets._data_table import RowKey
from textual.widgets.option_list import Option
from textual.widgets.selection_list import Selection
from textual.worker import WorkerCancelled

from archinstall.lib.output import debug
from archinstall.lib.translationhandler import tr
from archinstall.tui.menu_item import MenuItem, MenuItemGroup
from archinstall.tui.ui.result import Result, ResultType

ValueT = TypeVar('ValueT')


class BaseScreen(Screen[Result[ValueT]]):
	BINDINGS: ClassVar = [
		Binding('escape', 'cancel_operation', 'Cancel', show=False),
		Binding('ctrl+c', 'reset_operation', 'Reset', show=False),
	]

	def __init__(self, allow_skip: bool = False, allow_reset: bool = False):
		super().__init__()
		self._allow_skip = allow_skip
		self._allow_reset = allow_reset

	def action_cancel_operation(self) -> None:
		if self._allow_skip:
			_ = self.dismiss(Result(ResultType.Skip))

	async def action_reset_operation(self) -> None:
		if self._allow_reset:
			_ = self.dismiss(Result(ResultType.Reset))

	def _compose_header(self) -> ComposeResult:
		"""Compose the app header if global header text is available"""
		if tui.global_header:
			yield Static(tui.global_header, classes='app-header')


class LoadingScreen(BaseScreen[None]):
	CSS = """
	LoadingScreen {
		align: center middle;
		background: transparent;
	}

	.dialog {
		align: center middle;
		width: 100%;
		border: none;
		background: transparent;
	}

	.header {
		text-align: center;
		margin-bottom: 1;
	}

	LoadingIndicator {
		align: center middle;
	}
	"""

	def __init__(
		self,
		timer: int = 3,
		data_callback: Callable[[], Any] | None = None,
		header: str | None = None,
	):
		super().__init__()
		self._timer = timer
		self._header = header
		self._data_callback = data_callback

	async def run(self) -> Result[None]:
		assert TApp.app
		return await TApp.app.show(self)

	@override
	def compose(self) -> ComposeResult:
		yield from self._compose_header()

		with Center():
			with Vertical(classes='dialog'):
				if self._header:
					yield Static(self._header, classes='header')
				yield Center(LoadingIndicator())

		yield Footer()

	# def on_mount(self) -> None:
	# self.set_timer(self._timer, self.action_pop_screen)

	def on_mount(self) -> None:
		if self._data_callback:
			self._exec_callback()
		else:
			self.set_timer(self._timer, self.action_pop_screen)

	@work(thread=True)
	def _exec_callback(self) -> None:
		assert self._data_callback
		result = self._data_callback()
		_ = self.dismiss(Result(ResultType.Selection, _data=result))

	def action_pop_screen(self) -> None:
		_ = self.dismiss()


class OptionListScreen(BaseScreen[ValueT]):
	"""
	List single selection menu
	"""

	BINDINGS: ClassVar = [
		Binding('j', 'cursor_down', 'Down', show=False),
		Binding('k', 'cursor_up', 'Up', show=False),
	]

	CSS = """
		OptionListScreen {
			align-horizontal: center;
			align-vertical: middle;
			background: transparent;
		}

		.content-container {
			width: 1fr;
			height: 1fr;
			max-height: 100%;

			margin-top: 2;
			margin-bottom: 2;
			padding: 0;

			background: transparent;
		}

		.header {
			text-align: center;
			margin-top: 1;
			margin-bottom: 0;
			width: 100%;
			height: auto;
			background: transparent;
		}

		.list-container {
			width: auto;
			height: auto;
			max-height: 100%;

			margin-top: 2;
			margin-bottom: 2;
			padding: 0;

			background: transparent;
		}

		.no-border {
			border: none;
		}

		OptionList {
			width: auto;
			height: auto;
			min-width: 20%;
			max-height: 1fr;

			padding-top: 0;
			padding-bottom: 0;
			padding-left: 1;
			padding-right: 1;

			scrollbar-size-vertical: 1;

			background: transparent;
		}
	"""

	def __init__(
		self,
		group: MenuItemGroup,
		header: str | None = None,
		allow_skip: bool = False,
		allow_reset: bool = False,
		preview_location: Literal['right', 'bottom'] | None = None,
		show_frame: bool = False,
	):
		super().__init__(allow_skip, allow_reset)
		self._group = group
		self._header = header
		self._preview_location = preview_location
		self._show_frame = show_frame

	def action_cursor_down(self) -> None:
		option_list = self.query_one('#option_list_widget', OptionList)
		option_list.action_cursor_down()

	def action_cursor_up(self) -> None:
		option_list = self.query_one('#option_list_widget', OptionList)
		option_list.action_cursor_up()

	async def run(self) -> Result[ValueT]:
		assert TApp.app
		return await TApp.app.show(self)

	def _get_options(self) -> list[Option]:
		options = []

		for item in self._group.get_enabled_items():
			disabled = True if item.read_only else False
			options.append(Option(item.text, id=item.get_id(), disabled=disabled))

		return options

	@override
	def compose(self) -> ComposeResult:
		yield from self._compose_header()

		options = self._get_options()

		with Vertical(classes='content-container'):
			if self._header:
				yield Static(self._header, classes='header', id='header')

			option_list = OptionList(*options, id='option_list_widget')
			option_list.highlighted = self._group.get_focused_index()

			if not self._show_frame:
				option_list.classes = 'no-border'

			if self._preview_location is None:
				with Center():
					with Vertical(classes='list-container'):
						yield option_list
			else:
				Container = Horizontal if self._preview_location == 'right' else Vertical
				rule_orientation: Literal['horizontal', 'vertical'] = 'vertical' if self._preview_location == 'right' else 'horizontal'

				with Container():
					yield option_list
					yield Rule(orientation=rule_orientation)
					yield Static('', id='preview_content')

		yield Footer()

	def on_mount(self) -> None:
		focused_item = self._group.focus_item
		if focused_item:
			self._set_preview(focused_item.get_id())

	def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
		selected_option = event.option
		if selected_option.id is not None:
			item = self._group.find_by_id(selected_option.id)
			_ = self.dismiss(Result(ResultType.Selection, _item=item))

	def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
		if event.option.id:
			self._set_preview(event.option.id)

	def _set_preview(self, item_id: str) -> None:
		if self._preview_location is None:
			return None

		preview_widget = self.query_one('#preview_content', Static)
		item = self._group.find_by_id(item_id)

		if item.preview_action is not None:
			maybe_preview = item.preview_action(item)
			if maybe_preview is not None:
				preview_widget.update(maybe_preview)
				return

		preview_widget.update('')


class SelectListScreen(BaseScreen[ValueT]):
	"""
	Multi selection menu
	"""

	BINDINGS: ClassVar = [
		Binding('j', 'cursor_down', 'Down', show=False),
		Binding('k', 'cursor_up', 'Up', show=False),
	]

	CSS = """
		SelectListScreen {
			align-horizontal: center;
			align-vertical: middle;
			background: transparent;
		}

		.content-container {
			width: 1fr;
			height: 1fr;
			max-height: 100%;

			margin-top: 2;
			margin-bottom: 2;
			padding: 0;

			background: transparent;
		}

		.header {
			text-align: center;
			margin-top: 1;
			margin-bottom: 0;
			width: 100%;
			height: auto;
			background: transparent;
		}

		.list-container {
			width: auto;
			height: auto;
			max-height: 100%;

			margin-top: 2;
			margin-bottom: 2;
			padding: 0;

			background: transparent;
		}

		.no-border {
			border: none;
		}

		SelectionList {
			width: auto;
			height: auto;
			max-height: 1fr;

			padding-top: 0;
			padding-bottom: 0;
			padding-left: 1;
			padding-right: 1;

			scrollbar-size-vertical: 1;

			background: transparent;
		}
	"""

	def __init__(
		self,
		group: MenuItemGroup,
		header: str | None = None,
		allow_skip: bool = False,
		allow_reset: bool = False,
		preview_location: Literal['right', 'bottom'] | None = None,
		show_frame: bool = False,
	):
		super().__init__(allow_skip, allow_reset)
		self._group = group
		self._header = header
		self._preview_location = preview_location
		self._show_frame = show_frame

	def action_cursor_down(self) -> None:
		select_list = self.query_one('#select_list_widget', OptionList)
		select_list.action_cursor_down()

	def action_cursor_up(self) -> None:
		select_list = self.query_one('#select_list_widget', OptionList)
		select_list.action_cursor_up()

	def on_key(self, event: Key) -> None:
		if event.key == 'enter':
			items: list[MenuItem] = self.query_one(SelectionList).selected
			_ = self.dismiss(Result(ResultType.Selection, _item=items))

	async def run(self) -> Result[ValueT]:
		assert TApp.app
		return await TApp.app.show(self)

	def _get_selections(self) -> list[Selection[MenuItem]]:
		selections = []

		for item in self._group.get_enabled_items():
			is_selected = item in self._group.selected_items
			selection = Selection(item.text, item, is_selected)
			selections.append(selection)

		return selections

	@override
	def compose(self) -> ComposeResult:
		yield from self._compose_header()

		selections = self._get_selections()

		with Vertical(classes='content-container'):
			if self._header:
				yield Static(self._header, classes='header', id='header')

			selection_list = SelectionList[MenuItem](*selections, id='select_list_widget')

			if not self._show_frame:
				selection_list.classes = 'no-border'

			if self._preview_location is None:
				with Center():
					with Vertical(classes='list-container'):
						yield selection_list
			else:
				Container = Horizontal if self._preview_location == 'right' else Vertical
				rule_orientation: Literal['horizontal', 'vertical'] = 'vertical' if self._preview_location == 'right' else 'horizontal'

				with Container():
					yield selection_list
					yield Rule(orientation=rule_orientation)
					yield Static('', id='preview_content')

		yield Footer()

	def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
		selected_option = event.option
		if selected_option.id:
			item = self._group.find_by_id(selected_option.id)
			_ = self.dismiss(Result(ResultType.Selection, _item=item))

	def on_selection_list_selection_highlighted(self, event: SelectionList.SelectionHighlighted[ValueT]) -> None:
		if self._preview_location is None:
			return None

		index = event.selection_index
		selection: Selection[MenuItem] = self.query_one(SelectionList).get_option_at_index(index)
		item: MenuItem = selection.value

		preview_widget = self.query_one('#preview_content', Static)

		if item.preview_action is not None:
			maybe_preview = item.preview_action(item)
			if maybe_preview is not None:
				preview_widget.update(maybe_preview)
				return

		preview_widget.update('')


class ConfirmationScreen(BaseScreen[ValueT]):
	BINDINGS: ClassVar = [
		Binding('l', 'focus_right', 'Focus right', show=False),
		Binding('h', 'focus_left', 'Focus left', show=False),
		Binding('right', 'focus_right', 'Focus right', show=False),
		Binding('left', 'focus_left', 'Focus left', show=False),
	]

	CSS = """
	ConfirmationScreen {
		align: center middle;
	}

	.dialog-wrapper {
		align: center middle;
		height: 100%;
		width: 100%;
	}

	.dialog {
		width: 80;
		height: 10;
		border: none;
		background: transparent;
	}

	.dialog-content {
		padding: 1;
		height: 100%;
	}

	.message {
		text-align: center;
		margin-bottom: 1;
	}

	.buttons {
		align: center middle;
		background: transparent;
	}

	Button {
		width: 4;
		height: 3;
		background: transparent;
		margin: 0 1;
	}

	Button.-active {
		background: #1793D1;
		color: white;
		border: none;
		text-style: none;
	}
	"""

	def __init__(
		self,
		group: MenuItemGroup,
		header: str,
		allow_skip: bool = False,
		allow_reset: bool = False,
	):
		super().__init__(allow_skip, allow_reset)
		self._group = group
		self._header = header

	async def run(self) -> Result[ValueT]:
		assert TApp.app
		return await TApp.app.show(self)

	@override
	def compose(self) -> ComposeResult:
		yield from self._compose_header()

		with Center(classes='dialog-wrapper'):
			with Vertical(classes='dialog'):
				with Vertical(classes='dialog-content'):
					yield Static(self._header, classes='message')
					with Horizontal(classes='buttons'):
						for item in self._group.items:
							yield Button(item.text, id=item.key)

		yield Footer()

	def on_mount(self) -> None:
		self.update_selection()

	def update_selection(self) -> None:
		focused = self._group.focus_item
		buttons = self.query(Button)

		if not focused:
			return

		for button in buttons:
			if button.id == focused.key:
				button.add_class('-active')
				button.focus()
			else:
				button.remove_class('-active')

	def action_focus_right(self) -> None:
		self._group.focus_next()
		self.update_selection()

	def action_focus_left(self) -> None:
		self._group.focus_prev()
		self.update_selection()

	def on_key(self, event: Key) -> None:
		if event.key == 'enter':
			item = self._group.focus_item
			if not item:
				return None
			_ = self.dismiss(Result(ResultType.Selection, _item=item))


class NotifyScreen(ConfirmationScreen[ValueT]):
	def __init__(self, header: str):
		group = MenuItemGroup([MenuItem(tr('Ok'))])
		super().__init__(group, header)


class InputScreen(BaseScreen[str]):
	CSS = """
	InputScreen {
		align: center middle;
	}

	.input-header {
		text-align: center;
		width: 100%;
		padding-top: 2;
		padding-bottom: 1;
		margin: 0 0;
		color: white;
		text-style: bold;
		background: transparent;
	}

	.container-wrapper {
		align: center top;
		width: 100%;
		height: 1fr;
	}

	.input-content {
		width: 60;
		height: 10;
	}

	.input-failure {
		color: red;
		text-align: center;
	}

	Input {
		border: solid $accent;
		background: transparent;
		height: 3;
	}

	Input .input--cursor {
		color: white;
	}

	Input:focus {
		border: solid $primary;
	}
	"""

	def __init__(
		self,
		header: str | None = None,
		placeholder: str | None = None,
		password: bool = False,
		default_value: str | None = None,
		allow_reset: bool = False,
		allow_skip: bool = False,
		validator: Validator | None = None,
	):
		super().__init__(allow_skip, allow_reset)
		self._header = header or ''
		self._placeholder = placeholder or ''
		self._password = password
		self._default_value = default_value or ''
		self._allow_reset = allow_reset
		self._allow_skip = allow_skip
		self._validator = validator

	async def run(self) -> Result[str]:
		assert TApp.app
		return await TApp.app.show(self)

	@override
	def compose(self) -> ComposeResult:
		yield from self._compose_header()

		yield Static(self._header, classes='input-header')

		with Center(classes='container-wrapper'):
			with Vertical(classes='input-content'):
				yield Input(
					placeholder=self._placeholder,
					password=self._password,
					value=self._default_value,
					id='main_input',
					validators=self._validator,
					validate_on=['submitted'],
				)
				yield Static('', classes='input-failure', id='input-failure')

		yield Footer()

	def on_mount(self) -> None:
		input_field = self.query_one('#main_input', Input)
		input_field.focus()

	def on_input_submitted(self, event: Input.Submitted) -> None:
		if event.validation_result and not event.validation_result.is_valid:
			failures = [failure.description for failure in event.validation_result.failures if failure.description]
			failure_out = ', '.join(failures)

			self.query_one('#input-failure', Static).update(failure_out)
		else:
			_ = self.dismiss(Result(ResultType.Selection, _data=event.value))


class TableSelectionScreen(BaseScreen[ValueT]):
	BINDINGS: ClassVar = [
		Binding('j', 'cursor_down', 'Down', show=False),
		Binding('k', 'cursor_up', 'Up', show=False),
		Binding('space', 'toggle_selection', 'Toggle Selection', show=False),
	]

	CSS = """
		TableSelectionScreen {
			align: center middle;
			background: transparent;
		}

		DataTable {
			height: auto;
			width: auto;
			border: none;
			background: transparent;
		}

		DataTable .datatable--header {
			background: transparent;
			border: solid;
		}

		.content-container {
			width: auto;
			background: transparent;
			padding: 2 0;
		}

		.header {
			text-align: center;
			margin-bottom: 1;
		}

		LoadingIndicator {
			height: auto;
			background: transparent;
		}
	"""

	def __init__(
		self,
		header: str | None = None,
		data: list[ValueT] | None = None,
		data_callback: Callable[[], Awaitable[list[ValueT]]] | None = None,
		allow_reset: bool = False,
		allow_skip: bool = False,
		loading_header: str | None = None,
		multi: bool = False,
	):
		super().__init__(allow_skip, allow_reset)
		self._header = header
		self._data = data
		self._data_callback = data_callback
		self._loading_header = loading_header
		self._multi = multi

		self._selected_keys: set[RowKey] = set()
		self._current_row_key: RowKey | None = None

		if self._data is None and self._data_callback is None:
			raise ValueError('Either data or data_callback must be provided')

	async def run(self) -> Result[ValueT]:
		assert TApp.app
		return await TApp.app.show(self)

	def action_cursor_down(self) -> None:
		table = self.query_one(DataTable)
		next_row = min(table.cursor_row + 1, len(table.rows) - 1)
		table.move_cursor(row=next_row, column=table.cursor_column or 0)

	def action_cursor_up(self) -> None:
		table = self.query_one(DataTable)
		prev_row = max(table.cursor_row - 1, 0)
		table.move_cursor(row=prev_row, column=table.cursor_column or 0)

	@override
	def compose(self) -> ComposeResult:
		yield from self._compose_header()

		with Center():
			with Vertical(classes='content-container'):
				if self._header:
					yield Static(self._header, classes='header', id='header')

				if self._loading_header:
					yield Static(self._loading_header, classes='header', id='loading-header')

				yield LoadingIndicator(id='loader')
				yield DataTable(id='data_table')

		yield Footer()

	def on_mount(self) -> None:
		self._display_header(True)
		data_table = self.query_one(DataTable)
		data_table.cell_padding = 2

		if self._data:
			self._put_data_to_table(data_table, self._data)
		else:
			self._load_data(data_table)

	@work
	async def _load_data(self, table: DataTable[ValueT]) -> None:
		assert self._data_callback is not None
		data = await self._data_callback()
		self._put_data_to_table(table, data)

	def _display_header(self, is_loading: bool) -> None:
		try:
			loading_header = self.query_one('#loading-header', Static)
			header = self.query_one('#header', Static)
			loading_header.display = is_loading
			header.display = not is_loading
		except Exception:
			pass

	def _put_data_to_table(self, table: DataTable[ValueT], data: list[ValueT]) -> None:
		if not data:
			_ = self.dismiss(Result(ResultType.Selection))
			return

		cols = list(data[0].table_data().keys())  # type: ignore[attr-defined]

		if self._multi:
			cols.insert(0, ' ')

		table.add_columns(*cols)

		for d in data:
			row_values = list(d.table_data().values())  # type: ignore[attr-defined]

			if self._multi:
				row_values.insert(0, ' ')

			table.add_row(*row_values, key=d)  # type: ignore[arg-type]

		table.cursor_type = 'row'
		table.display = True

		loader = self.query_one('#loader')
		loader.display = False
		self._display_header(False)
		table.focus()

	def action_toggle_selection(self) -> None:
		if not self._multi:
			return

		if not self._current_row_key:
			return

		table = self.query_one(DataTable)
		cell_key = table.coordinate_to_cell_key(table.cursor_coordinate)

		if self._current_row_key in self._selected_keys:
			self._selected_keys.remove(self._current_row_key)
			table.update_cell(self._current_row_key, cell_key.column_key, ' ')
		else:
			self._selected_keys.add(self._current_row_key)
			table.update_cell(self._current_row_key, cell_key.column_key, 'X')

	def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
		self._current_row_key = event.row_key

	def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
		if self._multi:
			if len(self._selected_keys) == 0:
				_ = self.dismiss(
					Result[ValueT](
						ResultType.Selection,
						_data=[event.row_key.value],  # type: ignore[list-item]
					)
				)
			else:
				_ = self.dismiss(
					Result(
						ResultType.Selection,
						_data=[row_key.value for row_key in self._selected_keys],  # type: ignore[misc]
					)
				)
		else:
			_ = self.dismiss(
				Result[ValueT](
					ResultType.Selection,
					_data=event.row_key.value,  # type: ignore[arg-type]
				)
			)


class _AppInstance(App[ValueT]):
	BINDINGS: ClassVar = [
		Binding('ctrl+h', 'trigger_help', 'Show/Hide help', show=True),
	]

	CSS = """
	.app-header {
		dock: top;
		height: auto;
		width: 100%;
		content-align: center middle;
		background: #1793D1;
		color: black;
		text-style: bold;
	}

	Footer {
		dock: bottom;
		background: #184956;
		color: white;
		height: 1;
	}

	.footer-key--key {
		background: black;
		color: white;
	}

	.footer-key--description {
		background: black;
		color: white;
	}

	FooterKey.-command-palette {
		background: black;
		border-left: vkey ansi_black;
	}
	"""

	def __init__(self, main: Any) -> None:
		super().__init__(ansi_color=True)
		self._main = main

	def action_trigger_help(self) -> None:
		from textual.widgets import HelpPanel

		if self.screen.query('HelpPanel'):
			_ = self.screen.query('HelpPanel').remove()
		else:
			_ = self.screen.mount(HelpPanel())

	def on_mount(self) -> None:
		self._run_worker()

	@work
	async def _run_worker(self) -> None:
		try:
			await self._main._run()
		except WorkerCancelled:
			debug('Worker was cancelled')
		except Exception as err:
			debug(f'Error while running main app: {err}')
			# this will terminate the textual app and return the exception
			self.exit(err)  # type: ignore[arg-type]

	@work
	async def _show_async(self, screen: Screen[Result[ValueT]]) -> Result[ValueT]:
		return await self.push_screen_wait(screen)

	async def show(self, screen: Screen[Result[ValueT]]) -> Result[ValueT]:
		return await self._show_async(screen).wait()


class TApp:
	app: _AppInstance[Any] | None = None

	def __init__(self) -> None:
		self._main = None
		self._global_header: str | None = None

	@property
	def global_header(self) -> str | None:
		return self._global_header

	@global_header.setter
	def global_header(self, value: str | None) -> None:
		self._global_header = value

	def run(self, main: Any) -> Result[ValueT]:
		TApp.app = _AppInstance(main)
		result: Result[ValueT] | Exception | None = TApp.app.run()

		if isinstance(result, Exception):
			raise result

		if result is None:
			raise ValueError('No result returned')

		return result

	def exit(self, result: Result[ValueT]) -> None:
		assert TApp.app
		TApp.app.exit(result)
		return


tui = TApp()
