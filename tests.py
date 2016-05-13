from api import steam_api
from game import steam_game
from player import steam_player
import sys

if __name__ == '__main__':
  api_key_arg=None
  steamid_arg=None
  for arg in sys.argv:
    if arg.startswith('--apikey='):
      api_key_arg=arg.partition('=')[2].partition('=')[0]
    if arg.startswith('--steamid='):
      steamid_arg=arg.partition('=')[2].partition('=')[0]
  if api_key_arg is None:
    api_key_arg=input('Steam API Key: ')
  steam_api_instance = steam_api(api_key_arg)
  if steamid_arg is None:
    # Maintainer's vanity_url
    steam_api_instance.set_steam_id_64(steam_api_instance.vanity_url_steamid('knbnnate'))
  # Test the api class
  else:
    steam_api_instance.set_steam_id_64(steamid_arg)
  steam_api_instance.test()

  # Test the player and game classes that use the api class to load data
  steam_player_instance = steam_player(steam_api_instance=steam_api_instance,recurse=True)
  # Game test is implicit in player test
  steam_player_instance.test()
