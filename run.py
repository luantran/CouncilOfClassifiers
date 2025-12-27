import sys
import os

# Add server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from server.app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)