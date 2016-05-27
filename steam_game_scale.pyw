import tkinter as tk               #
import tkinter.font as tkfont      #
tk.font=tkfont                     # Yay aliasing
from PIL import Image, ImageTk     # PIL(low) dependency
import sys                         #
import os                          #
from api import steam_api          # requests dependency
from url_images import url_image   # requests dependency
from player import steam_player    #
from game import steam_game        #
from scale import playtime_weights #
import traceback                   #
import yaml                        # PyYAML dependency
import webbrowser                  #

class steam_colors():
  def __init__(self):
    pass
  bg='#171a21'
  fg='#767676'
  sbg=fg
  sfg=bg

def print_toplevel(msg):
  popup=tk.Toplevel(None)
  popup.configure(bg=steam_colors.bg)
  img=ImageTk.PhotoImage(file='steam_game_scale.png')
  popup.tk.call('wm','iconphoto',popup._w,img)
  popup.title('MESSAGE')
  popup.option_add('*Background',steam_colors.bg)
  popup.option_add('*Foreground',steam_colors.fg)
  popup.option_add('*Selectbackground',steam_colors.fg)
  popup.option_add('*Selectforeground',steam_colors.bg)
  popup_label=tk.Label(popup,text=msg)
  popup_label.pack()
  popup_button=tk.Button(popup,text='OK',command=popup.destroy)
  popup_button.pack()
  popup.mainloop()

