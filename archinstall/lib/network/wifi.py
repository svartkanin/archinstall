import time
from pprint import pprint

from archinstall.lib.exceptions import SysCallError
from archinstall.lib.general import SysCommand
from archinstall.lib.models.network import Wifi
from archinstall.lib.translationhandler import tr
from archinstall.tui.curses_menu import SelectMenu, Tui
from archinstall.tui.menu_item import MenuItem, MenuItemGroup
from archinstall.tui.result import ResultType
from archinstall.tui.types import Alignment, Orientation


class WifiHandler:
	def __init__(self):
		pass

	def start_setup(self) -> None:
		with Tui():
			prompt = tr('Would you like to connect to a Wifi?') + '\n'

			result = SelectMenu[bool](
				MenuItemGroup.yes_no(),
				header=prompt,
				alignment=Alignment.CENTER,
				columns=2,
				orientation=Orientation.HORIZONTAL,
			).run()

			match result.type_:
				case ResultType.Selection:
					if result.item() == MenuItem.no():
						return
				case ResultType.skip:
					return

		self.scan()
		wifis = self.list_scan()
		pprint(wifis)
		exit(0)

	def scan(self, wait: int = 5) -> None:
		Tui.print(tr('Scanning wifi...'), clear_screen=True)
		SysCommand('wpa_cli scan')
		time.sleep(wait)

	def list_scan(self) -> list[Wifi]:
		try:
			results = SysCommand('wpa_cli scan_results').decode()
			wifis = Wifi.from_results(results)
			return wifis
		except SysCallError as err:
			info('Unable to retrieve wifi results')
			raise err


wifi_handler = WifiHandler()
