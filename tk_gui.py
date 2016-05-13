from PIL import Image, ImageTk
import tkinter as tk
import io
import requests
from uuid import uuid4
import time

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

def tests():
  def oops(root):
    url_image.invalidate(poc_url)
    
  poc_url='https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/9c/9cecbe1f11b6fe03a1cc1fc3e9b779c37d160eb9.jpg'
  poc_url_2='https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/9c/9cecbe1f11b6fe03a1cc1fc3e9b779c37d160eb9_full.jpg'
  root=tk.Tk()
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
