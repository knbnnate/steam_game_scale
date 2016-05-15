from PIL import Image, ImageTk
import tkinter as tk
import io
import requests
from uuid import uuid4
import time
from game import steam_game, BadSteamGameInfoException
from player import steam_player

class url_image_store(tk.Tk):
  def __init__(self,parent=None,inert=False):
    if parent is not None or not inert:
      tk.Tk.__init__(self,parent)
    self.response_store={}
    self.jpg_bytes_store={}
    self.image_file_store={}
    self.python_image_store={}
    self.tk_image_store={}
    self.tk_label_store={}
    self.uuids={}
    self.time={}
  def url_image(self,url,parent=None):
    if parent is None:
      parent=self
    if url in self.uuids.keys():
      # We want a new label object for the existing image
      new_tk_label=tk.Label(parent,image=self.tk_image_store[self.uuids[url].get('tk_image',None)])
      new_tk_label_uuid=uuid4()
      self.tk_label_store[new_tk_label_uuid]=new_tk_label
      self.uuids[url]['tk_label'].append(new_tk_label_uuid)
      return new_tk_label
    else:
      tk_label_uuid=uuid4()
      self.tk_label_store[tk_label_uuid]=[]
      self.uuids[url]={'response':None,'jpg_bytes':None,'image_file':None,'python_image':None,'tk_image':None,'tk_label':None}
      # item, uuid, store the item, store the uuid
      response=requests.get(url)
      response_uuid=uuid4()
      self.response_store[response_uuid]=response
      self.uuids[url]['response']=response_uuid
      #
      jpg_bytes=response.content
      jpg_bytes_uuid=uuid4()
      self.jpg_bytes_store[jpg_bytes_uuid]=jpg_bytes
      self.uuids[url]['jpg_bytes']=jpg_bytes_uuid
      #
      image_file=io.BytesIO(jpg_bytes)
      image_file_uuid=uuid4()
      self.image_file_store[image_file_uuid]=image_file
      self.uuids[url]['image_file']=image_file_uuid
      #
      python_image=Image.open(image_file)
      python_image_uuid=uuid4()
      self.python_image_store[python_image_uuid]=python_image
      self.uuids[url]['python_image']=python_image_uuid
      #
      tk_image=ImageTk.PhotoImage(python_image)
      tk_image_uuid=uuid4()
      self.tk_image_store[tk_image_uuid]=tk_image
      self.uuids[url]['tk_image']=tk_image_uuid
      
      # We may want to know how old this data is at some point
      self.time[url]=int(time.time())
      
      # Finally, generate a label - multiple label uuids can exist for a url so store a list that might be appended to later
      tk_label=tk.Label(parent,image=tk_image)
      self.tk_label_store[tk_label_uuid]=tk_label
      self.uuids[url]['tk_label']=[tk_label_uuid]
      #
      return tk_label
  # This is very destructive and I hope I'll never have to use it
  def invalidate(self,url):
    if url in self.uuids.keys():
      response_uuid=self.uuids[url].pop('response',None)
      del self.response_store[response_uuid]
      jpg_bytes_uuid=self.uuids[url].pop('jpg_bytes',None)
      del self.jpg_bytes_store[jpg_bytes_uuid]
      image_file_uuid=self.uuids[url].pop('image_file',None)
      del self.image_file_store[image_file_uuid]
      python_image_uuid=self.uuids[url].pop('python_image',None)
      del self.python_image_store[python_image_uuid]
      tk_image_uuid=self.uuids[url].pop('tk_image',None)
      del self.tk_image_store[tk_image_uuid]
      tk_label_uuids=self.uuids[url].pop('tk_label',[])
      for tk_label_uuid in tk_label_uuids:
        del self.tk_label_store[tk_label_uuid]
      del self.time[url]
      del self.uuids[url]

class url_image():
  cache=url_image_store(inert=True)
  def __init__(self):
    pass
  @staticmethod
  def get(url,parent):
    return url_image.cache.url_image(url,parent)
  @staticmethod
  def invalidate(url):
    url_image.cache.invalidate(url)

class steam_colors():
  def __init__(self):
    pass
  bg='#171a21'
  fg='#767676'
  sbg=fg
  sfg=bg
  

