from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.geometry import Offset
from textual.widgets import OptionList
from textual.screen import Screen


def out(text):
    with open('out.txt', 'a') as f:
        f.write(text + '\n')


class FruitScreen(Screen):
    CSS = """
    .content-container {
        width: 1fr;
        height: 1fr;
        max-height: 100%;

        padding-top: 0;
        padding-bottom: 3;
        padding-left: 2;

        background: transparent;
    }

    .no-border {
        border: none;
    }

    .list-container {
        width: auto;
        height: auto;
        max-height: 100%;

        background: transparent;
    }

    OptionList {
        width: auto;
        height: auto;
        min-width: 15%;
        max-height: 1fr;

        background: transparent;
    }

    OptionList > .option-list--option-highlighted {
        background: blue;
        color: white;
        text-style: bold;
    }
    """

    def compose(self) -> None:
        self.app.console.show_cursor(True)

        with Vertical(classes='content-container'):
            option_list = OptionList(id='option_list_widget')

            option_list.classes = 'no-border'

            yield option_list

    def on_mount(self) -> None:
        self._update_options()

    def _update_options(self) -> None:
        option_list = self.query_one(OptionList)
        option_list.clear_options()
        option_list.add_options(['apple', 'banana', 'pear', 'cucumber', 'pineapple', 'broccoli', 'strawberry'])
        self._set_cursor()

    def on_option_list_selected(self) -> None:
        self.app.exit()

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        self._set_cursor()

    def _set_cursor(self):
        option_list = self.query_one(OptionList)
        index = option_list.highlighted

        out(f'HIGHTLIGHT: {index}')

        if index is None:
            return

        target_y = option_list.region.y + index + 1 - option_list.scroll_offset.y
        self.app.cursor_position = Offset(option_list.region.x, target_y)

        out(f'INDEX: {index}')
        out(f'TARGET: {target_y}')


class FruitApp(App):
    def on_mount(self) -> None:
        self.push_screen(FruitScreen())


if __name__ == '__main__':
    app = FruitApp()
    app.run()
