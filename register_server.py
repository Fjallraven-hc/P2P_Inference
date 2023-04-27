from socket import *
from multiprocessing import Process, Queue
import threading
import time
import json
from queue import Queue
import requests

register_server = socket(AF_INET,SOCK_STREAM)
#register_server.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
register_server.bind(('0.0.0.0',7777))
register_server.listen(5) # n为等待连接时可以最多挂起的连接个数

client_server = socket(AF_INET,SOCK_STREAM)
#client_server.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
client_server.bind(('0.0.0.0',6666))
client_server.listen(5) # n为等待连接时可以最多挂起的连接个数

# global variable for runtime_server
runtime_server_info = {}
client_request = Queue()

def runtime_server_talk(conn, runtime_server_addr):
    #若不用此句，客户端关闭时，服务端会因报错，停止
    try:
        print("-"*30)
        msg = conn.recv(1024)
        print(msg)
        print("receive register from :", runtime_server_addr, "message :", msg.decode())
        service_info = json.loads(msg.decode())
        conn.send("test alive".encode("utf-8"))
        msg = conn.recv(1024).decode()
        if msg == "alive":
            runtime_server_info[runtime_server_addr] = {
                "conn": conn,
                "addr": runtime_server_addr,
                "status": "alive",
                "service_info": service_info
            }
        for server in runtime_server_info:
            print(server)
        """if not msg:break
        conn.send(msg.upper())
        if msg.decode() == "exit":
            print("connection from", client_addr, "break")
            break"""
    except Exception:
        pass

class runtime_server:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
    
def register_runtime_server():
    print("开始等待Runtime Server注册...")
    global runtime_server_info
    while True:
        conn, client_addr=register_server.accept()
        # Compared to Thread, Process can not share socket
        # p=Process(target=talk,args=(conn,client_addr))
        temp_thread = threading.Thread(target=runtime_server_talk, args=(conn,client_addr))
        temp_thread.start()
        # temp_process = Process(target=talk, args=(conn,client_addr))
        # temp_process.start()

def test_alive_runtime_server():
    while True:
        time.sleep(10)
        for server in runtime_server_info:
            if runtime_server_info[server]["status"] == "alive":
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                try:
                    runtime_server_info[server]["conn"].send(f"test alive, time: {current_time}".encode("utf-8"))
                except BrokenPipeError:
                    runtime_server_info.pop(server)

def client_talk(conn, client_addr):
    # service : a json consists of all info
    #try:
    print("-"*30)
    msg = conn.recv(1024)
    print("receive service request from :", client_addr)
    print("service request: ", msg.decode())
    request_info = json.loads(msg.decode())
    # write the handle logic
    ans = bytes()
    for server in runtime_server_info:
        if request_info["service_type"] in runtime_server_info[server]["service_info"]:
            runtime_server_info[server]["conn"].send(msg)
            head_info = runtime_server_info[server]["conn"].recv(10)
            print("runtime server return data len:", int(head_info.decode()))
            # assume each side know buffer size is 4096
            buffer_size = 4096
            raw_data_len = int(head_info.decode())
            temp_recv_len = 0
            recv_count = 0
            while(temp_recv_len < raw_data_len):
                recv_count += 1
                print("recv_count:", recv_count)
                print("raw_data_len:", raw_data_len, ", temp_recv_len:", temp_recv_len)
                if 4096 < raw_data_len - temp_recv_len:
                    data = runtime_server_info[server]["conn"].recv(buffer_size)
                    ans += data
                    temp_recv_len += len(data)
                else:
                    data = runtime_server_info[server]["conn"].recv(raw_data_len - temp_recv_len)
                    ans += data
                    temp_recv_len += len(data)
            #ans = runtime_server_info[server]["conn"].recv(1000000)
            break
    default_ans = {
        "image": "this is a image"
    }
    print("client talk send bytes length:", len(ans))
    send_buffer_size = 5000
    conn.send(head_info)
    temp_send_len = 0
    send_count = 0
    while(temp_send_len < raw_data_len):
        send_count += 1
        print("send_count:", send_count)
        print("len_ans:", raw_data_len, ", temp_send_len:", temp_send_len)
        if send_buffer_size < raw_data_len - temp_send_len:
            conn.send(ans[temp_send_len:temp_send_len+send_buffer_size])
            temp_send_len += send_buffer_size
        else:
            conn.send(ans[temp_send_len:raw_data_len])
            temp_send_len += raw_data_len - temp_send_len
        #time.sleep(1)
        #test = conn.recv(7).decode()
        #print(test)
    print(ans[:100])
    conn.send(ans)
    print("respond service request to :", client_addr)
    #except Exception as e:
    #    print(e.__traceback__)
    #    print(f"try connecting with {client_addr} meets error!")
    #    pass

def collect_client_request():
    print("开始等待client request...")
    global runtime_server_info
    while True:
        conn, client_addr=client_server.accept()
        # Compared to Thread, Process can not share socket
        # p=Process(target=talk,args=(conn,client_addr))
        temp_thread = threading.Thread(target=client_talk, args=(conn,client_addr))
        temp_thread.start()
        # temp_process = Process(target=talk, args=(conn,client_addr))
        # temp_process.start()


if __name__ == '__main__':
    register_thread = threading.Thread(target=register_runtime_server)
    register_thread.start()
    #test_alive_thread = threading.Thread(target=test_alive_runtime_server)
    #test_alive_thread.start()
    client_thread = threading.Thread(target=collect_client_request)
    client_thread.start()

    # count = 0
    while True:
        pass
        # count += 1
        # conn, client_addr=register_server.accept()
        # p = threading.Thread(target=talk, args=(conn,client_addr))
        # Compared to Thread, Process can not share socket
        # p=Process(target=talk,args=(conn,client_addr))
        # p.start()
        # runtime_server_list.append(runtime_server(conn, client_addr))
        # print(runtime_server_list)
