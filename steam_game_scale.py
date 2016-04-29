import requests
import json
import tkinter as tk
import tkinter.ttk as ttk
import sys
import traceback
import pprint

pp = pprint.PrettyPrinter(indent=2)

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

black='#000000'
dark='#224477'
medium='#4488DD'
light='#66AAFF'
silver='#C0C0C0'
white='#FFFFFF'
red='#FF0000'
green='#00FF00'
blue='#0000FF'

mammoth=140
fat=80
bigboned=64
skinny=24

def pack_space(foo,bar=None):
  foo.spacers.append(tk.Label(foo,width=100,bg=dark,fg=dark,textvariable=foo.blanktext))
  foo.spacers[-1].pack(fill='X')

def grid_space(foo,bar=0):
  foo.spacers.append(tk.Label(foo,width=100,bg=dark,fg=dark,textvariable=foo.blanktext))
  foo.spacers[-1].grid(column=0,row=bar)

space=grid_space

def pack_label(foo,text=None,bar=None):
  ret=tk.Label(foo,textvariable=text)
  ret.pack()
  return ret

def grid_label(foo,text=None,bar=0):
  ret=tk.Label(foo,textvariable=text)
  ret.grid(column=0,row=bar)
  return ret

label=grid_label

def pack_entry(foo,bar=None):
  ret=tk.Entry(foo)
  ret.pack()
  return ret

def grid_entry(foo,bar=0):
  ret=tk.Entry(foo)
  ret.grid(column=0,row=bar)
  return ret

entry=grid_entry

def pack_button(foo,bar=None):
  ret=tk.Button(foo)
  ret.pack()
  return ret

def grid_button(foo,bar=0):
  ret=tk.Button(foo)
  ret.grid(column=0,row=bar)
  return ret

button=grid_button

def pack_combobox(foo,bar=None):
  ret=ttk.Combobox(foo)
  ret.pack()
  return ret

def grid_combobox(foo,bar=0):
  ret=ttk.Combobox(foo)
  ret.grid(column=0,row=bar)
  return ret

combobox=grid_combobox

