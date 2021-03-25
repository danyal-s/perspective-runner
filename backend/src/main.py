import time
import datetime
from flask import Flask
app = Flask(__name__)

def main():
    app.run(host='0.0.0.0', port=5001)

@app.route('/')
def hello():
    return {
                "message":"Hello World!"
           }

if __name__ == "__main__":
    main()

# %%
