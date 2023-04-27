# run on local
import time
import json
import socket
import base64

def save_encoded_image(b64_image: str, output_path: str):
    """
    Save the given image to the given output path.
    """
    with open(output_path, "wb") as image_file:
        image_file.write(base64.b64decode(b64_image))

client = socket.socket()
# connect to server
client.connect(('162.105.146.176', 6666))
service_info = {
    "service_type": "stable_diffusion_txt2image",
    "prompt": "Hawaii surfing",
    "H": 512,
    "W": 512
}
# msg = "this is a client service request!"
msg = json.dumps(service_info)
client.send(msg.encode("utf-8"))

print("-"*30)
head_info = client.recv(10)
buffer_size = 5000 # configurable
raw_data_len = int(head_info.decode())
temp_recv_len = 0
recv_count = 0
ans = bytes()
while(temp_recv_len < raw_data_len):
    recv_count += 1
    print("recv_count:", recv_count)
    print("raw_data_len:", raw_data_len, ", temp_recv_len:", temp_recv_len)
    if buffer_size < raw_data_len - temp_recv_len:
        data = client.recv(buffer_size)
        print("recv data size:", len(data))
        ans += data
        temp_recv_len += len(data)
    else:
        data = client.recv(raw_data_len - temp_recv_len)
        print("recv data size:", len(data))
        ans += data
        temp_recv_len += len(data)
    print("current data length:", len(ans))
    #time.sleep(1)
print("recv data length:", len(ans))
#print(ans[:100])
save_encoded_image(json.loads(ans)['image'], "Hawai_surfing.png")
client.close()
