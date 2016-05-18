import tkinter as tk               #
from PIL import Image, ImageTk     # PIL dependency
import sys                         #
import os                          #
from api import steam_api          # depends on requests
from url_images import url_image   # depends on requests
from player import steam_player    #
from game import steam_game        #
from scale import playtime_weights #
import traceback                   #

class steam_colors():
  def __init__(self):
    pass
  bg='#171a21'
  fg='#767676'
  sbg=fg
  sfg=bg
  
class params_input():
  def submit_steamid(self):
    self.steamid_arg=id_dialog.steamid_prompt_entry.get()
    self.steamid_provided=True
    self.id_dialog.destroy()
  def submit_vanity_url(self):
    self.vanity_url_arg=self.id_dialog.vanity_url_prompt_entry.get()
    self.vanity_url_provided=True
    self.id_dialog.destroy()
  def submit_api_key(self):
    self.api_key_arg=self.api_key_dialog.api_key_prompt_entry.get()
    self.api_key_provided=True
    self.api_key_dialog.destroy()
  def __init__(self):
    self.steamid_provided=False
    self.steamid_arg=None
    self.vanity_url_provided=False
    self.vanity_url_arg=None
    self.api_key_provided=False
    self.api_key_arg=None
    if os.path.isfile('api_key.py'):
      try:
        from api_key import api_key_arg
        self.api_key_arg=api_key_arg
        self.api_key_provided=True
      except:
        print('api_key.py does not set an api_key_arg string')
    if os.path.isfile('vanity_url.py'):
      try:
        from vanity_url import vanity_url_arg
        self.vanity_url_arg=vanity_url_arg
        self.vanity_url_provided=True
      except:
        print('vanity_url.py does not set a vanity_url_arg string')
    if not self.vanity_url_provided:
      if os.path.isfile('steamid.py'):
        try:
          from steamid import steamid_arg
          self.steamid_arg=steamid_arg
          self.steamid_provided=True
        except:
          print('steamid.py does not set a steamid_arg string')
    # Can override the files with command line args
    for arg in sys.argv:
      if arg.startswith('--vanityurl='):
        self.vanity_url_arg=arg.partition('=')[2]
        self.vanity_url_provided=True
      if arg.startswith('--apikey='):
        self.api_key_arg=arg.partition('=')[2]
        self.api_key_provided=True
      if arg.startswith('--steamid='):
        self.steamid_arg=arg.partition('=')[2]
        self.steamid_provided=True
    # If nothing provided in directory or on command line, prompt user in tkinter
    if not self.steamid_provided and not self.vanity_url_provided:
      self.id_dialog = tk.Tk(None)
      self.id_dialog.title('ID Dialog')
      img=ImageTk.PhotoImage(file='steam_game_scale.png')
      self.id_dialog.tk.call('wm','iconphoto',self.id_dialog._w,img)
      self.id_dialog.configure(bg=steam_colors.bg)
      self.id_dialog.option_add('*Background',steam_colors.bg)
      self.id_dialog.option_add('*Foreground',steam_colors.fg)
      self.id_dialog.steamid_prompt_label=tk.LabelFrame(self.id_dialog,text='Please enter your SteamID')
      self.id_dialog.steamid_prompt_label.pack()
      self.id_dialog.steamid_prompt_entry=tk.Entry(self.id_dialog.steamid_prompt_label)
      self.id_dialog.steamid_prompt_entry.pack()
      self.id_dialog.steamid_submit_button=tk.Button(self.id_dialog.steamid_prompt_label,text='Submit SteamID')
      self.id_dialog.steamid_submit_button.configure(command=self.submit_steamid)
      self.id_dialog.steamid_submit_button.pack()
      self.id_dialog.vanity_url_prompt_label=tk.LabelFrame(self.id_dialog,text='OR, please enter your vanity url')
      self.id_dialog.vanity_url_prompt_label.pack()
      self.id_dialog.vanity_url_prompt_entry=tk.Entry(self.id_dialog.vanity_url_prompt_label)
      self.id_dialog.vanity_url_prompt_entry.pack()
      self.id_dialog.vanity_url_submit_button=tk.Button(self.id_dialog.vanity_url_prompt_label,text='Submit Vanity URL')
      self.id_dialog.vanity_url_submit_button.configure(command=self.submit_vanity_url)
      self.id_dialog.vanity_url_submit_button.pack()
      self.id_dialog.mainloop()
    if not self.api_key_provided:
      self.api_key_dialog = tk.Tk(None)
      self.api_key_dialog.title('API Key Dialog')
      img=ImageTk.PhotoImage(file='steam_game_scale.png')
      self.api_key_dialog.tk.call('wm','iconphoto',self.api_key_dialog._w,img)
      self.api_key_dialog.configure(bg=steam_colors.bg)
      self.api_key_dialog.option_add('*Background',steam_colors.bg)
      self.api_key_dialog.option_add('*Foreground',steam_colors.fg)
      self.api_key_dialog.api_key_prompt_label=tk.LabelFrame(self.api_key_dialog,text='Please enter your Steam API Key')
      self.api_key_dialog.api_key_prompt_label.pack()
      self.api_key_dialog.api_key_prompt_entry=tk.Entry(self.api_key_dialog.api_key_prompt_label)
      self.api_key_dialog.api_key_prompt_entry.pack()
      self.api_key_dialog.api_key_submit_button=tk.Button(self.api_key_dialog.api_key_prompt_label,text='Submit Steam API Key')
      self.api_key_dialog.api_key_submit_button.configure(command=self.submit_api_key)
      self.api_key_dialog.api_key_submit_button.pack()
      self.api_key_dialog.mainloop()

def print_tk(msg):
  popup=tk.Tk(None)
  popup.configure(bg=steam_colors.bg)
  img=ImageTk.PhotoImage(file='steam_game_scale.png')
  popup.tk.call('wm','iconphoto',popup._w,img)
  popup.title('')
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
      print_tk("Error loading player and game data; cannot proceed.\n{}".format(traceback.format_exc()))
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
      print_tk("Error loading player and game data; cannot proceed.\n{}".format(traceback.format_exc()))
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


