from __future__ import annotations

from archinstall.lib.menu.helpers import Confirmation, SelectionMenu
from archinstall.lib.translationhandler import tr
from archinstall.tui.menu_item import MenuItem, MenuItemGroup
from archinstall.tui.ui.result import ResultType as UiResultType

from ..hardware import GfxDriver, SysInfo


def select_kernel(preset: list[str] = []) -> list[str]:
	"""
	Asks the user to select a kernel for system.

	:return: The string as a selected kernel
	:rtype: string
	"""
	kernels = ['linux', 'linux-lts', 'linux-zen', 'linux-hardened']
	default_kernel = 'linux'

	items = [MenuItem(k, value=k) for k in kernels]

	group = MenuItemGroup(items, sort_items=True)
	group.set_default_by_value(default_kernel)
	group.set_focus_by_value(default_kernel)
	group.set_selected_by_value(preset)

	result = SelectionMenu[str](
		group,
		header=tr('Select which kernel(s) to install'),
		allow_skip=True,
		allow_reset=True,
		multi=True,
	).show()

	match result.type_:
		case UiResultType.Skip:
			return preset
		case UiResultType.Reset:
			return []
		case UiResultType.Selection:
			return result.get_values()


def ask_for_bootloader(preset: Bootloader | None) -> Bootloader | None:
	# Systemd is UEFI only
	options = []
	hidden_options = []
	default = None
	header = tr('Select which bootloader to install')

	if arch_config_handler.args.skip_boot:
		default = Bootloader.NO_BOOTLOADER
	else:
		hidden_options += [Bootloader.NO_BOOTLOADER]

	if not SysInfo.has_uefi():
		options += [Bootloader.Grub, Bootloader.Limine]
		if not default:
			default = Bootloader.Grub
		header += '\n' + tr('UEFI is not detected and some options are disabled')
	else:
		options += [b for b in Bootloader if b not in hidden_options]
		if not default:
			default = Bootloader.Systemd

	items = [MenuItem(o.value, value=o) for o in options]
	group = MenuItemGroup(items)
	group.set_default_by_value(default)
	group.set_focus_by_value(preset)

	result = SelectionMenu[Bootloader](
		group,
		header=header,
		allow_skip=True,
	).show()

	match result.type_:
		case UiResultType.Skip:
			return preset
		case UiResultType.Selection:
			return result.get_value()
		case UiResultType.Reset:
			raise ValueError('Unhandled result type')


def ask_for_uki(preset: bool = True) -> bool:
	prompt = tr('Would you like to use unified kernel images?') + '\n'

	group = MenuItemGroup.yes_no()
	group.set_focus_by_value(preset)

	result = Confirmation[bool](
		group,
		header=prompt,
		allow_skip=True,
	).show()

	match result.type_:
		case UiResultType.Skip:
			return preset
		case UiResultType.Selection:
			return result.item() == MenuItem.yes()
		case UiResultType.Reset:
			raise ValueError('Unhandled result type')


def select_driver(options: list[GfxDriver] = [], preset: GfxDriver | None = None) -> GfxDriver | None:
	"""
	Some what convoluted function, whose job is simple.
	Select a graphics driver from a pre-defined set of popular options.

	(The template xorg is for beginner users, not advanced, and should
	there for appeal to the general public first and edge cases later)
	"""
	if not options:
		options = [driver for driver in GfxDriver]

	items = [MenuItem(o.value, value=o, preview_action=lambda x: x.value.packages_text()) for o in options]
	group = MenuItemGroup(items, sort_items=True)
	group.set_default_by_value(GfxDriver.AllOpenSource)

	if preset is not None:
		group.set_focus_by_value(preset)

	header = ''
	if SysInfo.has_amd_graphics():
		header += tr('For the best compatibility with your AMD hardware, you may want to use either the all open-source or AMD / ATI options.') + '\n'
	if SysInfo.has_intel_graphics():
		header += tr('For the best compatibility with your Intel hardware, you may want to use either the all open-source or Intel options.\n')
	if SysInfo.has_nvidia_graphics():
		header += tr('For the best compatibility with your Nvidia hardware, you may want to use the Nvidia proprietary driver.\n')

	result = SelectionMenu[GfxDriver](
		group,
		header=header,
		allow_skip=True,
		allow_reset=True,
		preview_orientation='right',
	).show()

	match result.type_:
		case UiResultType.Skip:
			return preset
		case UiResultType.Reset:
			return None
		case UiResultType.Selection:
			return result.get_value()


def ask_for_swap(preset: bool = True) -> bool:
	if preset:
		default_item = MenuItem.yes()
	else:
		default_item = MenuItem.no()

	prompt = tr('Would you like to use swap on zram?') + '\n'

	group = MenuItemGroup.yes_no()
	group.set_focus_by_value(default_item)

	result = Confirmation[bool](
		group,
		header=prompt,
		allow_skip=True,
	).show()

	match result.type_:
		case UiResultType.Skip:
			return preset
		case UiResultType.Selection:
			return result.item() == MenuItem.yes()
		case UiResultType.Reset:
			raise ValueError('Unhandled result type')
