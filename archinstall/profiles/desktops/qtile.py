from typing import Optional, List, Any, TYPE_CHECKING

from archinstall.profiles.profiles import ProfileType, GreeterType
from archinstall.profiles.xorg import XorgProfile

if TYPE_CHECKING:
	_: Any


class QtileProfileV2(XorgProfile):
	def __init__(self):
		super().__init__('Qtile', ProfileType.WindowMgr, description='')

	@property
	def packages(self) -> List[str]:
		return [
			'qtile',
			'alacritty'
		]

	@property
	def default_greeter_type(self) -> Optional[GreeterType]:
		return GreeterType.Lightdm

	def preview_text(self) -> Optional[str]:
		text = str(_('Environment type: {}')).format(self.profile_type.value)
		return text + '\n' + self.packages_text()