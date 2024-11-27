#!/usr/bin/python3

from modules.config import ProductionConfig
from modules.__init__ import create_app

# Initialize flask app
app = create_app(ProductionConfig())

print('script finished')

if __name__ == "__main__":
    app.run()
