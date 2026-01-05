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

        target_y = option_list.region.y + index - option_list.scroll_offset.y
        self.app.cursor_position = Offset(option_list.region.x, target_y)

        out(f'INDEX: {index}')
        out(f'TARGET: {target_y}')


class FruitApp(App):
    CSS = """
    Screen {
        color: white;
    }

    * {
        scrollbar-size: 1 1;

        /* Use high contrast colors */
        scrollbar-color: white;
        scrollbar-background: black;
    }

    .app-header {
        dock: top;
        height: auto;
        width: 100%;
        content-align: center middle;
        background: blue;
        color: white;
        text-style: bold;
    }

    .header-text {
        text-align: center;
        width: 100%;
        height: auto;

        padding-top: 2;
        padding-bottom: 2;

        background: transparent;
    }

    .preview-header {
        text-align: center;
        color: white;
        text-style: bold;
        width: 100%;

        padding-bottom: 1;

        background: transparent;
    }

    .no-border {
        border: none;
    }

    Input {
        border: solid gray 50%;
        background: transparent;
        height: 3;
        color: white;
    }

    Input .input--cursor {
        color: white;
    }

    Input:focus {
        border: solid blue;
    }

    Footer {
        dock: bottom;
        width: 100%;
        background: transparent;
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

    def on_mount(self) -> None:
        self.push_screen(FruitScreen())


if __name__ == '__main__':
    app = FruitApp()
    app.run()
