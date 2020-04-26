import sys
import time
import flask
from flask import request, jsonify, make_response, render_template
from opcua import Client, ua
from functools import wraps
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger.utils import swag_from

###########
##Flask app setting
###########
app = flask.Flask(__name__)
app.config["DEBUG"] = True

###########
## Flasgger settings
###########
app.json_encoder = LazyJSONEncoder
swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'opc_apispec',
            "route": '/opc_apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

template = dict(
    info={
        'title': LazyString(lambda: 'API Documentation'),
        'version': LazyString(lambda: '1.0'),
        'description': LazyString(lambda: 'API documentation for prototpye. All API requires basic authentication.'),
    },
    host=LazyString(lambda: request.host),
    schemes=[LazyString(lambda: 'https' if request.is_secure else 'http')],
    foo=LazyString(lambda: "Bar")
)

swagger = Swagger(app, config=swagger_config, template=template)

###########
## Authentication Decorator
###########
def auth_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        auth = request.authorization
        if auth and auth.username == "<username>" and auth.password == "<password>":
            return f(*args,**kwargs)
            
        return make_response('Please login!',401,{'WWW-Authenticate':'Basic realm="Login Required"'})
        
    return decorated

###########
## Connect to OPC UA Server
###########
client = Client("opc.tcp://<opc ua server address>:<opc ua server port number>")

###########
## Initialize variable with respective OPC UA node
###########
GearMotorTemperatureLeftNode = client.get_node("<OPC UA Server node>")
GearMotorTemperatureRightNode = client.get_node("<OPC UA Server node>")
GearModeEnableNode = client.get_node("<OPC UA Server node>")
GearMotorTurnDirectionNode = client.get_node("<OPC UA Server node>")
SetGearMotorSpeedNode = client.get_node("<OPC UA Server node>")
ControlPanelOpsModeNode = client.get_node("<OPC UA Server node>")

###########
## Homepage
###########
@app.route('/',methods=['GET'])
def home():
    return render_template('index.html',title='Welcome')

###########
## api to get values for all nodes
###########
@app.route('/api/reading',methods=['GET'])
@auth_required
@swag_from('getnode.yml')
def getreading():
    client.connect()
    response = {}
    response["GearMotorTemperatureLeft"] = GearMotorTemperatureLeftNode.get_value()
    response["GearMotorTemperatureRight"] = GearMotorTemperatureRightNode.get_value()
    response["GearModeEnable"] = GearModeEnableNode.get_value()
    response["GearMotorTurnDirection"] = GearMotorTurnDirectionNode.get_value()
    response["SetGearMotorSpeed"] = SetGearMotorSpeedNode.get_value()
    response["ControlPanelOpsMode"] = ControlPanelOpsModeNode.get_value()
    client.disconnect()
    return(jsonify(response))

###########
## api to toggle gear mode
###########
@app.route('/api/gearmode/toggle',methods=['GET'])
@auth_required
@swag_from('gearmode.yml')
def toggle_gearmode():
    client.connect()
    currentvalue = bool(GearModeEnableNode.get_value())
    setting = ua.DataValue(ua.Variant(not currentvalue,ua.VariantType.Boolean))
    GearModeEnableNode.set_value(setting)
    if currentvalue == False:
        msg = "Gear motor is started."
    else:
        msg = "Gear motor is stopped."
    client.disconnect()    
    return(jsonify(message=msg))

###########
## api to toggle motor turn direction
###########
@app.route('/api/motordirection/toggle',methods=['GET'])
@auth_required
@swag_from('motordirection.yml')
def toggle_direction():
    client.connect()
    currentvalue = bool(GearMotorTurnDirectionNode.get_value())
    setting = ua.DataValue(ua.Variant(not currentvalue,ua.VariantType.Boolean))
    GearMotorTurnDirectionNode.set_value(setting)
    if currentvalue == False:
        msg = "Gear motor direction is set to clockwise."
    else:
        msg = "Gear motor direction is set to anti-clockwise."
    client.disconnect()
    return(jsonify(message=msg))

###########
## api to set speed
###########
@app.route('/api/motorspeed/speed=<speed>',methods=['GET'])
@auth_required
@swag_from('motorspeed.yml')
def set_speed(speed):
    client.connect()
    targetspeed = int(speed)
    setting = ua.DataValue(ua.Variant(targetspeed,ua.VariantType.Int16))
    SetGearMotorSpeedNode.set_value(setting)
    client.disconnect()
    return(jsonify(message="Gear motor speed is set to %s." % str(targetspeed)))

###########
## api to set ops mode
###########
@app.route('/api/controlpanelops/mode=<mode>',methods=['GET'])
@auth_required
@swag_from('opsmode.yml')
def set_mode(mode):
    client.connect()
    targetmode = int(mode)
    setting = ua.DataValue(ua.Variant(targetmode,ua.VariantType.Int16))
    ControlPanelOpsModeNode.set_value(setting)
    client.disconnect()
    if targetmode == 0:
        return(jsonify(message="Control Panel Ops mode is set to false."))
    elif targetmode == 1:
        return(jsonify(message="Control Panel Ops mode is set to true."))
    else:
        return(jsonify(message="Control Panel Ops mode is set to maintenance."))

###########
## handle error page
###########
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', title='Error')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
