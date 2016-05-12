from api import steam_api
from game import steam_game
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=2)
pp2 = pp
pp4 = PrettyPrinter(indent=4)
pp6 = PrettyPrinter(indent=6)

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
      self.steam_games=[ steam_game(steam_game_info, self.personaname, self.steam_id_64) for steam_game_info in self.steam_api_instance.games_info(self.steam_id_64,playtime) ]
  def load_steam_friends(self,playtime=0):
    self.steam_friends = [ steam_player(self.steam_api_instance,playtime,steamid) for steamid in self.steam_api_instance.friends_steamids(self.steam_id_64) ]
  def filter_games(self,playtime=0):
    return [ game for game in self.steam_games if game.playtime_forever > playtime ]
  def test(self):
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint(["### steam_player test ###","{}".format(self.personaname),"### steam_player test ###"])
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint(["{} realname: {}".format(self.personaname, self.realname)])
    pp4.pprint(["{} avatar_url: {}".format(self.personaname, self.avatar_url)])
    if len(self.steam_games) > 0:
      pp4.pprint(["{} games:".format(self.personaname)])
      for game in self.steam_games:
        pp6.pprint(['#',"Game from steam_games list:",'#'])
        game.test()
    else:
      pp.pprint(["{0} games not loaded yet, or {0} has no games".format(self.personaname)])
    if len(self.steam_friends) > 0:
      pp.pprint(["{} friends list test (1 friend):".format(self.personaname)])
      for friend in [self.steam_friends[0]]:
        pp.pprint(['#',"Friend from steam_friends list:",'#'])
        friend.test()
    else:
      pp.pprint(["{0} friends not loaded yet, or {0} has no friends".format(self.personaname)])
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint(["### end steam_player test ###","{}".format(self.personaname),"### end steam_player test ###"])
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint("#")
