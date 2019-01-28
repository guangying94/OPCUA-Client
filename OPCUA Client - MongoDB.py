import opcua
from opcua import Client
from opcua import ua
import time
import pymongo
from pymongo import MongoClient


if __name__ == "__main__":
    ## first connect to OPC Server
    client = Client("opc.tcp://OPC-Server:53530/OPCUA/SimulationServer")

    ## then connect to Mongo DB
    ## database is "test"
    ## collection is "opc3"
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient.test
    mycol = mydb.opc3

    try:
        client.connect()
        counter = client.get_node("ns=5;s=Counter1")
        expression = client.get_node("ns=5;s=Expression1")
        random = client.get_node("ns=5;s=Random1")
        sawtooth = client.get_node("ns=5;s=Sawtooth1")
        sinusoid = client.get_node("ns=5;s=Sinusoid1")
        square = client.get_node("ns=5;s=Square1")
        triangle = client.get_node("ns=5;s=Triangle1")
        datapoint = 0

        ## only log 1000 data points, can replace with "True"
        while(datapoint < 1000):
            counterValue = counter.get_value()
            expressionValue = expression.get_value()
            randomValue = random.get_value()
            sawtoothValue = sawtooth.get_value()
            sinusoidValue = sinusoid.get_value()
            squareValue = square.get_value()
            triangleValue = triangle.get_value()
            
            opcdata = {'Object':'opc-prosys','Counter':counterValue,'Expression':expressionValue,'Random':randomValue,'Sawtooth':sawtoothValue,'Sinusoid':sinusoidValue,'Square':squareValue,'Triangle':triangleValue}
            result = mycol.insert_one(opcdata)
            print(result.inserted_id)
            print(opcdata)
            datapoint = datapoint + 1
            time.sleep(0.00001)


    finally:
        client.disconnect()

