from pathlib import Path

from archinstall.lib.menu.helpers import Input
from archinstall.lib.translationhandler import tr
from archinstall.tui.curses_menu import EditMenu
from archinstall.tui.result import ResultType
from archinstall.tui.types import Alignment

from ..models.users import Password
from ..output import FormattedOutput


def get_password(
	header: str | None = None,
	allow_skip: bool = False,
	preset: str | None = None,
	skip_confirmation: bool = False,
) -> Password | None:
	failure: str | None = None

	while True:
		user_hdr = None
		if failure is not None:
			user_hdr = f'{header}\n{failure}\n'
		elif header is not None:
			user_hdr = header

		result = Input(
			header=user_hdr,
			allow_skip=allow_skip,
			default_value=preset,
			password=True,
		).show()

		if allow_skip:
			if not result.get_value():
				return None

		password = Password(plaintext=result.get_value())

		if skip_confirmation:
			return password

		if header is not None:
			confirmation_header = f'{header}{tr("Password")}: {password.hidden()}\n'
		else:
			confirmation_header = f'{tr("Password")}: {password.hidden()}\n'

		confirmation_header += '\n' + tr('Confirm password')

		result = Input(
			header=confirmation_header,
			allow_skip=False,
			password=True,
		).show()

		if password._plaintext == result.get_value():
			return password

		failure = tr('The confirmation password did not match, please try again')


def prompt_dir(
	text: str,
	header: str | None = None,
	validate: bool = True,
	must_exist: bool = True,
	allow_skip: bool = False,
	preset: str | None = None,
) -> Path | None:
	def validate_path(path: str | None) -> str | None:
		if path:
			dest_path = Path(path)

			if must_exist:
				if dest_path.exists() and dest_path.is_dir():
					return None
			else:
				return None

		return tr('Not a valid directory')

	if validate:
		validate_func = validate_path
	else:
		validate_func = None

	result = EditMenu(
		text,
		header=header,
		alignment=Alignment.CENTER,
		allow_skip=allow_skip,
		validator=validate_func,
		default_text=preset,
	).input()

	match result.type_:
		case ResultType.Skip:
			return None
		case ResultType.Selection:
			if not result.text():
				return None
			return Path(result.text())

	return None


def is_subpath(first: Path, second: Path) -> bool:
	"""
	Check if _first_ a subpath of _second_
	"""
	try:
		first.relative_to(second)
		return True
	except ValueError:
		return False


def format_cols(items: list[str], header: str | None = None) -> str:
	if header:
		text = f'{header}:\n'
	else:
		text = ''

	nr_items = len(items)
	if nr_items <= 4:
		col = 1
	elif nr_items <= 8:
		col = 2
	elif nr_items <= 12:
		col = 3
	else:
		col = 4

	text += FormattedOutput.as_columns(items, col)
	# remove whitespaces on each row
	text = '\n'.join([t.strip() for t in text.split('\n')])
	return text
