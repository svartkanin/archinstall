from typing import Optional, List

from profiles_v2.profiles_v2 import ProfileType
from profiles_v2.xorg import XorgProfileV2


class I3gapsProfileV2(XorgProfileV2):
	def __init__(self):
		super().__init__('i3-gaps', ProfileType.WindowMgr, description='')

	@classmethod
	def packages(cls) -> List[str]:
		return super().packages() + [
			'i3lock',
			'i3status',
			'i3blocks',
			'xterm',
			'lightdm-gtk-greeter',
			'lightdm',
			'dmenu',
			'i3-gaps'
		]

	@classmethod
	def services(cls) -> List[str]:
		return ['lightdm']

	def preview_text(self) -> Optional[str]:
		text = str(_('Environment type: {}')).format(self.profile_type.value)
		return text + '\n' + self.packages_text()
