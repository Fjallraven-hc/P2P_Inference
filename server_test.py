import json
from blockutils import *
import logging
import websocket
import time
import argparse
from multiprocessing import Process, Queue

from pytriton_server_prepare import *
from request_collection import *

logging.basicConfig(level=logging.DEBUG)
parser = argparse.ArgumentParser(description="AntGrid Server Communication Module.")

parser.add_argument('--host', type=str, default='162.105.146.176', help='IP address of the scheduler.')
parser.add_argument('--port', type=str, default='3000', help='Port of the scheuler.')
parser.add_argument('--route', type=str, default='ws', help='Route of the websocket page.')
parser.add_argument('-u', '--username', type=str, required=True, help='Username to login.')
parser.add_argument('-p', '--password', type=str, required=True, help='Password to login')

args = parser.parse_args()

def set_login_package(token: str, device: str, devicemem: str):
    return {
        "type": PackageType.Login,
        "authorization": token,
        "device": device,
        "deviceMem": devicemem
    }



device = "NVIDIA GTX 1080Ti"
devicemem = "2 GiB"


state_pack = {
    "type": PackageType.ServerState,
    "state": "Running",
    "model": "Stable Diffution v1.4",
}


token = ""

def on_open(wsapp):
    logging.info("Connection Established.")
    info = {
        "type": PackageType.Login,
        "authorization": token,
        "device": device,
        "devicemem": devicemem
    }
    wsapp.send(json.dumps(info))

def on_message(wsapp, message):
    message = json.loads(message)
    if message["type"] == PackageType.PulseCheck:
        logging.info("Pluse Check.")
        wsapp.send(json.dumps(state_pack))

    elif message["type"] == PackageType.Verification:
        if message["state"] == "failed":
            logging.warning("Auth Failed.")
            return
        print("receive model message as below:\n", message)
        model_to_run = message["model"]
        # here you got the model_to_run message, and decide on which model to run.
        logging.info(f"Prepare pytriton for model: {model_to_run}")
        pytriton_file_name = prepare(message)
        p = Process(target=run_pytriton, args=(pytriton_file_name,))
        p.start()
        ##########################################################################
        time.sleep(5)
        response = {
            "type": PackageType.ServerState,
            "state": "Running",
            "model": model_to_run
        }
        wsapp.send(json.dumps(response))
        logging.info("Running {}".format(model_to_run))

    elif message["type"] == PackageType.Request:
        payload = json.loads(message["payload"])
        print(payload)
        outputs = infer(payload[0][1])
        print(type(outputs))
        response = {
            "type": PackageType.Response,
            "payload": outputs[0]
        } # this
        wsapp.send(json.dumps(response))

def on_cont_message(wsapp, frame_data, frame_fin):
    logging.info("Receive continuous message.")
    print(type(frame_data), frame_fin,"----", sep="\n")

def on_data(wsapp, frame_data, frame_opcode, frame_fin):
    pass

if __name__ == '__main__':
    try:
        logging.info("ServerRuntime Start.")
        url = 'ws://' + args.host + ':' + args.port + '/' + args.route
        login_url = 'http://' + args.host + ':' + args.port + '/' + "login"
        token = get_token(args.username, args.password, login_url)
        wsapp = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message, on_cont_message=on_cont_message, on_data=on_data)
        wsapp.run_forever()
    except KeyboardInterrupt:
        logging.info("ServerRuntime exited.")
        wsapp.close()
