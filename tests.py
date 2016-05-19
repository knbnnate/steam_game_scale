from api import steam_api
from game import steam_game
from player import steam_player
from steam_game_scale import params_input, steam_game_scale_tk
import sys
import os
import traceback

if __name__ == '__main__':
  params=params_input()
  steam_api_instance=None
  try:
    steam_api_instance=steam_api(params.api_key_arg)
    if params.steamid_provided:
      steam_api_instance.set_steam_id_64(params.steamid_arg)
    elif params.vanity_url_provided:
      params.steamid_arg=steam_api_instance.vanity_url_steamid(params.vanity_url_arg)
      steam_api_instance.set_steam_id_64(params.steamid_arg)
    else:
      print("No steamid and no vanity url provided; cannot proceed")
      sys.exit(1)
  except Exception as e:
    print("Error on steamid or vanity url; cannot proceed.")
    traceback.print_exc()
    sys.exit(1)

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
  do_steam_game_scale_tk_test=input('Run the gui app? (y/n, [y])')
  if do_steam_game_scale_tk_test.lower() != 'n':
    app=steam_game_scale_tk(params)