class steam_game_tk(tk.Frame,steam_game):
  def __init__(self,master,steam_game_info,owner_personaname='Unknown Game Owner',owner_steamid=-1):
    self.init(master,steam_game_info,owner_personaname,owner_steamid)
  def init(self,master,steam_game_info,owner_personaname='Unknown Game Owner',owner_steamid=-1):
    steam_game.__init__(self,steam_game_info,owner_personaname,owner_steamid)
    tk.Frame.__init__(self,master)
    self.logo_height=69
    self.logo_width=184
    self.pack()
    self.configure(bg=steam_colors.bg)
    self.name_tk=tk.LabelFrame(text=self.name)
    self.name_tk.configure(bg=steam_colors.bg,fg=steam_colors.fg)
    self.name_tk.pack(side='top',fill='both',expand='yes')
    self.logo_frame_tk=tk.Frame(self.name_tk,bg=steam_colors.bg,height=self.logo_height,width=self.logo_width)
    self.logo_frame_tk.pack_propagate(0)
    self.logo_frame_tk.pack(side='top')
    self.logo_tk=url_image.get(url=self.img_logo_url,parent=self.logo_frame_tk)
    self.logo_tk.configure(bg=steam_colors.bg)
    self.logo_tk.pack(side='top',fill='both',expand='yes')
    self.owner_tk=tk.Label(master=self.name_tk,text="Owner: {} [{}]".format(self.owner_personaname,self.owner_steamid))
    self.owner_tk.configure(anchor='w')
    self.owner_tk.configure(bg=steam_colors.bg,fg=steam_colors.fg)
    self.owner_tk.pack(side='top',fill='both')
    self.playtime_tk=tk.Label(master=self.name_tk,text="Playtime: {}".format(self.playtime_text()))
    self.playtime_tk.configure(anchor='w')
    self.playtime_tk.configure(bg=steam_colors.bg,fg=steam_colors.fg)
    self.playtime_tk.pack(side='top',fill='both',anchor='w')
    self.widgets=[self.logo_frame_tk,self.logo_tk,self.name_tk,self.owner_tk,self.playtime_tk]
  def destroy_widgets(self):
    for widget in self.widgets:
      widget.destroy()
    self.destroy()
  # Simple but expensive
  def reinit(self,master,steam_game_info,owner_personaname='Unknown Game Owner',owner_steamid=-1):
    self.destroy_widgets()
    self.init(master,steam_game_info,owner_personaname,owner_steamid)
    
