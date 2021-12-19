import time
import requests
import socketio

class Module:
  """Module class used to instantiate the module and communicate with the backend."""

  def __init__(self, type):
    config = self.__read_config()
    self.type = type
    self.registered = False
    self.__token = config['token']
    self.socket = socketio.Client()
    self.listeners = []
  
  def register(self):
    """Registers module to the backend.
    
    If the module token is not set in the configuration file (token=""), this method will send a `POST /modules/register`
    to gets a new token. This call will store this module in the backend with status = `PENDING`.

    If the token is stored on the configuration file, this method will periodically check if the module is registered (status != `PENDING`) by
    a websocket event emission (`module.register`) while the module receives a `MODULE_IS_PENDING` error.

    After a positive response on the same event, the module is officially registered in the backend and can communicate to dedicated events.
    """
    if self.__token == '':
      res = requests.post("http://localhost/modules/register", { 'type': self.type })
      self.__token = res.json()['token']
      self.__write_config('token', self.__token)
    self.__checkRegistration()
  
  def connect(self, address):
    """Connects the module websocket to the backend"""
    self.socket.connect(address)

  def disconnect(self):
    """Disconnects the module websocket from the backend"""
    self.socket.disconnect()
  
  def listening(self, event_name, raw_event_name=bool):
    """Listening on a websocket event.
    
    This method is a decorator. Usage example :
    ```Python
    module = ghc.Module(0)

    @module.listening('color')
    def color_listener(data):
      print(data)
    ```
    """
    def inner(fc):
      self.socket.on(('module.' + str(self.type) + '.' + event_name) if not raw_event_name else event_name, fc)
      return fc
    return inner

  def send(self, event_name, data):
    """Sends data to a websocket event"""
    event_name = 'module.' + str(self.type) + '.' + event_name
    self.socket.emit(event_name, data)
    print('Sended event %s', event_name)
  
  def __read_config(self):
    """Reads the configuration file."""
    try:
      config = {}
      with open('config') as f:
        for line in f.readlines():
          items = line.split('=')
          config[items[0]] = items[1]
      return config
    except FileNotFoundError:
      print('Creating configuration file')
      self.__create_config({ 'token': '' })
      return self.__read_config() # Recursive if file not created
  
  def __create_config(self, config):
    """Creates the configuration file.
    
    This method will erase current configuration file if exists.
    """
    with open('config', 'w') as f:
      for key, value in config.items():
        f.write(key + '=' + value)
  
  def __write_config(self, key, value):
    """Writes a key value pair into the configuration file.
    
    This method will read and recreate the configuration file.
    """
    config = self.__read_config()
    config[key] = value
    self.__create_config(config)
  
  def __checkRegistration(self):
    """Checks the module registration state.
    
    The module will be registered when the `module.register` event listener receives a positive response.
    While the registration is not validated, the program will freezes to sends periodically websocket event `module.register`.
    """
    @self.socket.on('module.register')
    def register(data):
      if data['status']:
        self.registered = True
        print('Module registered')

    i = 0
    while True:
      i += 1
      print('Checking registration (attempt', i, ')')
      self.socket.emit('module.register', { 'token': self.__token })
      time.sleep(10)
      if self.registered:
        break