class params_input():
  def load_params(self):
    if not os.path.isfile(self.saved_filename):
      with open(self.saved_filename,'w') as yaml_stream:
        api_keys={}
        steamids={}
        vanity_urls={}
        yaml.dump({'api_keys':api_keys,'vanity_urls':vanity_urls,'steamids':steamids},yaml_stream)
    with open(self.saved_filename,'r') as yaml_stream:
      self.loaded_params=yaml.load(yaml_stream)
      self.loaded_api_keys=self.loaded_params.get('api_keys',{})
      self.loaded_steamids=self.loaded_params.get('steamids',{})
      self.loaded_vanity_urls=self.loaded_params.get('vanity_urls',{})
  def save_params(self):
    with open(self.saved_filename,'w') as yaml_stream:
      yaml.dump({'api_keys':self.loaded_api_keys,
                 'vanity_urls':self.loaded_vanity_urls,
                 'steamids':self.loaded_steamids},yaml_stream)
  def clean_vanity_url(self):
    if self.vanity_url_arg.endswith('/home'):
      self.vanity_url_arg=self.vanity_url_arg.rpartition('/')[0]
    if '/' in self.vanity_url_arg:
      self.vanity_url_arg=self.vanity_url_arg.rpartition('/')[2]
  def create_api_key_entry(self):
    name=self.params_dialog.api_key_input_name_entry.get()
    value=self.params_dialog.api_key_input_value_entry.get()
    if len(name) > 0 and len(value) > 0:
      self.loaded_api_keys[name]=value
      self.save_params()
      self.init_api_key_prompt_listbox()
      self.params_dialog.api_key_input_name_entry.delete(0,tk.END)
      self.params_dialog.api_key_input_value_entry.delete(0,tk.END)
  def delete_api_key_entry(self):
    for selection_index in self.params_dialog.api_key_prompt_listbox.curselection():
      selection_text=self.params_dialog.api_key_prompt_listbox.get(int(selection_index))
      selected_api_key=self.params_dialog.api_key_selection_map[selection_text]
      del(self.loaded_api_keys[selected_api_key])
      self.save_params()
      self.init_api_key_prompt_listbox()
  def lookup_vanity_url(self):
    selected_api_key=None
    steamid=None
    for selection_index in self.params_dialog.api_key_prompt_listbox.curselection():
      selection_text=self.params_dialog.api_key_prompt_listbox.get(int(selection_index))
      selected_api_key_name=self.params_dialog.api_key_selection_map[selection_text]
      selected_api_key=self.loaded_api_keys[selected_api_key_name]
    if selected_api_key is not None:
      try:
        temp_api_instance=steam_api(selected_api_key)
        vanity_url=self.params_dialog.vanity_url_input_value_entry.get()
        steamid=temp_api_instance.vanity_url_steamid(vanity_url)
      except:
        vanity_url=None
        print_toplevel('Failure looking up Custom URL - bad API key selection. Deleting selected key is suggested.')
    else:
      print_toplevel('Please select an API key to perform this lookup')
    if len(self.params_dialog.steamid_input_value_entry.get()) > 0:
      self.params_dialog.steamid_input_value_entry.delete(0,tk.END)
    if steamid is not None:
      self.params_dialog.steamid_input_value_entry.insert(0,steamid)
      if vanity_url is not None:
        self.loaded_vanity_urls[vanity_url]=steamid
        self.save_params()
  def create_steamid_entry(self):
    name=self.params_dialog.steamid_input_name_entry.get()
    value=self.params_dialog.steamid_input_value_entry.get()
    if len(name) > 0 and len(value) > 0:
      self.loaded_steamids[name]=value
      self.save_params()
      self.init_steamid_prompt_listbox()
      self.params_dialog.steamid_input_name_entry.delete(0,tk.END)
      self.params_dialog.steamid_input_value_entry.delete(0,tk.END)
  def delete_steamid_entry(self):
    for selection_index in self.params_dialog.steamid_prompt_listbox.curselection():
      selection_text=self.params_dialog.steamid_prompt_listbox.get(int(selection_index))
      selected_steamid_name=self.params_dialog.steamid_selection_map[selection_text]
      del(self.loaded_steamids[selected_steamid_name])
      self.save_params()
      self.init_steamid_prompt_listbox()
  def api_key_help_button(self):
    webbrowser.open('http://steamcommunity.com/dev/apikey')
  def vanity_url_help_button(self):
    webbrowser.open('http://steamcommunity.com/my/edit')
  def init_steamid_prompt_listbox(self):
    while self.params_dialog.steamid_prompt_listbox.size() > 0:
      self.params_dialog.steamid_prompt_listbox.delete(0)
    for steamid_name in sorted(set(self.loaded_steamids.keys())):
      self.params_dialog.steamid_prompt_listbox.insert(self.params_dialog.steamid_prompt_listbox.size(),
                                                       '{}: [{}]'.format(steamid_name,self.loaded_steamids[steamid_name]))
      self.params_dialog.steamid_selection_map['{}: [{}]'.format(steamid_name,self.loaded_steamids[steamid_name])]=steamid_name
    # Adjust listbox width since tkinter does not do it for you, ever
    if len(self.loaded_steamids.keys()) > 0:
      f = tk.font.Font(font=self.params_dialog.steamid_prompt_listbox.cget("font"))
      req_width=max([len('{}: [{}]'.format(steamid_name,self.loaded_steamids[steamid_name])) for steamid_name in self.loaded_steamids.keys()])
      self.params_dialog.steamid_prompt_listbox.configure(width=req_width)
  def init_api_key_prompt_listbox(self):
    while self.params_dialog.api_key_prompt_listbox.size() > 0:
      self.params_dialog.api_key_prompt_listbox.delete(0)
    for api_key_name in sorted(set(self.loaded_api_keys.keys())):
      self.params_dialog.api_key_prompt_listbox.insert(self.params_dialog.api_key_prompt_listbox.size(),
                                                       '{}: [{}]'.format(api_key_name,'*****************'))
      self.params_dialog.api_key_selection_map['{}: [{}]'.format(api_key_name,'*****************')]=api_key_name
    # Adjust listbox width since tkinter does not do it for you, ever
    if len(self.loaded_api_keys.keys()) > 0:
      f = tk.font.Font(font=self.params_dialog.api_key_prompt_listbox.cget("font"))
      req_width=max([len('{}: [{}]'.format(api_key_name,'*****************')) for api_key_name in self.loaded_api_keys.keys()])
      self.params_dialog.api_key_prompt_listbox.configure(width=req_width)
  def api_key_listbox_select(self,event):
    for selection_index in self.params_dialog.api_key_prompt_listbox.curselection():
      selection_text=self.params_dialog.api_key_prompt_listbox.get(int(selection_index))
      selected_api_key=self.params_dialog.api_key_selection_map[selection_text]
      self.api_key_arg=self.loaded_api_keys[selected_api_key]
      self.api_key_provided=True
  def steamid_listbox_select(self,event):
    for selection_index in self.params_dialog.steamid_prompt_listbox.curselection():
      selection_text=self.params_dialog.steamid_prompt_listbox.get(int(selection_index))
      selected_steamid=self.params_dialog.steamid_selection_map[selection_text]
      self.steamid_arg=self.loaded_steamids[selected_steamid]
      self.steamid_provided=True
      self.vanity_url_provided=False
  def start_app_button(self):
    if self.steamid_arg is not None and self.api_key_arg is not None:
      self.params_dialog.destroy()
    else:
      print_toplevel('Please select an API key and Steam ID to start the app')
  def __init__(self):
    self.saved_filename='saved_params.yaml'
    self.loaded_params={}
    self.loaded_api_keys={}
    self.loaded_vanity_urls={}
    self.load_params()
    self.steamid_arg=None
    self.api_key_arg=None
    self.vanity_url_arg=None
    self.steamid_provided=False
    self.api_key_provided=False
    self.vanity_url_provided=False
    self.params_dialog = tk.Tk(None)
    self.params_dialog.title('Initialization Information')
    img=ImageTk.PhotoImage(file='steam_game_scale.png')
    self.params_dialog.tk.call('wm','iconphoto',self.params_dialog._w,img)
    self.params_dialog.configure(bg=steam_colors.bg)
    self.params_dialog.option_add('*Background',steam_colors.bg)
    self.params_dialog.option_add('*Foreground',steam_colors.fg)
    self.params_dialog.option_add('*Font','courier')
    
    # Helper webbrowser buttons
    self.params_dialog.api_key_help_button=tk.Button(self.params_dialog,text='Help me find my API key',command=self.api_key_help_button)
    self.params_dialog.api_key_help_button.pack(ipadx=5,ipady=5,padx=5,pady=5)
    self.params_dialog.vanity_url_help_button=tk.Button(self.params_dialog,text='Help me find my Custom URL',command=self.vanity_url_help_button)
    self.params_dialog.vanity_url_help_button.pack(ipadx=5,ipady=5,padx=5,pady=5)
    
    ### API Key selection/input
    # select
    self.params_dialog.api_key_selection_map={}
    self.params_dialog.api_key_prompt_label=tk.LabelFrame(self.params_dialog,text='Please select a saved API key')
    self.params_dialog.api_key_prompt_label.pack(side='left',ipadx=1,ipady=1,padx=1,pady=1,fill='both')
    self.params_dialog.api_key_prompt_listbox=tk.Listbox(self.params_dialog.api_key_prompt_label,exportselection=0)
    self.init_api_key_prompt_listbox()
    self.params_dialog.api_key_prompt_listbox.pack(ipadx=5,ipady=5,padx=5,pady=5)
    self.params_dialog.api_key_prompt_listbox.bind('<<ListboxSelect>>',self.api_key_listbox_select)
    self.params_dialog.api_key_prompt_delete_button=tk.Button(self.params_dialog.api_key_prompt_label,text='Delete Selected API Key')
    self.params_dialog.api_key_prompt_delete_button.configure(command=self.delete_api_key_entry)
    self.params_dialog.api_key_prompt_delete_button.pack(ipadx=1,ipady=1,padx=1,pady=1)
    # input
    self.params_dialog.api_key_input_label=tk.Label(self.params_dialog.api_key_prompt_label,text='Or, add a new API key to the list:')
    self.params_dialog.api_key_input_label.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.api_key_input_name_label=tk.Label(self.params_dialog.api_key_prompt_label,text='New API key name:')
    self.params_dialog.api_key_input_name_label.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.api_key_input_name_entry=tk.Entry(self.params_dialog.api_key_prompt_label)
    self.params_dialog.api_key_input_name_entry.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.api_key_input_value_label=tk.Label(self.params_dialog.api_key_prompt_label,text='New API key:')
    self.params_dialog.api_key_input_value_label.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.api_key_input_value_entry=tk.Entry(self.params_dialog.api_key_prompt_label,show='*')
    self.params_dialog.api_key_input_value_entry.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.api_key_add_button=tk.Button(self.params_dialog.api_key_prompt_label,text='Add API key')
    self.params_dialog.api_key_add_button.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.api_key_add_button.configure(command=self.create_api_key_entry)
    
    ### SteamID selection/input
    # select
    self.params_dialog.steamid_selection_map={}
    self.params_dialog.steamid_prompt_label=tk.LabelFrame(self.params_dialog,text='Please select a saved SteamID')
    self.params_dialog.steamid_prompt_label.pack(side='left',ipadx=1,ipady=1,padx=1,pady=1,fill='both')
    self.params_dialog.steamid_prompt_listbox=tk.Listbox(self.params_dialog.steamid_prompt_label,exportselection=0)
    self.init_steamid_prompt_listbox()
    self.params_dialog.steamid_prompt_listbox.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.steamid_prompt_listbox.bind('<<ListboxSelect>>',self.steamid_listbox_select)
    self.params_dialog.steamid_prompt_delete_button=tk.Button(self.params_dialog.steamid_prompt_label,text='Delete Selected Steam ID')
    self.params_dialog.steamid_prompt_delete_button.configure(command=self.delete_steamid_entry)
    self.params_dialog.steamid_prompt_delete_button.pack(ipadx=1,ipady=1,padx=1,pady=1)
    # input
    self.params_dialog.steamid_input_label=tk.Label(self.params_dialog.steamid_prompt_label,text='Or, add a new Steam ID to the list:')
    self.params_dialog.steamid_input_label.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.steamid_input_name_label=tk.Label(self.params_dialog.steamid_prompt_label,text='New Steam ID name:')
    self.params_dialog.steamid_input_name_label.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.steamid_input_name_entry=tk.Entry(self.params_dialog.steamid_prompt_label)
    self.params_dialog.steamid_input_name_entry.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.steamid_input_value_label=tk.Label(self.params_dialog.steamid_prompt_label,text='New Steam ID:')
    self.params_dialog.steamid_input_value_label.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.steamid_input_value_entry=tk.Entry(self.params_dialog.steamid_prompt_label)
    self.params_dialog.steamid_input_value_entry.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.steamid_add_button=tk.Button(self.params_dialog.steamid_prompt_label,text='Add Steam ID')
    self.params_dialog.steamid_add_button.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.steamid_add_button.configure(command=self.create_steamid_entry)
    # by vanity url
    self.params_dialog.vanity_url_input_label=tk.Label(self.params_dialog.steamid_prompt_label,text="Or, lookup a new Steam ID by Custom URL lookup:\n(Requires API Key)")
    self.params_dialog.vanity_url_input_label.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.vanity_url_input_value_label=tk.Label(self.params_dialog.steamid_prompt_label,text='Custom URL for lookup:')
    self.params_dialog.vanity_url_input_value_label.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.vanity_url_input_value_entry=tk.Entry(self.params_dialog.steamid_prompt_label)
    self.params_dialog.vanity_url_input_value_entry.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.vanity_url_lookup_button=tk.Button(self.params_dialog.steamid_prompt_label,text='Lookup Steam ID')
    self.params_dialog.vanity_url_lookup_button.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.vanity_url_lookup_button.configure(command=self.lookup_vanity_url)

    ### Start steam_game_scale app
    # select
    self.params_dialog.start_label=tk.LabelFrame(self.params_dialog,text='Start Steam Game Scale')
    self.params_dialog.start_label.pack(side='left',ipadx=1,ipady=1,padx=1,pady=1,fill='both')
    self.params_dialog.start_button=tk.Button(self.params_dialog.start_label,text='Apply Parameters and Start App')
    self.params_dialog.start_button.pack(ipadx=1,ipady=1,padx=1,pady=1)
    self.params_dialog.start_button.configure(command=self.start_app_button)

    # Main loop go go go
    self.params_dialog.mainloop()

