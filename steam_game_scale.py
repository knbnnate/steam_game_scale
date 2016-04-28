import requests
import json
import tkinter as tk
import tkinter.ttk as ttk
import sys

api_host='http://api.steampowered.com'

def make_pretty_friends_list(friends_list):
  pl = []
  for friend in friends_list:
    personaname=friend['personaname'] if 'personaname' in friend.keys() else 'API failure retrieving personaname'
    steamid=friend['steamid'] if 'steamid' in friend.keys() else 'API failure retrieving steamid'
    realname=friend['realname'] if 'realname' in friend.keys() else 'Unknown'
    pl.append( { personaname : {'steamid' : steamid , 'realname' : realname } } )
  return pl

def get_personanames(friends_list):
  pn = []
  for friend in friends_list:
    personaname=friend['personaname'] if 'personaname' in friend.keys() else 'API failure retrieving personaname'
    pn.append( personaname )
  return pn

class steam_game_scale(tk.Tk):
  def __init__(self,parent):
    tk.Tk.__init__(self,parent)
    self.parent=parent
    self.initialize()
  def initialize(self):
    self.grid()

    self.spacers=[]
    
    self.spacers.append(tk.Label(self,width=100,bg='#224477',fg='#224477',textvariable=tk.StringVar(value='blank')))
    self.spacers[-1].grid(column=0,row=0)

    self.status_header_text = tk.StringVar(value='Please enter a valid SteamID and Steam API Key')

    self.status_header_label = tk.Label(self,width=64,textvariable=self.status_header_text,bg='#4488DD',fg='silver')
    self.status_header_label.grid(column=0,row=10)
    
    self.spacers.append(tk.Label(self,width=100,bg='#224477',fg='#224477',textvariable=tk.StringVar(value='blank')))
    self.spacers[-1].grid(column=0,row=20)
    
    self.steamid_entry_label_text = tk.StringVar(value='SteamID')
    
    self.steamid_entry_label = tk.Label(self,width=24,textvariable=self.steamid_entry_label_text,bg='#4488DD',fg='silver')
    self.steamid_entry_label.grid(column=0,row=30)
    
    self.steamid_entry = tk.Entry(self,width=24,fg='#66AAFF',bg='silver',justify='center')
    self.steamid_entry.grid(column=0,row=40)
    
    self.steam_api_key_entry_label_text = tk.StringVar(value='Steam API Key')
        
    self.spacers.append(tk.Label(self,width=100,bg='#224477',fg='#224477',textvariable=tk.StringVar(value='blank')))
    self.spacers[-1].grid(column=0,row=50)
    
    self.steam_api_key_entry_label = tk.Label(self,width=64,textvariable=self.steam_api_key_entry_label_text,bg='#4488DD',fg='silver')
    self.steam_api_key_entry_label.grid(column=0,row=60)
    
    self.steam_api_key_entry = tk.Entry(self,width=64,fg='#66AAFF',bg='silver',justify='center')
    self.steam_api_key_entry.grid(column=0,row=70)
    
    self.resizable(False,False)
                            
    self.spacers.append(tk.Label(self,width=100,bg='#224477',fg='#224477',textvariable=tk.StringVar(value='blank')))
    self.spacers[-1].grid(column=0,row=80)
    
    self.query_friends_button = tk.Button(self,text='Query Friends List', command=self.query_friends_button_click,fg='#4488DD',bg='silver')
    self.query_friends_button.grid(column=0,row=90)
        
    self.spacers.append(tk.Label(self,width=100,bg='#224477',fg='#224477',textvariable=tk.StringVar(value='blank')))
    self.spacers[-1].grid(column=0,row=100)
    
    self.style = ttk.Style()
    self.style.configure('Steam.TCombobox',background=[('pressed','silver')],foreground=[('pressed','#66AAFF')])
    
    self.friends_combobox = ttk.Combobox(self,style='Steam.TCombobox',state='disabled',width=40)
    self.friends_combobox.grid(column=0,row=110)
    
    self.spacers.append(tk.Label(self,width=100,bg='#224477',fg='#224477',textvariable=tk.StringVar(value='blank')))
    self.spacers[-1].grid(column=0,row=115)

    self.friend_balance_button = tk.Button(self,text='Calculate balances',state='disabled',command=self.friend_balance_button_click,fg='#4488DD',bg='silver')
    self.friend_balance_button.grid(column=0,row=120)
        
    self.spacers.append(tk.Label(self,width=100,bg='#224477',fg='#224477',textvariable=tk.StringVar(value='blank')))
    self.spacers[-1].grid(column=0,row=130)
    
    self.friends_persona_text = tk.StringVar(value='No Friend Selected')
    self.friend_persona_header = tk.Label(self,width=60,bg='#66AAFF',fg='#224477',textvariable=self.friends_persona_text)
    self.friend_persona_header.grid(column=0,row=140)
    
    self.friends_realname_text = tk.StringVar(value='')
    self.friend_realname_header = tk.Label(self,width=60,bg='#66AAFF',fg='#224477',textvariable=self.friends_realname_text)
    self.friend_realname_header.grid(column=0,row=143)
    
    self.friends_steamid_text = tk.StringVar(value='')
    self.friend_steamid_header = tk.Label(self,width=60,bg='#66AAFF',fg='#224477',textvariable=self.friends_steamid_text)
    self.friend_steamid_header.grid(column=0,row=147)
    
    self.spacers.append(tk.Label(self,width=100,bg='#224477',fg='#224477',textvariable=tk.StringVar(value='blank')))
    self.spacers[-1].grid(column=0,row=150)

    self.threshold_minutes_label_a_text=tk.StringVar(value='Game Intersection Playtime Threshold A (minutes, default 60)')
    self.threshold_minutes_a = 60
    self.threshold_minutes_label_a=tk.Label(self,width=60,textvariable=self.threshold_minutes_label_a_text,bg='#4488DD',fg='silver')
    self.threshold_minutes_label_a.grid(column=0,row=160)

    self.threshold_minutes_entry_a = tk.Entry(self,width=60,fg='#66AAFF',bg='silver',justify='center')
    self.threshold_minutes_entry_a.grid(column=0,row=170)
    
    self.threshold_minutes_label_b_text=tk.StringVar(value='Game Intersection Playtime Threshold B (minutes, default 60)')
    self.threshold_minutes_b = 60
    self.threshold_minutes_label_b=tk.Label(self,width=60,textvariable=self.threshold_minutes_label_b_text,bg='#4488DD',fg='silver')
    self.threshold_minutes_label_b.grid(column=0,row=180)

    self.threshold_minutes_entry_b = tk.Entry(self,width=60,fg='#66AAFF',bg='silver',justify='center')
    self.threshold_minutes_entry_b.grid(column=0,row=190)
    
    self.spacers.append(tk.Label(self,width=100,bg='#224477',fg='#224477',textvariable=tk.StringVar(value='blank')))
    self.spacers[-1].grid(column=0,row=193)
    
    self.game_intersections_label_text=tk.StringVar(value='Game Intersections Within Thresholds')
    self.threshold_minutes_label_b=tk.Label(self,width=40,textvariable=self.game_intersections_label_text,bg='#4488DD',fg='silver')
    self.threshold_minutes_label_b.grid(column=0,row=195)

    self.game_intersections_frame = tk.Frame(self,height=20,width=140)
    self.game_intersections_frame.grid(column=0,row=200)

    self.game_intersections_listbox = tk.Listbox(self.game_intersections_frame,height=20,width=80)
    self.game_intersections_listbox.grid(column=0,row=200)

    self.game_intersections_scrollbar = tk.Scrollbar(self.game_intersections_frame)
    self.game_intersections_scrollbar.grid(column=1,row=200,sticky='ns')

    self.game_intersections_listbox.configure(yscrollcommand=self.game_intersections_scrollbar.set)
    self.game_intersections_scrollbar.configure(command=self.game_intersections_listbox.yview)
    
    self.spacers.append(tk.Label(self,width=100,bg='#224477',fg='#224477',textvariable=tk.StringVar(value='blank')))
    self.spacers[-1].grid(column=0,row=205)
    

  def query_friends_button_click(self):
    self.steamid=self.steamid_entry.get()
    self.steam_api_key=self.steam_api_key_entry.get()
    # During runtime, define these methods with the provided steam API key
    def steam_api_call(api, method, parameters, version='v0001'):
      uri='/'.join([api_host,api,method,version])
      params_list=[parameter+'='+parameters[parameter] for parameter in parameters.keys()]
      key_string='key={}'.format(self.steam_api_key)
      format_string='format=json'
      total_params=params_list.append(key_string)
      total_params=params_list.append(format_string)
      params='&'.join(params_list)
      r=requests.get(uri+'/?'+params)
      return json.loads(r.text)
    def resolve_vanity_url(vanity_url,version='v0001'):
      response=steam_api_call('ISteamUser','ResolveVanityURL',{'vanityurl':vanity_url}, version)['response']
      if response['success'] == 1:
        return response['steamid']
    def get_fun_games(steamid,threshold=60,version='v0001'):
      response=steam_api_call('IPlayerService','GetOwnedGames',{'steamid':steamid,'include_appinfo':'1'},version)['response']
      if response['game_count'] > 0:
        return [app['name'] for app in response['games'] if int(app['playtime_forever']) > threshold]
    def get_player_summaries(steamids,version='v0002'):
      response=steam_api_call('ISteamUser','GetPlayerSummaries',{'steamids':steamids},version)
      return response
    def get_friends_list(steamid,relationship='all',version='v0001'):
      response=steam_api_call('ISteamUser','GetFriendList',{'steamid':steamid,'relationship':relationship},version)['friendslist']['friends']
      return get_player_summaries(','.join([friend['steamid'] for friend in response]))['response']['players']
    # And then use them to get a list of friends for comparing
    try:
      self.friends_list=get_friends_list(self.steamid)
      self.pretty_friends_list=make_pretty_friends_list(self.friends_list)
      self.friend_personanames=sorted(get_personanames(self.friends_list))
      self.friends_combobox.configure(state='enabled',values=self.friend_personanames)
      self.status_header_label.configure(fg='silver')
      self.friends_combobox.set('Please select a friend for balance sheet calculation')
      self.friend_balance_button.configure(state='active')
    except Exception as inst:
      print(type(inst))
      print(inst.args)
      print(inst)
      self.status_header_label.configure(fg='red')
      self.friends_combobox.configure(state='disabled',values=[])
      self.friends_combobox.set('')
      self.friend_balance_button.configure(state='disabled')
      self.friends_persona_text.set('No Friend Selected')
      self.selected_friend_persona=self.friends_combobox.get()
      self.friends_realname_text.set('')
      self.friends_steamid_text.set('')
      while self.game_intersections_listbox.size() > 0:
        self.game_intersections_listbox.delete(0)
  def friend_balance_button_click(self):
    while self.game_intersections_listbox.size() > 0:
      self.game_intersections_listbox.delete(0)
    # During runtime, define these methods with the provided steam API key
    def steam_api_call(api, method, parameters, version='v0001'):
      uri='/'.join([api_host,api,method,version])
      params_list=[parameter+'='+parameters[parameter] for parameter in parameters.keys()]
      key_string='key={}'.format(self.steam_api_key)
      format_string='format=json'
      total_params=params_list.append(key_string)
      total_params=params_list.append(format_string)
      params='&'.join(params_list)
      r=requests.get(uri+'/?'+params)
      return json.loads(r.text)
    def resolve_vanity_url(vanity_url,version='v0001'):
      response=steam_api_call('ISteamUser','ResolveVanityURL',{'vanityurl':vanity_url}, version)['response']
      if response['success'] == 1:
        return response['steamid']
    def get_fun_games(steamid,threshold=60,version='v0001'):
      response=steam_api_call('IPlayerService','GetOwnedGames',{'steamid':steamid,'include_appinfo':'1'},version)['response']
      if response['game_count'] > 0:
        return [app['name'] for app in response['games'] if int(app['playtime_forever']) > threshold]
    def get_player_summaries(steamids,version='v0002'):
      response=steam_api_call('ISteamUser','GetPlayerSummaries',{'steamids':steamids},version)
      return response
    def get_friends_list(steamid,relationship='all',version='v0001'):
      response=steam_api_call('ISteamUser','GetFriendList',{'steamid':steamid,'relationship':relationship},version)['friendslist']['friends']
      return get_player_summaries(','.join([friend['steamid'] for friend in response]))['response']['players']
    # And then use them to get a list of friends for comparing
    self.selected_friend_persona=self.friends_combobox.get()
    self.friends_persona_text.set('Steam Persona: {}'.format(self.selected_friend_persona))
    selected_friend_realname=''
    selected_friend_steamid=''
    for friend in self.friends_list:
      if friend['personaname'] == self.selected_friend_persona:
        selected_friend_realname=friend['realname'] if 'realname' in friend.keys() else 'Unknown'
        selected_friend_steamid=friend['steamid'] if 'steamid' in friend.keys() else 'Unknown'
    self.friends_realname_text.set('Real Name: {}'.format(selected_friend_realname))
    self.friends_steamid_text.set('Steam ID: {}'.format(selected_friend_steamid))
    if self.threshold_minutes_entry_a.get().isdigit() and int(self.threshold_minutes_entry_a.get()) > 0:
      self.threshold_minutes_a = int(self.threshold_minutes_entry_a.get())
    if self.threshold_minutes_entry_b.get().isdigit() and int(self.threshold_minutes_entry_b.get()) > 0:
      self.threshold_minutes_b = int(self.threshold_minutes_entry_b.get())
    games_a=get_fun_games(self.steamid,self.threshold_minutes_a)
    games_b=get_fun_games(selected_friend_steamid,self.threshold_minutes_b)
    games_intersection=[zgame for zgame in reversed(sorted(set(games_a).intersection(set(games_b))))]
    for game in games_intersection:
      self.game_intersections_listbox.insert(0, game)
    

if __name__ == '__main__':
  app = steam_game_scale(None)
  app.title('Steam Game Scale')
  app.configure(background='#224477')
  app.mainloop()