class steam_player_tk(tk.Frame,steam_player):
  def select_game(self,event):
    # Tkinter kind of blows, the ListBoxSelect event does not seem to exist and curselection() is always lagged behind button clicks
    # So, on click, get the selection nearest the cursor using the coordinates from the event. That is actually the simplest way
    # to do this even though that's really dumb.
    index=event.widget.nearest(event.y)
    chosen_name=self.steam_games_listbox_tk.get(index)
    for game in self.steam_games:
      if game.name==chosen_name:
        self.selected_steam_game_tk.reinit(self.master,game.steam_game_info,game.owner_personaname,game.owner_steamid) 
    self.selected_steam_game_tk.pack(side='right',fill='both',expand='yes')
  def __init__(self,master,steam_api_instance,playtime=0,steam_id_64=None,recurse=False):
    self.init(master,steam_api_instance,playtime,steam_id_64,recurse)
  def init(self,master,steam_api_instance,playtime=0,steam_id_64=None,recurse=False):
    steam_player.__init__(self,steam_api_instance,playtime,steam_id_64,recurse)
    tk.Frame.__init__(self,master,bg=steam_colors.bg)
    self.master=master
    no_game_selected_info={'empty_steam_game_img_icon_url':None,'empty_steam_game_img_logo_url':None}
    no_game_selected_info['appid']=None
    no_game_selected_info['name']='No Game Selected'
    no_game_selected_info['playtime_forever']=-1
    self.steam_games.insert(0,steam_game(no_game_selected_info,self.personaname,self.steam_id_64))
    self.pack(side='top',fill='both',expand='yes')
    self.personaname_tk=tk.LabelFrame(self,text=self.personaname)
    self.personaname_tk.configure(bg=steam_colors.bg,fg=steam_colors.fg)
    self.personaname_tk.pack(side='top',fill='both',expand='yes')
    self.avatar_tk=url_image.get(url=self.avatar_url,parent=self.personaname_tk)
    self.avatar_tk.configure(bg=steam_colors.bg,fg=steam_colors.fg)
    self.avatar_tk.pack(side='left')
    self.info_frame_tk=tk.Frame(self.personaname_tk)
    self.info_frame_tk.configure(bg=steam_colors.bg)
    self.info_frame_tk.pack(side='right',fill='both',expand='yes')
    self.realname_tk=tk.Label(self.personaname_tk,text="Real name: {}".format(self.realname))
    self.realname_tk.configure(bg=steam_colors.bg,fg=steam_colors.fg)
    self.realname_tk.configure(anchor='w')
    self.realname_tk.pack(side='top',fill='both',expand='yes')
    self.steamid_tk=tk.Label(self.personaname_tk,text="Steam ID: {}".format(self.steam_id_64))
    self.steamid_tk.configure(anchor='w')
    self.steamid_tk.configure(bg=steam_colors.bg,fg=steam_colors.fg)
    self.steamid_tk.pack(side='top',fill='both',expand='yes')
    friend_lens=[len(friend.personaname) for friend in self.steam_friends]
    game_lens=[len(game.name) for game in self.steam_games]
    min_len=max(friend_lens+game_lens)
    lb=tk.Listbox()
    char_width=tk.font.Font(lb,lb.cget("font")).measure("0")
    lb.destroy()
    self.lists_tk=tk.Frame(self)
    self.lists_tk.configure(bg=steam_colors.bg,height=25)
    self.lists_tk.pack(side='top',fill='both',expand='no')
    self.steam_friends_frame_tk=tk.LabelFrame(self.lists_tk,height=15,text='Steam Friends')
    self.steam_friends_frame_tk.configure(bg=steam_colors.bg,fg=steam_colors.fg)
    self.steam_friends_frame_tk.pack(side='left',fill='both',expand='no')
    self.steam_friends_listbox_tk=tk.Listbox(self.steam_friends_frame_tk,height=15)
    self.steam_friends_listbox_tk.configure(bg=steam_colors.bg,fg=steam_colors.fg)
    self.steam_friends_listbox_tk.configure(selectbackground=steam_colors.sbg,selectforeground=steam_colors.sfg)
    self.steam_friends_listbox_tk.pack(side='left',fill='both',expand='no')
    self.steam_friends_scrollbar_tk=tk.Scrollbar(self.steam_friends_frame_tk)
    self.steam_friends_scrollbar_tk.pack(side='right',fill='y')
    self.steam_friends_scrollbar_tk.configure(command=self.steam_friends_listbox_tk.yview)
    self.steam_friends_listbox_tk.configure(yscrollcommand=self.steam_friends_scrollbar_tk.set)
    self.steam_games_frame_tk=tk.LabelFrame(self.lists_tk,height=15,text='Steam Games')
    self.steam_games_frame_tk.configure(bg=steam_colors.bg,fg=steam_colors.fg)
    self.steam_games_frame_tk.pack(side='right',fill='both',expand='no')
    self.steam_games_listbox_tk=tk.Listbox(self.steam_games_frame_tk,height=15)
    self.steam_games_listbox_tk.configure(bg=steam_colors.bg,fg=steam_colors.fg)
    self.steam_games_listbox_tk.configure(selectbackground=steam_colors.sbg,selectforeground=steam_colors.sfg)
    self.steam_games_listbox_tk.pack(side='left',fill='both',expand='no')
    self.steam_games_listbox_tk.bind('<Button-1>',self.select_game)
    self.steam_games_scrollbar_tk=tk.Scrollbar(self.steam_games_frame_tk)
    self.steam_games_scrollbar_tk.pack(side='right',fill='y')
    self.steam_games_scrollbar_tk.configure(command=self.steam_games_listbox_tk.yview)
    self.steam_games_listbox_tk.configure(yscrollcommand=self.steam_games_scrollbar_tk.set)
    self.selected_steam_game_tk=steam_game_tk(master,no_game_selected_info,self.personaname,self.steam_id_64)
    if min_len*char_width < self.selected_steam_game_tk.logo_width:
      min_len=(self.selected_steam_game_tk.logo_width/char_width)+2
    frame_width=(2*min_len)+2
    self.lists_tk.configure(height=25,width=frame_width)
    self.lists_tk.pack()
    self.steam_friends_listbox_tk.configure(width=min_len)
    self.steam_friends_listbox_tk.pack()
    self.steam_games_listbox_tk.configure(width=min_len)
    self.selected_steam_game_tk.configure(width=min_len)
    self.selected_steam_game_tk.pack()
    self.selected_steam_game_tk.pack_propagate(0)
    self.selected_steam_game_tk.pack(side='right',fill='both',expand='yes',anchor='e')
    for friend in sorted([friend.personaname for friend in self.steam_friends]):
      insert_index=self.steam_friends_listbox_tk.size()
      self.steam_friends_listbox_tk.insert(insert_index,friend)
    for game in sorted([game.name for game in self.steam_games]):
      insert_index=self.steam_games_listbox_tk.size()
      self.steam_games_listbox_tk.insert(insert_index,game)
    self.steam_games_listbox_tk.insert(0,'No Game Selected')
    self.widgets=[self.personaname_tk,self.avatar_tk,self.info_frame_tk,self.realname_tk]
    self.widgets=self.widgets+[self.steamid_tk,self.lists_tk,self.steam_friends_frame_tk]
    self.widgets=self.widgets+[self.steam_friends_listbox_tk,self.steam_friends_scrollbar_tk]
    self.widgets=self.widgets+[self.steam_games_frame_tk,self.steam_games_listbox_tk]
    self.widgets=self.widgets+[self.steam_games_scrollbar_tk]
  def destroy_widgets(self):
    for widget in self.widgets:
      widget.destroy()
  def reinit(self,master,steam_api_instance,playtime=0,steam_id_64=None,recurse=False):
    self.destroy_widgets()
    self.init(master,steam_api_instance,playtime,steam_id_64,recurse)