def print_tk(msg):
  popup=tk.Tk(None)
  popup.configure(bg=steam_colors.bg)
  img=ImageTk.PhotoImage(file='steam_game_scale.png')
  popup.tk.call('wm','iconphoto',popup._w,img)
  popup.title('MESSAGE')
  popup.option_add('*Background',steam_colors.bg)
  popup.option_add('*Foreground',steam_colors.fg)
  popup.option_add('*Selectbackground',steam_colors.fg)
  popup.option_add('*Selectforeground',steam_colors.bg)
  popup_label=tk.Label(popup,text=msg)
  popup_label.pack()
  popup_button=tk.Button(popup,text='OK',command=popup.destroy)
  popup_button.pack()
  popup.mainloop()

def insert_newlines(string, every=64):
    return '\n'.join(string[i:i+every] for i in range(0, len(string), every))

class no_steam_game():
  def __init__(self):
    self.steam_game_info={'appid':'No Game Selected',
                          'img_icon_url':'https://steamcommunity-a.akamaihd.net/public/shared/images/news/img_steam.gif',
                          'img_logo_url':'https://steamcommunity-a.akamaihd.net/public/shared/images/news/img_steam.gif',
                          'name':'No Game Selected',
                          'playtime_forever':'No Game Selected'}
    self.appid=self.steam_game_info['appid']
    self.img_icon_url=self.steam_game_info['img_icon_url']
    self.img_logo_url=self.steam_game_info['img_logo_url']
    self.name=self.steam_game_info['name']
    self.playtime_forever=self.steam_game_info['playtime_forever']
    self.owner_personaname='No Game Selected'
    self.owner_steamid='No Game Selected'
  def playtime_text(self):
    return 'No Game Selected'

