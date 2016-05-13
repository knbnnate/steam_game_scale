import requests
import json
import sys
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2)
pp2 = pp
pp4 = PrettyPrinter(indent=4)
pp6 = PrettyPrinter(indent=6)

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
  def steamid_personaname(self,steamid):
    response=self.get_player_summaries(steamid)
    players=response.get('players',[{}])
    player=players[0]
    return player.get('personaname','Unknown')
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
    test_personaname = self.steamid_personaname(steamid)
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint(["### steam_api test ###","{}".format(test_personaname),"### steam_api_test ###"])
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint("#")
    friend_steamids = self.friends_steamids(steamid)
    pp.pprint(["Printing {} friends' steamids:".format(test_personaname)])
    pp4.pprint([friend_steamids])
    friend_personanames = self.friends_personanames(steamid)
    pp.pprint(["Printing {} friends' personanames:".format(test_personaname)])
    pp4.pprint([friend_personanames])
    friend_details = self.friends_dicts(steamid)
    pp.pprint(["Printing {} friends' details by personaname:".format(test_personaname)])
    for personaname in friend_personanames:
      pp4.pprint(["  Data for {0}".format(personaname)])
      pp6.pprint([friend_details.get('personanames',{}).get(personaname,{})])
    pp.pprint(["Printing {} friends' details by steamid:".format(test_personaname)])
    for friend_steamid in friend_steamids:
      pp4.pprint(["  Data for {0}".format(friend_steamid)])
      pp6.pprint([friend_details.get('steamids',{}).get(friend_steamid,{})])
    pp.pprint(["Printing {} owned games:".format(test_personaname)])
    pp4.pprint([self.games_list(steamid)])
    pp.pprint(["Printing details about the games played by {} for more than 3 hours:".format(test_personaname)])
    pp4.pprint([self.games_info(steamid,60*3)])
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint(["### end steam_api test ###","{}".format(test_personaname),"### end steam_api_test ###"])
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint("#")
