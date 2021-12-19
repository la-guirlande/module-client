# Guirlande Hub - Module client

This client is used to communicate with the Guirlande Hub backend. All connected objects must integrate this library.

# Installation
```Shell
$ pip install guirlande_hub_client
```

# Usage
```Python
from guirlande_hub_client_package.ghc import Module

# Creating new module with module type (0 = LED_STRIP)
module = Module(0)

# Add websocket listeners
@module.listening('color')
def color_listener(data):
  print(data['r'], data['g'], data['b'])

  # Send data to websocket event
  module.send('color', { 'message': 'Received color !' })

# Connect / Disconnect the module
try:
  module.connect('http://localhost:8000')
  module.register()
  print('Connected')
except KeyboardInterrupt:
  module.disconnect()
  print('Disconnected')
```
