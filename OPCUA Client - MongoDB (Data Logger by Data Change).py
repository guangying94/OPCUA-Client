import opcua
from opcua import Client
from opcua import ua
import time
import pymongo
from pymongo import MongoClient


class SubHandler(object):

    def __init__(self,engine):
        self.engine = engine

    def datachange_notification(self,node,val,data):
        ## print("Python: New data change event",node,val)
        opcdata = {"Object":"CM4Ch0","Value":val}
        print(opcdata)
        if self.engine==mycol:
           result = mycol.insert_one(opcdata)
           ## print(result.inserted_id)


    def event_notification(self,event):
        print("Python: New event",event)

if __name__ == "__main__":
    ## connect to OPC Server
    client = Client("opc.tcp://OPC-Server:4840")
    print('OPC server connected')

    ## connect to MongoDB
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient.test
    mycol = mydb.opc4
    print('Mongo connected')

    try:
        client.connect()
        print("connected")
        counter = client.get_node("ns=2;s=Device.CM4Ch0")
        handler = SubHandler(mycol)
        sub = client.create_subscription(0.1,handler)
        handle = sub.subscribe_data_change(counter)

        while(True):
            time.sleep(0.000001)

    finally:
        client.disconnect()

        