class tests():
  def __init__(self,api_instance):
    self.api_instance=api_instance
  def run_tests(self,url_image_tests=False,game_tests=False):
    if url_image_tests:
      poc_url='https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/9c/9cecbe1f11b6fe03a1cc1fc3e9b779c37d160eb9.jpg'
      def oops(root):
        url_image.invalidate(poc_url)
      poc_url_2='https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/9c/9cecbe1f11b6fe03a1cc1fc3e9b779c37d160eb9_full.jpg'
      root=tk.Tk()
      root.title("Oops!")
      image_label=url_image.get(poc_url,parent=root)
      image_label.pack(expand='yes')
      bigger_image_label=url_image.get(poc_url_2,parent=root)
      bigger_image_label.pack(expand='yes')
      image_label_2=url_image.get(poc_url,parent=root)
      image_label_2.pack(expand='yes')

      ########################################################################################
      root.bind('<Button-1>',oops)                                                           #
      # Now if you click the test app, some of the cars will disappear! Oh no!               #
      # Should probably only do this for stuff that's not supposed to be displayed any more. #
      ########################################################################################
      root.focus_force()
      root.mainloop()

    if game_tests:
      game_app=tk.Tk()
      game_app.title('Game stuff yeah!')
      test_steam_game_tk=steam_game_tk(game_app,{'appid':391540,'img_icon_url':'2ce672b89b63ec1e70d2f12862e72eb4a33e9268','img_logo_url':'ae953fb87a0fd4958ca21995226c065f33290eba','name':'Undertale','playtime_forever':147},"Wild 'n Wooly Shambler",76561197960781001)
      game_app.mainloop()

    print('Loading data from the Steam API for the tk_gui steam_player_tk test, please wait a moment...')
    friend_app=tk.Tk()
    friend_app.title('Friend stuff wooo!')
    api_instance=self.api_instance
    test_steam_player_tk=steam_player_tk(friend_app,self.api_instance,steam_id_64=api_instance.steam_id_64,recurse=True)
    print('Loaded - check for lost focus')
    friend_app.focus_force()
    friend_app.mainloop()










  
