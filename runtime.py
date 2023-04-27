import time
import json
import socket
import requests

client = socket.socket()
# connect to server
client.connect(('162.105.146.176', 7777))
service_provided = {
    "stable_diffusion_txt2image": "input: [prompt]",
    "stable_diffusion_image2image": "input: [prompt, image]"
}
# msg = "this is a runtime server register request!"
msg = json.dumps(service_provided)
client.send(msg.encode("utf-8"))
while True:
    print("-"*30)
    data = client.recv(1024).decode()
    if len(data) == 0:
        print("connection broken")
        break
    #print(client.__repr__())
    print("recv:",data)
    if "test alive" in data:
        client.send("alive".encode("utf-8"))
        #print("send:", "alive")
    else:
        request_info = json.loads(data)
        print("handling request:", request_info)
        url = "http://162.105.146.175:8000/stable_diffusion_v1"
        payload = json.dumps({
        "prompt": request_info["prompt"],
        "H": request_info["H"],
        "W": request_info["W"]
        })
        headers = {
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        #print(response.json())
        raw_image = response.json()['image']
        ans = {
            "image": raw_image
        }
        ans = json.dumps(ans).encode("utf-8")
        len_ans = len(ans)
        head_info = "0"*(10-len(str(len_ans))) + str(len_ans)
        buffer_size = 4096
        print(head_info)
        print(len_ans)
        #print(ans[:100])
        client.send(head_info.encode("utf-8"))
        temp_send_len = 0
        send_count = 0
        while(temp_send_len < len_ans):
            send_count += 1
            print("send_count:", send_count)
            print("len_ans:", len_ans, ", temp_send_len:", temp_send_len)
            if buffer_size < len_ans - temp_send_len:
                client.send(ans[temp_send_len:temp_send_len+buffer_size])
                temp_send_len += buffer_size
            else:
                client.send(ans[temp_send_len:len_ans])
                temp_send_len += len_ans - temp_send_len
    # time.sleep(2)
    # print("send:",data.decode())
        #if msg == "exit":
        #    break
client.close()
