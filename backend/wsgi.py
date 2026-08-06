import os

from app import create_app

app = create_app(os.environ.get("APP_CONFIG", "config.DevelopmentConfig"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
