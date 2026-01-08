import sys
import os

# Add server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from server.app import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment variable (Render provides PORT env var)
    port = int(os.environ.get('PORT', 5000))

    # In production, don't use debug mode
    debug = os.environ.get('FLASK_ENV') == 'development'

    app.run(host='0.0.0.0', port=port, debug=debug)