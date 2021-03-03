from app import create_app
from flask_cors import CORS
import os
if __name__ == '__main__':
    app = create_app()
    CORS(app)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', debug=True, port=port)
