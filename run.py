from tooldb import app
import os

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('DEBUG') == '1')

# docker command to run container mapping to http port and passing environment variable for debug mode
# docker run -p 80:5000 -e DEBUG=1 <image name>
