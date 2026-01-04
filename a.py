from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.widgets import OptionList


class FruitApp(App):
	def compose(self) -> ComposeResult:
		yield OptionList('apple', 'banana', 'pear')

	def on_option_list_selected(self) -> None:
		self.exit()

	def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
		option_list = self.query_one(OptionList)
		index = option_list.highlighted

		if not index:
			return

		target_y = option_list.region.y + index - option_list.scroll_offset.y
		self.app.cursor_position = Offset(option_list.region.x, target_y)


if __name__ == '__main__':
	app = FruitApp()
	app.run()