class steam_game_scale(tk.Tk):
  def __init__(self,parent):
    tk.Tk.__init__(self,parent)
    self.parent=parent
    self.blanktext=tk.StringVar(value='blank')
    self.initialize()
    
  def steam_api_call(self, api, method, parameters, version='v0001'):
    uri='/'.join([api_host,api,method,version])
    params_list=[parameter+'='+parameters[parameter] for parameter in parameters.keys()]
    key_string='key={}'.format(self.steam_api_key)
    format_string='format=json'
    total_params=params_list.append(key_string)
    total_params=params_list.append(format_string)
    params='&'.join(params_list)
    #pp.pprint(uri+'/?'+params)
    r=requests.get(uri+'/?'+params)
    ret=json.loads(r.text)
    #pp.pprint(ret)
    return ret
  
  def resolve_vanity_url(self,vanity_url,version='v0001'):
    response=self.steam_api_call('ISteamUser','ResolveVanityURL',{'vanityurl':vanity_url}, version)['response']
    if response['success'] == 1:
      return response['steamid']
    
  def get_fun_games(self,steamid,threshold=60,version='v0001'):
    response=self.steam_api_call('IPlayerService','GetOwnedGames',{'steamid':steamid,'include_appinfo':'1'},version)['response']
    if response['game_count'] > 0:
      return [app['name'] for app in response['games'] if int(app['playtime_forever']) > threshold]
    
  def get_player_summaries(self,steamids,version='v0002'):
    response=self.steam_api_call('ISteamUser','GetPlayerSummaries',{'steamids':steamids},version)
    return response
  
  def get_friends_list(self,relationship='all',version='v0001'):
    response=self.steam_api_call('ISteamUser','GetFriendList',{'steamid':self.steamid,'relationship':relationship},version)['friendslist']['friends']
    return self.get_player_summaries(','.join([friend['steamid'] for friend in response]))['response']['players']

  def initial_input_state(self):
    self.status_header_text.set('Please enter a valid SteamID and Steam API Key')
    self.status_header_label.configure(width=fat,bg=medium,fg=silver)
    self.steamid_entry_label_text.set('SteamID')
    self.steamid_entry_label.configure(width=fat,bg=medium,fg=silver)
    self.steamid_entry.configure(width=skinny,fg=light,bg=silver,justify='center')
    self.steam_api_key_entry_label_text.set('Steam API Key')
    self.steam_api_key_entry_label.configure(width=fat,bg=medium,justify='center')
    self.steam_api_key_entry.configure(width=fat,fg=light,bg=silver,justify='center')
    self.query_friends_button.configure(text='Query Friends List', command=self.query_friends_button_click,fg=medium,bg=silver)
    self.style.configure('Steam.TCombobox',background=[('pressed',silver)],foreground=[('pressed',light)])
    self.friends_combobox.configure(style='Steam.TCombobox',state='disabled',width=fat,values=[])
    self.friends_combobox.set('')
    self.friend_balance_button.configure(text='Calculate Balances',state='disabled',command=self.friend_balance_button_click,fg=medium,bg=silver)
    self.friends_persona_text.set('No Friend Selected')
    self.friend_persona_header.configure(width=bigboned,bg=light,fg=dark)
    self.friends_realname_text.set('')
    self.friend_realname_header.configure(width=bigboned,bg=light,fg=dark)
    self.friends_steamid_text.set('')
    self.friend_steamid_header.configure(width=bigboned,bg=light,fg=dark)
    self.threshold_minutes_label_a_text.set('Game Intersection Playtime Threshold A (minutes, default 60)')
    self.threshold_minutes_a = 60
    self.threshold_minutes_label_a.configure(width=fat,bg=medium,fg=silver)
    self.threshold_minutes_entry_a.configure(width=skinny,fg=light,bg=silver,justify='center')
    self.threshold_minutes_label_b_text.set('Game Intersection Playtime Threshold B (minutes, default 60)')
    self.threshold_minutes_b = 60
    self.threshold_minutes_label_b.configure(width=fat,bg=medium,fg=silver)
    self.threshold_minutes_entry_b.configure(width=skinny,fg=light,bg=silver,justify='center')
    self.game_intersections_label_text.set('Game Intersections Within Thresholds')
    self.game_intersections_frame.grid(column=0,row=200)
    self.game_intersections_listbox.configure(yscrollcommand=self.game_intersections_scrollbar.set)
    self.game_intersections_listbox.grid(column=0,row=200)
    self.game_intersections_scrollbar.configure(command=self.game_intersections_listbox.yview)
    self.game_intersections_scrollbar.grid(column=1,row=200,sticky='ns')
    self.steam_api_key=0
    self.steamid=0
    while self.game_intersections_listbox.size() > 0:
      self.game_intersections_listbox.delete(0)
    self.friends_list=[]
    self.pretty_friends_list=[]
    self.friend_personanames=[]
    self.selected_friend_persona=''
  
  def initialize(self):
    self.grid()
    self.resizable(False,False)
    self.spacers=[]
    self.style = ttk.Style()
    
    space(self,0)
    self.status_header_text = tk.StringVar()
    self.status_header_label = label(self,self.status_header_text,10)
    space(self,20)
    self.steamid_entry_label_text = tk.StringVar()
    self.steamid_entry_label = label(self,self.steamid_entry_label_text,30)
    self.steamid_entry = entry(self,40)
    space(self,50)
    self.steam_api_key_entry_label_text = tk.StringVar()
    self.steam_api_key_entry_label = label(self,self.steam_api_key_entry_label_text,60)
    self.steam_api_key_entry = entry(self,70)
    space(self,80)
    self.query_friends_button = button(self,90)
    space(self,100)
    self.friends_combobox = combobox(self,110)
    space(self,115)
    self.friend_balance_button = button(self,120)
    space(self,130)
    self.friends_persona_text = tk.StringVar()
    self.friend_persona_header = label(self,self.friends_persona_text,140)
    self.friends_realname_text = tk.StringVar()
    self.friend_realname_header = label(self,self.friends_realname_text,143)
    self.friends_steamid_text = tk.StringVar()
    self.friend_steamid_header = label(self,self.friends_steamid_text,147)
    space(self,150)
    self.threshold_minutes_label_a_text = tk.StringVar()
    self.threshold_minutes_label_a = label(self,self.threshold_minutes_label_a_text,160)
    self.threshold_minutes_entry_a = entry(self,170)
    self.threshold_minutes_label_b_text = tk.StringVar()
    self.threshold_minutes_label_b = label(self,self.threshold_minutes_label_b_text,180)
    self.threshold_minutes_entry_b = entry(self,190)
    space(self,193)
    self.game_intersections_label_text = tk.StringVar()
    self.game_intersections_frame = tk.Frame(self,height=20,width=mammoth)
    self.game_intersections_listbox = tk.Listbox(self.game_intersections_frame,height=20,width=fat)
    self.game_intersections_scrollbar = tk.Scrollbar(self.game_intersections_frame)
    space(self,205)
    
    self.initial_input_state()

  def valid_friends_state(self):
    self.status_header_label.configure(fg='silver')
    self.friend_balance_button.configure(state='active')
    while self.game_intersections_listbox.size() > 0:
      self.game_intersections_listbox.delete(0)
    
  def query_friends_button_click(self):
    self.steamid=self.steamid_entry.get()
    self.steam_api_key=self.steam_api_key_entry.get()
    try:
      self.friends_list=self.get_friends_list()
      self.pretty_friends_list=make_pretty_friends_list(self.friends_list)
      self.friend_personanames=sorted(get_personanames(self.friends_list))
      self.valid_friends_state()
      self.friends_combobox.configure(state='enabled',values=self.friend_personanames)
      self.friends_combobox.set('Please select a friend for balance sheet calculation')
    except Exception as inst:
      print(type(inst))
      print(inst.args)
      print(inst)
      traceback.print_exc()
      self.initial_input_state()
      self.status_header_label.configure(fg=red)
  def friend_balance_button_click(self):
    self.valid_friends_state()
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
      self.threshold_minutes_label_a.configure(fg=silver)
    else:
      self.threshold_minutes_a = 60
      self.threshold_minutes_label_a.configure(fg=silver)
      if self.threshold_minutes_entry_a.get() != '':
        self.threshold_minutes_label_a.configure(fg=red)
        self.threshold_minutes_a = 60
    if self.threshold_minutes_entry_b.get().isdigit() and int(self.threshold_minutes_entry_b.get()) > 0:
      self.threshold_minutes_b = int(self.threshold_minutes_entry_a.get())
      self.threshold_minutes_label_b.configure(fg=silver)
    else:
      self.threshold_minutes_b = 60
      self.threshold_minutes_label_b.configure(fg=silver)
      if self.threshold_minutes_entry_b.get() != '':
        self.threshold_minutes_label_b.configure(fg=red)
        self.threshold_minutes_b = 60
    games_a=self.get_fun_games(self.steamid,self.threshold_minutes_a)
    games_b=self.get_fun_games(selected_friend_steamid,self.threshold_minutes_b)
    games_intersection=[zgame for zgame in reversed(sorted(set(games_a).intersection(set(games_b))))]
    for game in games_intersection:
      self.game_intersections_listbox.insert(0, game)
    

if __name__ == '__main__':
  app = steam_game_scale(None)
  app.title('Steam Game Scale')
  app.configure(background=dark)
  app.mainloop()
