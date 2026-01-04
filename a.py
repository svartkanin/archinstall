from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.widgets import OptionList

def out(text):
	with open('out.txt', 'a') as f:
		f.write(text + '\n')


class FruitApp(App):
	def compose(self) -> ComposeResult:
		self.app.console.show_cursor(True)
		yield OptionList('apple', 'banana', 'pear')

	def on_mount(self) -> None:
		self.query_one(OptionList).highlighted = 2
		self._set_cursor()

	def on_option_list_selected(self) -> None:
		self.exit()

	def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
		self._set_cursor()

	def _set_cursor(self):
		option_list = self.query_one(OptionList)
		index = option_list.highlighted

		out(f'HIGHTLIGHT: {index}')

		if index is None:
			return

		target_y = option_list.region.y + index+1 - option_list.scroll_offset.y
		self.app.cursor_position = Offset(option_list.region.x, target_y)

		out(f'INDEX: {index}')
		out(f'TARGET: {target_y}')


if __name__ == '__main__':
	app = FruitApp()
	app.run()
