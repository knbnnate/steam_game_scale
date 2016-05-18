from api import steam_api
from game import steam_game
from player import steam_player
import sys
import os
from broken_tk_gui import tests as tk_gui_tests

if __name__ == '__main__':
################## Figure out an API key and a steam user to test with ##################
  steamid_provided=False
  vanity_url_provided=False
  api_key_provided=False
  # Can have files setting api_key_arg, steamid_arg, vanity_url_arg
  if os.path.isfile('api_key.py'):
    try:
      from api_key import api_key_arg
      api_key_provided=True
    except:
      print('api_key.py does not set an api_key_arg string')
  if os.path.isfile('vanity_url.py'):
    try:
      from vanity_url import vanity_url_arg
      vanity_url_provided=True
    except:
      print('vanity_url.py does not set a vanity_url_arg string')
  if not vanity_url_provided:
    if os.path.isfile('steamid.py'):
      try:
        from steamid import steamid_arg
        steamid_arg_provided=True
      except:
        print('steamid.py does not set a steamid_arg string')
  # Can override the files with command line args
  for arg in sys.argv:
    if arg.startswith('--vanityurl='):
      vanity_url_arg=arg.partition('=')[2]
      vanity_url_provided=True
    if arg.startswith('--apikey='):
      api_key_arg=arg.partition('=')[2]
      api_key_provided=True
    if arg.startswith('--steamid='):
      steamid_arg=arg.partition('=')[2]
      steamid_provided=True
  # If nothing provided in directory or on command line, prompt user in console
  if not steamid_provided and not vanity_url_provided:
    vanity_url_arg=input('Vanity URL (enter no text to input a steamid instead): ')
    if vanity_url_arg != '':
      vanity_url_provided=True
    else:
      steamid_arg=input('Steam ID: ')
      if steamid_arg != '':
        steamid_provided=True
  if not api_key_provided:
    api_key_arg=input('Steam API Key: ')
    if api_key_arg != '':
      api_key_provided=True
  if api_key_provided:
    steam_api_instance = steam_api(api_key_arg)
  else:
    print("Please provide a valid API key somehow or none of this will work")
    sys.exit(0)
  if not steamid_provided and not vanity_url_provided:
    # Maintainer's vanity_url, better than nothing
    steam_api_instance.set_steam_id_64(steam_api_instance.vanity_url_steamid('knbnnate'))
  elif steamid_provided:
    steam_api_instance.set_steam_id_64(steamid_arg)
  else:
    steam_api_instance.set_steam_id_64(steam_api_instance.vanity_url_steamid(vanity_url_arg))
################## That was fun, on to tests ##################

  do_api_test=input('Test the steam_api class? (y/n, [y]) ')
  if do_api_test.lower() != 'n':
    # Test the api class
    steam_api_instance.test()

  do_player_game_test=input('Test the steam_player and thus the steam_game class? (y/n, [y]) ')
  if do_player_game_test.lower() != 'n':
    print('Loading data from the Steam API for the steam_player test, please wait a moment...')
    player_game_exceptions=[]
    try:
      # Test the player and game classes that use the api class to load data
      steam_player_instance = steam_player(steam_api_instance=steam_api_instance,recurse=True)
      # Game test is implicit in player test
    except Exception as e:
      player_game_exceptions.append([e,'Failure loading steam_player object'])
      print('Failure loading steam_player object')
    try:
      steam_player_instance.test()
    except Exception as e:
      player_game_exceptions.append([e,'Failure running steam_player test method'])
      print('Failure running steam_player test method')
    if len(player_game_exceptions) == 0:
      print('SUCCESS testing steam_player class')
    elif len(player_game_exceptions) == 1:
      print('FAILURE testing steam_player class')
      for item in player_game_exceptions:
        print(item[1])
    else:
      print('FAILURES testing steam_player class')
      for item in player_game_exceptions:
        print(item[1])
  do_tk_gui_test=input('Test the tk_gui module? (y/n, [y]) ')
  if do_tk_gui_test.lower() != 'n':
    test=tk_gui_tests(steam_api_instance)
    test.run_tests()