class no_steam_player():
  def __init__(self):
    self.steam_id_64='No Friend Selected'
    self.steam_api_instance=None
    self.player_data={'personaname':'No Friend Selected',
                      'realname':'No Friend Selected',
                      'avatar':'https://steamcommunity-a.akamaihd.net/public/shared/images/news/img_steam.gif'}
    self.personaname=self.player_data['personaname']
    self.realname=self.player_data['realname']
    self.avatar_url=self.player_data['avatar']
    self.steam_games=[]
    self.steam_friends=[]
    
class steam_game_scale_tk():
  def init_avatar(self):
    self.app.avatar_img_label.configure(image=url_image.get(self.player.avatar_url))
    self.app.avatar_img_label.place(x=50,y=50,anchor='center')
  def init_player_info(self):
    self.app.player_info_label.configure(text=self.player.personaname)
    self.app.player_info_label.place(x=20,y=40,anchor='w')
    self.app.player_steamid_label.configure(text='SteamID: {}'.format(self.player.steam_id_64))
    self.app.player_steamid_label.place(x=20,y=60,anchor='w')
    self.app.player_realname_label.configure(text='Real Name: {}'.format(insert_newlines(self.player.realname,42)))
    self.app.player_realname_label.place(x=20,y=80,anchor='w')
  def init_player_lists(self):
    self.app.friends_listbox.configure(exportselection=0,yscrollcommand=self.app.friends_scrollbar.set,selectmode='single')
    self.app.friends_scrollbar.configure(command=self.app.friends_listbox.yview)
    self.app.friends_scrollbar.place(x=450,y=20,anchor='ne',height=280,width=450)
    self.app.friends_listbox.place(x=0,y=20,anchor='nw',height=280,width=450)
    for personaname in sorted([friend.personaname for friend in self.player.steam_friends]):
      self.app.friends_listbox.insert(self.app.friends_listbox.size(),personaname)
    self.app.games_listbox.configure(exportselection=0,yscrollcommand=self.app.games_scrollbar.set,selectmode='single')
    self.app.games_scrollbar.configure(command=self.app.games_listbox.yview)
    self.app.games_scrollbar.place(x=450,y=20,anchor='ne',height=280,width=450)
    self.app.games_listbox.place(x=0,y=20,anchor='nw',height=280,width=450)
    for name in sorted([game.name for game in self.player.steam_games]):
      self.app.games_listbox.insert(self.app.games_listbox.size(),name)
    self.app.friends_listbox.bind('<<ListboxSelect>>',self.friend_listbox_select)
    self.app.games_listbox.bind('<<ListboxSelect>>',self.game_listbox_select)
  def friend_listbox_select(self, event):
    selected_friend_personaname=self.app.friends_listbox.get(self.app.friends_listbox.curselection())
    for friend in self.player.steam_friends:
      if friend.personaname==selected_friend_personaname:
        self.app.selected_friend=friend
    self.init_comparisons()
  def game_listbox_select(self, event):
    selected_game_name=self.app.games_listbox.get(self.app.games_listbox.curselection())
    for game in self.player.steam_games:
      if game.name==selected_game_name:
        self.app.selected_game=game
    self.init_comparisons()
  def wipe_result_details(self):
    while self.app.comparison_results_listbox.size() > 0:
      self.app.comparison_results_listbox.delete(0)
    self.app.comparison_results_scrollbar.configure(command=self.app.comparison_results_listbox.yview)
    self.app.comparison_results_listbox.configure(exportselection=0,yscrollcommand=self.app.comparison_results_scrollbar.set,selectmode='single')
    self.app.comparison_results_scrollbar.place(x=450,y=0,anchor='ne',height=280,width=450)
    self.app.comparison_results_listbox.place(x=0,y=0,anchor='nw',height=280,width=450)
    self.app.comparison_results_details_image.configure(image=url_image.get('https://steamcommunity-a.akamaihd.net/public/shared/images/news/img_steam.gif'))
    self.app.comparison_results_details_image.place(x=50,y=50,anchor='center')
    self.app.comparison_results_details_name.configure(text='No Comparison Results Available',justify='left')
    self.app.comparison_results_details_name.place(x=110,y=40,anchor='w')
    self.app.comparison_results_details_number.configure(text='No Comparison Results Available',justify='left')
    self.app.comparison_results_details_number.place(x=110,y=70,anchor='w')
  def game_comparison_listbox_select(self, event):
    comparison_friend_personaname=self.app.comparison_results_listbox.get(self.app.comparison_results_listbox.curselection())
    for friend in self.player.steam_friends:
      if friend.personaname==comparison_friend_personaname:
        comparison_friend=friend
    self.app.comparison_results_details_image.configure(image=url_image.get(comparison_friend.avatar_url))
    self.app.comparison_results_details_name.configure(text='{}'.format(insert_newlines(comparison_friend.personaname,42)))
    for game in comparison_friend.steam_games:
      if game.name==self.app.selected_game.name:
        self.app.comparison_results_details_number.configure(text="Friend's playtime:\n{}".format(game.playtime_text()))
  def friend_comparison_listbox_select(self, event):
    comparison_game_name=self.app.comparison_results_listbox.get(self.app.comparison_results_listbox.curselection())
    for game in self.player.steam_games:
      if game.name==comparison_game_name:
        comparison_game=game
    # Comparison selected game img_icon_url
    self.app.comparison_results_details_image.configure(image=url_image.get(comparison_game.img_icon_url))
    # Comparison selected game personaname
    self.app.comparison_results_details_name.configure(text='{}'.format(insert_newlines(comparison_game.name,42)))
    # Comparison selected game playtime for app selected friend
    for game in self.app.selected_friend.steam_games:
      if game.name==comparison_game_name:
        self.app.comparison_results_details_number.configure(text="Friend's playtime:\n{}".format(game.playtime_text()))
  def init_game_result_details(self):
    self.wipe_result_details()
    playtime_threshold=int(self.app.game_comparison_parameter_entry.get())
    weights=playtime_weights(0,playtime_threshold)
    matching_friends=weights.game_compare_friends(self.app.selected_game,self.player.steam_friends)
    for personaname in sorted([friend.personaname for friend in matching_friends]):
      self.app.comparison_results_listbox.insert(self.app.comparison_results_listbox.size(),personaname)
    self.app.comparison_results_listbox.bind('<<ListboxSelect>>',self.game_comparison_listbox_select)
  def init_friend_result_details(self):
    self.wipe_result_details()
    playtime_threshold=int(self.app.friend_comparison_parameter_entry.get())
    weights=playtime_weights(0,playtime_threshold)
    matching_games_pairs=weights.friend_compare_games(self.app.selected_friend,self.player.steam_games)
    matching_games=[pair[1] for pair in matching_games_pairs]
    for name in sorted([game.name for game in matching_games]):
      self.app.comparison_results_listbox.insert(self.app.comparison_results_listbox.size(),name)
    self.app.comparison_results_listbox.bind('<<ListboxSelect>>',self.friend_comparison_listbox_select)
  def init_comparisons(self):
    self.app.friend_comparison_avatar_img_label.configure(image=url_image.get(self.app.selected_friend.avatar_url))
    self.app.friend_comparison_avatar_img_label.place(x=50,y=50,anchor='center')
    self.app.game_comparison_icon_img_label.configure(image=url_image.get(self.app.selected_game.img_icon_url))
    self.app.game_comparison_icon_img_label.place(x=50,y=50,anchor='center')
    self.app.friend_comparison_parameter_label.configure(text="Playtime filter in minutes\nfor games owned by:\n[{}]:".format(insert_newlines(self.app.selected_friend.personaname,42)))
    self.app.friend_comparison_parameter_label.configure(justify='left')
    self.app.friend_comparison_parameter_label.place(x=110,y=40,anchor='w')
    self.app.game_comparison_parameter_label.configure(text="Playtime filter in minutes\nfor friends who own game:\n[{}]:".format(insert_newlines(self.app.selected_game.name,42)))
    self.app.game_comparison_parameter_label.configure(justify='left')
    self.app.game_comparison_parameter_label.place(x=110,y=40,anchor='w')
    self.app.friend_comparison_parameter_entry.configure(exportselection=0)
    self.app.friend_comparison_parameter_entry.place(x=110,y=80,anchor='w')
    self.app.game_comparison_parameter_entry.configure(exportselection=0)
    self.app.game_comparison_parameter_entry.place(x=110,y=80,anchor='w')
    self.app.friend_comparison_games_count_label.configure(text="Total games owned by friend:\n{}".format(len(self.app.selected_friend.steam_games)))
    self.app.friend_comparison_games_count_label.configure(justify='left')
    self.app.friend_comparison_games_count_label.place(x=110,y=170,anchor='w')
    self.app.game_comparison_game_playtime_label.configure(text="Your playtime:\n{}".format(self.app.selected_game.playtime_text()))
    self.app.game_comparison_game_playtime_label.configure(justify='left')
    self.app.game_comparison_game_playtime_label.place(x=110,y=170,anchor='w')
    self.app.friend_comparison_button.configure(text='Run Friend Comparison')
    self.app.friend_comparison_button.configure(command=self.init_friend_result_details)
    self.app.friend_comparison_button.place(x=110,y=120,anchor='w')
    self.app.game_comparison_button.configure(text='Run Game Comparison')
    self.app.game_comparison_button.configure(command=self.init_game_result_details)
    self.app.game_comparison_button.place(x=110,y=120,anchor='w')
    self.wipe_result_details()
  def load_player_game_data(self):
    try:
      self.player=steam_player(self.api_instance,steam_id_64=self.api_instance.steam_id_64,recurse=True)
      self.popup.destroy()
    except Exception as e:
      print_tk("Error loading player and game data; cannot proceed.\nSometimes the Steam API does not respond and you have to try again.\n{}".format(traceback.format_exc()))
      sys.exit(1)
    
  def dialog_loading_player_game(self):
    self.popup=tk.Tk(None)
    selfpopup.configure(bg=steam_colors.bg)
    img=ImageTk.PhotoImage(file='steam_game_scale.png')
    self.popup.tk.call('wm','iconphoto',self.popup._w,img)
    self.popup.title('')
    self.popup.option_add('*Background',steam_colors.bg)
    self.popup.option_add('*Foreground',steam_colors.fg)
    self.popup.option_add('*Selectbackground',steam_colors.fg)
    self.popup.option_add('*Selectforeground',steam_colors.bg)
    self.popup_label=tk.Label(self.popup,text="Loading player and game data from the Steam API - this may take a moment.")
    self.popup_label.pack()
    self.popup_button=tk.Button(self.popup,text='OK',command=self.load_player_game_data)
    self.popup_button.pack()
    self.popup.mainloop()
  def __init__(self,params):
    self.params=params
    self.api_instance=None
    try:
      self.api_instance=steam_api(params.api_key_arg)
      if params.steamid_provided:
        self.api_instance.set_steam_id_64(params.steamid_arg)
      elif params.vanity_url_provided:
        self.params.steamid_arg=self.api_instance.vanity_url_steamid(params.vanity_url_arg)
        self.api_instance.set_steam_id_64(self.params.steamid_arg)
      else:
        print_tk("No steamid and no vanity url provided; cannot proceed")
        sys.exit(1)
    except Exception as e:
      print_tk("Error on steamid or vanity url; cannot proceed.")
      sys.exit(1)
    print_tk("Loading player and game data from the Steam API - this may take a moment.")
    try:
      self.player=steam_player(self.api_instance,steam_id_64=self.api_instance.steam_id_64,recurse=True)
    except Exception as e:
      print_tk("Please try again if your Steam ID and API key are valid - rarely, the Steam API fails and causes this error.")
      sys.exit(1)
    self.app = tk.Tk(None)
    self.app.geometry('900x900')
    self.app.resizable(width=False,height=False)
    img=ImageTk.PhotoImage(file='steam_game_scale.png')
    self.app.tk.call('wm','iconphoto',self.app._w,img)
    self.app.title('Steam Games Scale')
    self.app.option_add('*Background',steam_colors.bg)
    self.app.option_add('*Foreground',steam_colors.fg)
    self.app.configure(bg=steam_colors.bg)
    self.app.grid()
    # App is set up

    # Top row
    self.app.player_info_frame=tk.Frame(self.app)
    self.app.player_info_frame.configure(width=900,height=100)
    self.app.player_info_frame.grid(column=0,row=0)
    # Avatar in top row
    self.app.avatar_frame=tk.Frame(self.app.player_info_frame)
    self.app.avatar_frame.configure(width=100,height=100)
    self.app.avatar_frame.grid(column=0,row=0)
    self.app.avatar_img_label=tk.Label(master=self.app.avatar_frame)
    self.init_avatar()
    # player details in top row
    self.app.player_details_frame=tk.Frame(self.app.player_info_frame)
    self.app.player_details_frame.configure(width=800,height=100)
    self.app.player_details_frame.grid(column=1,row=0)
    self.app.player_info_label=tk.Label(self.app.player_details_frame)
    self.app.player_steamid_label=tk.Label(self.app.player_details_frame)
    self.app.player_realname_label=tk.Label(self.app.player_details_frame)
    self.init_player_info()
    # Player details are set up

    # Second row
    self.app.lists_frame=tk.Frame(self.app)
    self.app.lists_frame.configure(width=900,height=300)
    self.app.lists_frame.grid(column=0,row=1)
    # Friends frame left side of second row
    self.app.friends_frame_label=tk.Label(self.app.lists_frame,text='Steam Friends')
    self.app.friends_frame_label.grid(column=0,row=0,sticky='nsew')
    self.app.friends_frame=tk.Frame(self.app.lists_frame)
    self.app.friends_frame.configure(width=450,height=300)
    self.app.friends_frame.grid(column=0,row=1,sticky='nsew')
    self.app.friends_listbox=tk.Listbox(self.app.friends_frame,width=450,height=300)
    self.app.friends_scrollbar=tk.Scrollbar(self.app.friends_frame)
    # Games frame right side of second row
    self.app.games_frame_label=tk.Label(self.app.lists_frame,text='Steam Games')
    self.app.games_frame_label.grid(column=1,row=0,sticky='nsew')
    self.app.games_frame=tk.Frame(self.app.lists_frame)
    self.app.games_frame.configure(width=450,height=300)
    self.app.games_frame.grid(column=1,row=1,sticky='nsew')
    self.app.games_listbox=tk.Listbox(self.app.games_frame,width=450,height=300)
    self.app.games_scrollbar=tk.Scrollbar(self.app.games_frame)
    self.init_player_lists()
    # Lists still need bindings once comparisons are set up

    # Third row
    self.app.comparison_frame=tk.Frame(self.app)
    self.app.comparison_frame.configure(width=900,height=200)
    self.app.comparison_frame.grid(column=0,row=2)
    self.app.selected_friend=no_steam_player()
    self.app.selected_game=no_steam_game()
    # Parameters for finding games a friend has in common with you
    self.app.friend_comparison_params_frame=tk.Frame(self.app.comparison_frame)
    self.app.friend_comparison_params_frame.configure(width=450,height=200)
    self.app.friend_comparison_params_frame.grid(column=0,row=0)
    self.app.friend_comparison_avatar_img_label=tk.Label(self.app.friend_comparison_params_frame)
    self.app.friend_comparison_parameter_label=tk.Label(self.app.friend_comparison_params_frame)
    self.app.friend_comparison_parameter_entry=tk.Entry(self.app.friend_comparison_params_frame)
    self.app.friend_comparison_games_count_label=tk.Label(self.app.friend_comparison_params_frame)
    self.app.friend_comparison_button=tk.Button(self.app.friend_comparison_params_frame)
    # Parameters for finding friends who have a game in common with you
    # Stack up the inits so the details objects will exist when the inits clear them
    self.app.game_comparison_params_frame=tk.Frame(self.app.comparison_frame)
    self.app.game_comparison_params_frame.configure(width=450,height=200)
    self.app.game_comparison_params_frame.grid(column=1,row=0)
    self.app.game_comparison_icon_img_label=tk.Label(self.app.game_comparison_params_frame)
    self.app.game_comparison_parameter_label=tk.Label(self.app.game_comparison_params_frame)
    self.app.game_comparison_parameter_entry=tk.Entry(self.app.game_comparison_params_frame)
    self.app.game_comparison_game_playtime_label=tk.Label(self.app.game_comparison_params_frame)
    self.app.game_comparison_button=tk.Button(self.app.game_comparison_params_frame)

    # Fourth row
    self.app.comparison_results_frame=tk.Frame(self.app)
    self.app.comparison_results_frame.configure(width=900,height=300)
    self.app.comparison_results_frame.grid(column=0,row=3)
    # List of games or players that match the applied comparison
    self.app.comparison_results_list_frame=tk.Frame(self.app.comparison_results_frame)
    self.app.comparison_results_list_frame.configure(width=450,height=300)
    self.app.comparison_results_list_frame.grid(column=0,row=0)
    self.app.comparison_results_listbox=tk.Listbox(self.app.comparison_results_list_frame)
    self.app.comparison_results_scrollbar=tk.Scrollbar(self.app.comparison_results_list_frame)
    # Details of selected game or player match
    self.app.comparison_results_details_frame=tk.Frame(self.app.comparison_results_frame)
    self.app.comparison_results_details_frame.configure(width=450,height=300)
    self.app.comparison_results_details_frame.grid(column=1,row=0)
    self.app.comparison_results_details_image=tk.Label(self.app.comparison_results_details_frame)
    self.app.comparison_results_details_name=tk.Label(self.app.comparison_results_details_frame)
    self.app.comparison_results_details_number=tk.Label(self.app.comparison_results_details_frame)
    
    self.init_comparisons()
    self.app.mainloop()

if __name__ == '__main__':
################## Figure out an API key and a steam user to test with ##################
  # Can have files setting api_key_arg, steamid_arg, vanity_url_arg
  app=steam_game_scale_tk(params_input())


