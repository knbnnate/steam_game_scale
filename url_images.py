import tkinter as tk
from PIL import Image, ImageTk
import io
import requests
from uuid import uuid4
import time

class url_image_store():
  def __init__(self):
    self.response_store={}
    self.img_bytes_store={}
    self.image_file_store={}
    self.python_image_store={}
    self.tk_image_store={}
    self.uuids={}
    self.time={}
  def url_image(self,url):
    if url in self.uuids.keys():
      return self.tk_image_store[self.uuids[url].get('tk_image',None)]
    else:
      self.uuids[url]={'response':None,'img_bytes':None,'image_file':None,'python_image':None,'tk_image':None}
      # item, uuid, store the item, store the uuid
      response=requests.get(url)
      response_uuid=uuid4()
      self.response_store[response_uuid]=response
      self.uuids[url]['response']=response_uuid
      #
      img_bytes=response.content
      img_bytes_uuid=uuid4()
      self.img_bytes_store[img_bytes_uuid]=img_bytes
      self.uuids[url]['img_bytes']=img_bytes_uuid
      #
      image_file=io.BytesIO(img_bytes)
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
      #
      return tk_image
  # This is very destructive and I hope I'll never have to use it
  def invalidate(self,url):
    if url in self.uuids.keys():
      response_uuid=self.uuids[url].pop('response',None)
      del self.response_store[response_uuid]
      img_bytes_uuid=self.uuids[url].pop('img_bytes',None)
      del self.img_bytes_store[img_bytes_uuid]
      image_file_uuid=self.uuids[url].pop('image_file',None)
      del self.image_file_store[image_file_uuid]
      python_image_uuid=self.uuids[url].pop('python_image',None)
      del self.python_image_store[python_image_uuid]
      tk_image_uuid=self.uuids[url].pop('tk_image',None)
      del self.tk_image_store[tk_image_uuid]
      del self.time[url]
      del self.uuids[url]

class url_image():
  cache=url_image_store()
  def __init__(self):
    pass
  @staticmethod
  def get(url):
    return url_image.cache.url_image(url)
  @staticmethod
  def invalidate(url):
    url_image.cache.invalidate(url)
