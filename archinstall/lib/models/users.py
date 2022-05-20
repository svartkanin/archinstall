from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class User:
	username: str
	password: str
	sudo: bool

	@property
	def display(self) -> str:
		password = '*' * len(self.password)
		return f'{_("Username")}: {self.username:16} {_("Password")}: {password:16} sudo: {str(self.sudo)}'

	@classmethod
	def _parse(cls, config_users: List[Dict[str, str]]) -> List['User']:
		users = []

		for entry in config_users:
			username = entry.get('username', None)
			password = entry.get('!password', '')
			sudo = entry.get('sudo', False)

			if username is None:
				continue

			user = User(username, password, sudo)
			users.append(user)

		return users

	@classmethod
	def _parse_backwards_compatible(cls, config_users: Dict[str, Dict[str, str]], sudo: bool) -> List['User']:
		if len(config_users.keys()) > 0:
			username = list(config_users.keys())[0]
			password = config_users[username]['!password']

			if password:
				return [User(username, password, sudo)]

		return []

	@classmethod
	def parse_arguments(
		cls,
		config_users: Union[List[Dict[str, str]], Dict[str, str]],
		config_superusers: Union[List[Dict[str, str]], Dict[str, str]]
	) -> List['User']:
		users = []

		# backwards compability
		if isinstance(config_users, Dict):
			users += cls._parse_backwards_compatible(config_users, False)
		else:
			users += cls._parse(config_users)

		# backwards compability
		if isinstance(config_superusers, Dict):
			users += cls._parse_backwards_compatible(config_superusers, True)

		return users
