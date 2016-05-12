import requests
import json
import sys
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)

api_host='http://api.steampowered.com'

class failed_request():
  def __init__(self,failure='',e=None):
    self.text=failure
    self.exception=e

class steam_api():
  # Constructor requires an api key positional parameter
  def __init__(self,api_key,steam_id_64=None):
    self.api_key=api_key
    self.steam_id_64=steam_id_64

  # Can reset the api key; can set a steam_id_64 as the default steamid for api calls that use one
  def set_steam_id_64(self,steam_id_64):
    self.steam_id_64=steam_id_64
  def set_api_key(self,api_key):
    self.api_key=api_key

  # Basic api call using the api key set when constructing the class
  def steam_api_call(self, api, method, parameters, version='v0001'):
    uri='/'.join([api_host,api,method,version])
    params_list=[parameter+'='+parameters[parameter] for parameter in parameters.keys()]
    key_string='key={}'.format(self.api_key)
    format_string='format=json'
    total_params=params_list.append(key_string)
    total_params=params_list.append(format_string)
    params='&'.join(params_list)
    try:
      r=requests.get(uri+'/?'+params)
    except Exception as e:
      r=failed_request(e.__class__.__name__,e)
    try:
      ret=json.loads(r.text)
    except JSONDecodeError as e:
      ret={}
    return ret
  
  # class methods that directly hit the steam api
  def resolve_vanity_url(self,vanity_url,version='v0001'):
    api='ISteamUser'
    method='ResolveVanityUrl'
    method_params={'vanityurl':vanity_url}
    return self.steam_api_call(api,method,method_params,version).get('response',{})
  def get_player_summaries(self,steamids,version='v0002'):
    api='ISteamUser'
    method='GetPlayerSummaries'
    method_params={'steamids':steamids}
    return self.steam_api_call(api,method,method_params,version).get('response',{})
  def get_friend_list(self,relationship='all',steamid=None,version='v0001'):
    if steamid is None:
      steamid=self.steam_id_64
    api='ISteamUser'
    method='GetFriendList'
    method_params={'steamid':steamid,'relationship':relationship}
    friendslist=self.steam_api_call(api,method,method_params,version).get('friendslist',{})
    return friendslist.get('friends',{})
  def get_owned_games(self,steamid=None,version='v0001'):
    if steamid is None:
      steamid=self.steam_id_64
    api='IPlayerService'
    method='GetOwnedGames'
    method_params={'steamid':steamid,'include_appinfo':'1'}
    return self.steam_api_call(api,method,method_params,version).get('response',{})
    
  # class methods that parse data returned by the steam api
  def vanity_url_steamid(self,vanity_url):
    response=self.resolve_vanity_url(vanity_url)
    if 'success' in response.keys() and response['success'] == 1:
      return response['steamid']
    else:
      return None
  def friends_steamids(self,steamid=None):
    if steamid is None:
      steamid=self.steam_id_64
    return [friend['steamid'] for friend in self.get_friend_list(steamid=steamid)]
  def friends_summaries(self,steamid=None):
    if steamid is None:
      steamid=self.steam_id_64
    return self.get_player_summaries(','.join(self.friends_steamids(steamid))).get('players',[])
  def friends_personanames(self,steamid=None):
    if steamid is None:
      steamid=self.steam_id_64
    personanames=[]
    players=self.friends_summaries(steamid)
    for player in players:
      personaname=player['personaname'] if 'personaname' in player.keys() else 'API failure retrieving personaname'
      personanames.append(personaname)
    return personanames
  def friends_dicts(self,steamid=None):
    if steamid is None:
      steamid=self.steam_id_64
    personanames={}
    steamids={}
    players=self.friends_summaries(steamid)
    for player in players:
      if 'personaname' in player.keys():
        personanames[player['personaname']]=player
      if 'steamid' in player.keys():
        steamids[player['steamid']]=player
    return {'personanames' : personanames, 'steamids' : steamids }
  def player_games(self,steamid=None):
    if steamid is None:
      steamid=self.steam_id_64
    return self.get_owned_games(steamid).get('games',[])
  def games_list(self,steamid=None,playtime=0):
    if steamid is None:
      steamid=self.steam_id_64
    return [ app['name'] for app in self.player_games(steamid) if int(app['playtime_forever']) > playtime ]
  def games_info(self,steamid=None,playtime=0):
    if steamid is None:
      steamid=self.steam_id_64
    return [ app for app in self.player_games(steamid) if int(app['playtime_forever']) > playtime ]

  # Make sure this all seems to be working as intended
  def test(self,steamid=None):
    if steamid is None:
      steamid=self.steam_id_64
    some_badgers_steamid = self.vanity_url_steamid('badger32d')
    badger_friend_steamids = self.friends_steamids(some_badgers_steamid)
    pp.pprint("Printing badger's friends' steamids:")
    pp.pprint(badger_friend_steamids)
    badger_friend_personanames = self.friends_personanames(some_badgers_steamid)
    pp.pprint("Printing badger's friends' personanames:")
    pp.pprint(badger_friend_personanames)
    badger_friend_details = self.friends_dicts(some_badgers_steamid)
    pp.pprint("Printing badger's friends' details by personaname:")
    for personaname in badger_friend_personanames:
      pp.pprint("  Data for {0}".format(personaname))
      pp.pprint(badger_friend_details.get('personanames',{}).get(personaname,{}))
    pp.pprint("Printing badger's friends' details by steamid:")
    for steamid in badger_friend_steamids:
      pp.pprint("  Data for {0}".format(steamid))
      pp.pprint(badger_friend_details.get('steamids',{}).get(steamid,{}))
    pp.pprint("Printing badgers owned games:")
    pp.pprint(self.games_list(some_badgers_steamid))
    pp.pprint("Printing details about the games the badger played for more than 3 hours:")
    pp.pprint(self.games_info(some_badgers_steamid,60*3))

