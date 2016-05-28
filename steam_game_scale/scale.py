from steam_game_scale.game import steam_game
from steam_game_scale.player import steam_player

class playtime_weights():
  def __init__(self,player_game_playtime=0,friend_game_playtime=0):
    self.player=player_game_playtime
    self.friend=friend_game_playtime
  def game_compare_friends(self,steam_game,steam_friends):
    matching_friends=[]
    for friend in steam_friends:
      for game in friend.steam_games:
        if game.name==steam_game.name and game.playtime_forever >= self.friend:
          matching_friends.append(friend)
    return matching_friends
  def friend_compare_games(self,steam_friend,steam_games):
    matching_games=[]
    for game in steam_games:
      for friend_game in steam_friend.steam_games:
        if game.name==friend_game.name:
          if game.playtime_forever > self.player and friend_game.playtime_forever > self.friend:
            matching_games.append([game,friend_game])
    return matching_games
    
