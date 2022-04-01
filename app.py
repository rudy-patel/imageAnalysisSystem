from server.main import create_app
import os

if __name__ == "__main__":
    app = create_app(os.getenv('FLASK_CONFIG') or 'dev')
    app.run()