from flask import Flask, render_template
from flask_restful import Api

from config import ap_url
from resource_controller import Ap_Locker_Controller, Ap_Proxy_Controller, Ap_Payment_Gateway_Controller

app = Flask(__name__)
api = Api(app)

# register route for home page
@app.route("/")
def home():
    return render_template('home.html', ap_url="http://"+ap_url)

# register route for three APIs
api.add_resource(Ap_Locker_Controller, '/locker', '/locker/', '/locker/<string:type>')
api.add_resource(Ap_Proxy_Controller, '/proxy', '/proxy/', '/proxy/<string:type>')
api.add_resource(Ap_Payment_Gateway_Controller, '/payment_gateway', '/payment_gateway/', '/payment_gateway/<string:type>')

if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)