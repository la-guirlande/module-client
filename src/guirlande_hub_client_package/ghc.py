import requests
import socketio

class Module:
  """Module class used to instantiate the module and communicate with the backend"""

  def __init__(self, type):
    self.type = type
    self.__token = ''
    self.socket = socketio.Client()
    self.listeners = []
  
  def send(self, eventName, data):
    eventName = 'module.' + self.type + '.' + eventName
    self.socket.emit(eventName, data)
    print('Sended event %s', eventName)
