#!/usr/bin/python3

from modules.__init__ import create_app
from modules.config import ProductionConfig
from modules.data_functions import send_notifications

# Initialize flask app
app = create_app(ProductionConfig())

    
# Start loop to send notifications
#send_notifications()

print('script finished')

if __name__ == "__main__":
    # Start main application
    app.run()