class steam_game():
  def __init__(self,steam_game_info):
    img_url_template='http://media.steampowered.com/steamcommunity/public/images/apps/{0}/{1}.jpg'
    if 'appid' in steam_game_info.keys():
      self.appid = steam_game_info['appid'] if 'appid' in steam_game_info.keys() else -1
      if 'img_icon_url' in steam_game_info.keys():
        self.img_icon_url = img_url_template.format(self.appid,steam_game_info['img_icon_url'])
      else:
        self.img_icon_url = None
      if 'img_logo_url' in steam_game_info.keys():
        self.img_logo_url = img_url_template.format(self.appid,steam_game_info['img_logo_url'])
      else:
        self.img_logo_url = None
    else:
      self.appid = -1
    self.name = steam_game_info.get('name','Unknown')
    self.playtime_forever = steam_game_info.get('playtime_forever',0)
  
class steam_player():
  def __init__(self,steam_api_instance,playtime=0,steam_id_64=None,recurse=False):
    if steam_id_64 is None:
      steam_id_64=steam_api_instance.steam_id_64
    self.steam_id_64=steam_id_64
    self.steam_api_instance=steam_api_instance
    self.player_data = self.steam_api_instance.get_player_summaries(self.steam_id_64).get('players',[{}])[0]
    self.personaname = self.player_data['personaname'] if 'personaname' in self.player_data.keys() else 'Unknown'
    self.realname = self.player_data['realname'] if 'realname' in self.player_data.keys() else 'Unknown'
    self.avatar_url = self.player_data['avatar'] if 'avatar' in self.player_data.keys() else None
    self.steam_games=[]
    self.load_steam_games(playtime)
    self.steam_friends=[]
    if recurse:
      self.load_steam_friends(playtime)
    pass
  def load_steam_games(self,playtime=0):
    if self.steam_id_64 is not None:
      self.steam_games=[ steam_game(steam_game_info) for steam_game_info in self.steam_api_instance.games_info(self.steam_id_64,playtime) ]
  def load_steam_friends(self,playtime=0):
    self.steam_friends = [ steam_player(self.steam_api_instance,playtime,steamid) for steamid in self.steam_api_instance.friends_steamids(self.steam_id_64) ]
  def filter_games(self,playtime=0):
    return [ game for game in self.steam_games if game.playtime_forever > playtime ]

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
  steam_api_instance.set_steam_id_64(steam_api_instance.vanity_url_steamid('badger32d'))
  # Test the api class
  # steam_api_instance.test()

  # Test the player and game classes that use the api class to load data
  steam_player_instance = steam_player(steam_api_instance=steam_api_instance,recurse=True)
  pp.pprint("Player {} steam games:".format(steam_player_instance.personaname))
  pp.pprint( [ game.name for game in steam_player_instance.steam_games ] )
  for friend_instance in steam_player_instance.steam_friends:
    pp.pprint("Player {} steam games:".format(friend_instance.personaname))
    pp.pprint( [ game.name for game in friend_instance.steam_games ] )
