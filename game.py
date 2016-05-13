from pprint import PrettyPrinter

pp = PrettyPrinter(indent=2)
pp2 = pp
pp4 = PrettyPrinter(indent=4)

class steam_game():
  def __init__(self,steam_game_info, owner_personaname='Unknown Game Owner', owner_steamid=-1):
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
    self.name = steam_game_info.get('name','Unknown Game Name')
    self.playtime_forever = steam_game_info.get('playtime_forever',0)
    self.owner_personaname = owner_personaname
    self.owner_steamid = owner_steamid
  def playtime_text(self):
    if self.playtime_forever is None or self.playtime_forever == 0:
      return 'Not played'
    minutes_rem=int(self.playtime_forever%60)
    hours_total=int(self.playtime_forever/60)
    hours_rem=int(hours_total%24)
    days=int(hours_total/24)
    if days > 0:
      return '{} days, {} hours {} minutes'.format(days,hours_rem,minutes_rem)
    elif hours_total > 0:
      return '{} hours, {} minutes'.format(hours_total,minutes_rem)
    else:
      return '{} minutes'.format(self.playtime_forever)
  def test(self):
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint(["### steam_game test ###","{}".format(self.name),"### steam_game test ###"])
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint("#")
    pp4.pprint(["{} appid: {}".format(self.name, self.appid)])
    pp4.pprint(["{} img_icon_url: {}".format(self.name, self.img_icon_url)])
    pp4.pprint(["{} img_logo_url: {}".format(self.name, self.img_logo_url)])
    pp4.pprint(["{} steamid of owner {}: {}".format(self.name, self.owner_personaname, self.owner_steamid)])
    pp4.pprint(["{} playtime by owner {}: {}".format(self.name, self.owner_personaname, self.playtime_forever)])
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint(["### end steam_game test ###","{}".format(self.name),"### end steam_game test ###"])
    pp.pprint("#")
    pp.pprint("#")
    pp.pprint("#")
