from typing import List

from archinstall.profiles.profiles import Profile, ProfileType


class LighttpdProfile(Profile):
	def __init__(self):
		super().__init__(
			'Lighttpd',
			ProfileType.ServerType
		)

	@property
	def packages(self) -> List[str]:
		return ['lighttpd']

	@property
	def services(self) -> List[str]:
		return ['lighttpd']