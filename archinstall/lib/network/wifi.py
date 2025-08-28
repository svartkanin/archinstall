import time
import re

from pprint import pformat

from archinstall.lib.exceptions import SysCallError
from archinstall.lib.general import SysCommand
from archinstall.lib.models.network import WifiNetwork, WifiConfiguredNetwork
from archinstall.lib.output import FormattedOutput
from archinstall.lib.translationhandler import tr
from archinstall.tui.curses_menu import SelectMenu, Tui
from archinstall.tui.menu_item import MenuItem, MenuItemGroup
from archinstall.tui.result import ResultType
from archinstall.tui.types import Alignment, Orientation, FrameProperties
from archinstall.lib.menu.menu_helper import MenuHelper
from archinstall.lib.output import info, debug, error

from textual.app import App, ComposeResult
from textual.containers import Vertical, Center
from textual.widgets import Input, Button, Label
from textual.binding import Binding


class PasswordInputWidget(App):
	CSS = """
	Screen {
		align: center middle;
	}

	Vertical {
		width: 60;
		height: 10;
		border: solid $primary;
		background: $surface;
	}

	Label {
		text-align: center;
		margin: 1 0;
	}

	Input {
		margin: 1 2;
	}

	Button {
		margin: 1 2;
		width: 100%;
	}
	"""

	BINDINGS = [
		Binding("escape", "quit", "Quit"),
	]

	def __init__(self, ssid: str):
		super().__init__()
		self.ssid = ssid
		self.password: str = ""
		self.submitted = False

	def compose(self) -> ComposeResult:
		with Center():
			with Vertical():
				cjk = '你好世界'
				yield Label(f"Enter  {cjk}  password for: {self.ssid}")
				yield Input(placeholder="Password", password=True, id="password_input")
				yield Button("Connect", id="connect_btn")

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "connect_btn":
			self.action_submit()

	def action_submit(self) -> None:
		password_input = self.query_one("#password_input", Input)
		self.password = password_input.value
		self.submitted = True
		self.exit(self.password)

	def action_quit(self) -> None:
		self.exit("")


class WifiHandler:
	def __init__(self):
		pass

	def start_setup(self) -> bool:
		with Tui():
			prompt = tr('No network connection found') + '\n\n'
			prompt += tr('Would you like to connect to a Wifi?') + '\n'

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
						return False
				case ResultType.Skip:
					return False

		interface = self._get_interface()

		if not interface:
			info('No wifi interface found')
			return False

		self._scan_wifi_networks()
		wifi_networks = self._get_scan_results()
		selected_network = self._select_wifi_network(wifi_networks)

		if not selected_network:
			return False

		return self._connect_network(interface, selected_network)

	def _get_password_for_network(self, ssid: str) -> str:
		"""Use the Textual password input widget to get password from user"""
		password_widget = PasswordInputWidget(ssid)
		password = password_widget.run()
		return password if password else ""

	def _connect_network(self, interface: str, selected_network: WifiNetwork) -> bool:
		list_networks = SysCommand('wpa_cli list_networks').decode()
		config_networks = WifiConfiguredNetwork.from_wpa(list_networks)

		network_id: int | None = None

		# we'll try to find an existing network that has
		# not been configured yet this is to avoid creating
		# multiple orphan networks when # running archinstall multiple times
		for network in config_networks:
			if not network.ssid and 'DISABLED' in network.flags:
				network_id = int(network.network_id)
				break

		if network_id is None:
			try:
				debug('Create new wpa network')

				output = SysCommand(f'wpa_cli -i {interface} add_network').decode()
				network_id = int(output)
			except Exception as e:
				error(f'Failed to create new network: {e}')
				return False

		debug(f'wpa netowrk ID: {network_id}')

		password = self._get_password_for_network(selected_network.ssid)
		if not password:
			info("No password provided, aborting connection")
			return False

		# Configure the network with SSID and password
		try:
			SysCommand(f'wpa_cli -i {interface} set_network {network_id} ssid "{selected_network.ssid}"')
			SysCommand(f'wpa_cli -i {interface} set_network {network_id} psk "{password}"')
			SysCommand(f'wpa_cli -i {interface} select_network {network_id}')
			SysCommand(f'wpa_cli -i {interface} save_config')
			info(f"Successfully configured network {selected_network.ssid}")
			return True
		except Exception as e:
			error(f'Failed to configure network: {e}')
			return False

	def _get_interface(self) -> str | None:
		interface = SysCommand('wpa_cli interface_list').decode()
		debug(f'Wifi interface output: {interface}')

		if interface.startswith('Selected interface'):
			# Output: Selected interface 'wlan0'
			pattern = r"'(.+)'"
			match = re.search(pattern, interface)

			if match:
				interface_name = match.group(1)
				return interface_name

		return None

	def _scan_wifi_networks(self, wait: int = 5) -> None:
		Tui.print(tr('Scanning Wifi networks...'), clear_screen=True)
		SysCommand('wpa_cli scan')
		time.sleep(wait)

	def _get_scan_results(self) -> list[WifiNetwork]:
		try:
			results = SysCommand('wpa_cli scan_results').decode()

			from archinstall.lib.output import debug
			from pprint import pformat
			debug(pformat(results))

			networks = WifiNetwork.from_wpa(results)
			return networks
		except SysCallError as err:
			Tui.print('Unable to retrieve wifi results')
			raise err

	def _select_wifi_network(self, wifi_networks: list[WifiNetwork]) -> WifiNetwork | None:
		if not wifi_networks:
			Tui.print(tr('No WiFi networks found'))
			return None

		group = MenuHelper(wifi_networks).create_menu_group()

		with Tui():
			result = SelectMenu[WifiNetwork | None](
				group,
				header=tr('Select a WiFi network to connect to') + '\n',
				alignment=Alignment.CENTER,
				allow_skip=True,
			).run()

			match result.type_:
				case ResultType.Selection:
					return result.item().value
				case ResultType.Skip:
					return None

		return None


wifi_handler = WifiHandler()
