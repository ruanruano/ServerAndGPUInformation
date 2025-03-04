from flask import Flask, jsonify,render_template
from datetime import datetime
from flask_cors import CORS
import threading
import paramiko
import json
import time

#region 全局

app = Flask(__name__)
CORS(app)
port = 15002
server_list_path = '/media/disk2/rzp/server/tool_checkgpusweb/serverList.json'
data_list_lock = threading.Lock()
check_interval = 2
# 共享list
data_dict = dict()

#endregion

#region 接口

# 测试用
@app.route('/')
def hello():
    # return 'hi. —— CheckGPUsWeb'
    return 'hi. —— CheckGPUsWeb'

@app.route('/all_data', methods=['GET'])
def get_data():
    return jsonify(get_all_data())

# 开始连接服务器
def connect_server():
    pass

#endregion
import json

import json

# def get_gpus_info(client, timeout, info_list: list = None):
#     try:
#         # 获取 GPU 信息
#         cmd = (
#             'nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free,'
#             'utilization.gpu,utilization.memory,temperature.gpu --format=csv'
#         )
#         stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
#         output = stdout.read().decode()
#         output = output.split('\n')

#         # 解析 GPU 信息 -----------------------------
#         start_idx = 0
#         for i in range(len(output)):
#             if output[i].startswith('index'):
#                 start_idx = i + 1
#                 break
#         output = output[start_idx:-1]

#         gpu_results = []
#         for data in output:
#             data_list = data.split(', ')
#             idx = int(data_list[0])
#             gpu_name = data_list[1]
#             total_mem = int(data_list[2].split(' ')[0])
#             used_mem = int(data_list[3].split(' ')[0])
#             free_mem = int(data_list[4].split(' ')[0])
#             util_gpu = int(data_list[5].split(' ')[0])
#             util_mem = int(data_list[6].split(' ')[0])
#             temperature = int(data_list[7])

#             if gpu_name.startswith('NVIDIA '):
#                 gpu_name = gpu_name[7:]
#             if gpu_name.startswith('GeForce '):
#                 gpu_name = gpu_name[8:]

#             gpu_results.append({
#                 'idx': idx,
#                 'gpu_name': gpu_name,
#                 'total_mem': total_mem,
#                 'used_mem': used_mem,
#                 'free_mem': free_mem,
#                 'util_gpu': util_gpu,
#                 'util_mem': util_mem,
#                 'temperature': temperature,
#                 'users': {}
#             })

#         # 获取用户和显存信息
#         gpustat_cmd = 'gpustat --json'
#         stdin, stdout, stderr = client.exec_command(gpustat_cmd, timeout=timeout)
#         gpustat_output = stdout.read().decode()
        
#         # 确保 gpustat 输出不是空的
#         if not gpustat_output:
#             raise ValueError("gpustat did not return any output.")

#         gpustat_info = json.loads(gpustat_output)

#         # 确保解析的 gpustat 信息格式正确
#         if 'gpus' not in gpustat_info:
#             raise ValueError("Parsed gpustat info does not contain 'gpus' key.")

#         # 解析进程信息 -----------------------------
#         for gpu in gpustat_info['gpus']:
#             idx = gpu['index']
#             processes = gpu.get('processes', [])  # 使用 get() 方法避免 KeyError
#             for process in processes:
#                 username = process['username']
#                 memory_used = process['gpu_memory_usage']  # 占用的显存
#                 # 找到对应的 GPU，将用户及其显存使用情况记录下来
#                 for gpu_result in gpu_results:
#                     if gpu_result['idx'] == idx:
#                         if username not in gpu_result['users']:
#                             gpu_result['users'][username] = 0
#                         gpu_result['users'][username] += memory_used

#         return gpu_results
#     except Exception as e:
#         if info_list is not None:
#             info_list.append(f'gpus: {e}')
#         return None

import json

def get_gpus_info(client, timeout, info_list: list = None):
    try:
        # 获取 GPU 信息
        cmd = (
            'nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free,'
            'utilization.gpu,utilization.memory,temperature.gpu --format=csv'
        )
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        output = stdout.read().decode()
        output = output.split('\n')

        # 解析 GPU 信息 -----------------------------
        start_idx = 0
        for i in range(len(output)):
            if output[i].startswith('index'):
                start_idx = i + 1
                break
        output = output[start_idx:-1]

        gpu_results = []
        for data in output:
            data_list = data.split(', ')
            idx = int(data_list[0])
            gpu_name = data_list[1]
            total_mem = int(data_list[2].split(' ')[0])
            used_mem = int(data_list[3].split(' ')[0])
            free_mem = int(data_list[4].split(' ')[0])
            util_gpu = int(data_list[5].split(' ')[0])
            util_mem = int(data_list[6].split(' ')[0])
            temperature = int(data_list[7])

            # 简化 GPU 名称
            if gpu_name.startswith('NVIDIA '):
                gpu_name = gpu_name[7:]
            if gpu_name.startswith('GeForce '):
                gpu_name = gpu_name[8:]

            gpu_results.append({
                'idx': idx,
                'gpu_name': gpu_name,
                'total_mem': total_mem,
                'used_mem': used_mem,
                'free_mem': free_mem,
                'util_gpu': util_gpu,
                'util_mem': util_mem,
                'temperature': temperature,
                'users': {}
            })

        # 获取用户和显存信息
        gpustat_cmd = 'gpustat --json'
        stdin, stdout, stderr = client.exec_command(gpustat_cmd, timeout=timeout)
        gpustat_output = stdout.read().decode()

        # 确保 gpustat 输出不是空的
        if not gpustat_output:
            raise ValueError("gpustat did not return any output.")

        gpustat_info = json.loads(gpustat_output)

        # 确保解析的 gpustat 信息格式正确
        if 'gpus' not in gpustat_info:
            raise ValueError("Parsed gpustat info does not contain 'gpus' key.")

        # 解析进程信息 -----------------------------
        for gpu in gpustat_info['gpus']:
            idx = gpu['index']
            processes = gpu.get('processes', [])  # 使用 get() 方法避免 KeyError
            for process in processes:
                username = process['username']
                gpu_memory_usage = process['gpu_memory_usage']  # 占用的显存
                # 找到对应的 GPU，将用户及其显存使用情况记录下来
                for gpu_result in gpu_results:
                    if gpu_result['idx'] == idx:
                        if username not in gpu_result['users']:
                            gpu_result['users'][username] = 0
                        gpu_result['users'][username] += gpu_memory_usage

        return gpu_results
    except Exception as e:
        if info_list is not None:
            info_list.append(f'gpus: {e}')
        return None



def get_storage_info(client, timeout, path_list, info_list:list=None):
    if info_list is None:
        info_list = []
        
    result = []
    for target_path in path_list:
        try:
            stdin, stdout, stderr = client.exec_command(f'df {target_path} | grep \'{target_path}\'', timeout=timeout)
            output = stdout.read().decode()
            if not output:
                info_list.append(f"No storage info found for {target_path}")
                continue
                
            data = output.split()
            if len(data) < 4:
                info_list.append(f"Unexpected output format for {target_path}: {output}")
                continue
                
            tmp_res = {
                "path": target_path,
                "total": int(data[1]),
                "available": int(data[3])
            }
            result.append(tmp_res)
            
        except Exception as e:
            info_list.append(f'Error retrieving storage info for {target_path}: {e}')
    
    return result if result else None


def get_memory_info(client, timeout, info_list:list=None):
    try:
        stdin, stdout, stderr = client.exec_command('free', timeout=timeout)
        output = stdout.read().decode().split('\n')[1]
        if output == "":
            return None
        data = output.split()
        result = {
            "total": int(data[1]),
            "used": int(data[2])
        }

        return result
    except Exception as e:
        if info_list is not None:
            info_list.append(f'memory: {e}')
        return None

def get_network_info(client, timeout, interface_name, info_list:list=None):
    try:
        if interface_name is None:
            return None
        stdin, stdout, stderr = client.exec_command(f'ifstat -i {interface_name} 0.1 1', timeout=timeout)
        output = stdout.read().decode().split('\n')[2]
        data = output.split()
        result = {
            "in": float(data[0]),
            "out": float(data[1])
        }
        return result
    except Exception as e:
        if info_list is not None:
            info_list.append(f'network: {e}')
        return None

# 持续获取一个服务器的信息
def keep_check_one(server: dict, shared_data_list: dict, server_title: str, interval: float, re_connect_time: float=5):
    # 处理一下需要检查的存储空间路径
    if not 'storage_list' in server:
        server['storage_list'] = []
    if not '/' in server['storage_list']:
        server['storage_list'].insert(0, '/')

    re_try_count = 0
    # 循环连接
    while True:
        try:
            # 建立SSH连接
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(server['ip'], port=server['port'], username=server['username'], password=server.get('password', None), key_filename=server.get('key_filename', None), timeout=interval*3)
            cmd = 'nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu,utilization.memory,temperature.gpu --format=csv'

            shared_data_list[server_title]['err_info'] = None
            re_try_count = 0

            # 循环检测
            keep_run = True
            while keep_run:
                try:
                    error_info_list = []
                    # gpu 信息
                    gpu_info = get_gpus_info(client, interval*3, info_list=error_info_list)
                    # 存储空间信息
                    storage_info = get_storage_info(client, interval*3, server['storage_list'], info_list=error_info_list)
                    # 内存信息
                    memory_info = get_memory_info(client, interval*3, info_list=error_info_list)
                    # 网络信息
                    network_info = get_network_info(client, interval*3, server.get('network_interface_name', None), info_list=error_info_list)

                    # 记录信息
                    with data_list_lock:
                        shared_data_list[server_title]['gpu_info_list'] = gpu_info
                        shared_data_list[server_title]['storage_info_list'] = storage_info
                        shared_data_list[server_title]['memory_info'] = memory_info
                        shared_data_list[server_title]['network_info'] = network_info
                        shared_data_list[server_title]['updated'] = True
                        shared_data_list[server_title]['maxGPU'] = len(gpu_info)
                        if len(error_info_list) > 0:
                            shared_data_list[server_title]['err_info'] = '\n'.join(error_info_list)

                except Exception as e:
                    keep_run = False
                    shared_data_list[server_title]['err_info'] = f'{e}'
                    if 'gpu_info_list' in shared_data_list[server_title]:
                        shared_data_list[server_title].pop('gpu_info_list')

                time.sleep(interval)

            # 关闭连接
            client.close()
        except Exception as e:
            shared_data_list[server_title]['err_info'] = f'retry:{re_try_count}, {e}'
        time.sleep(re_connect_time)
        re_try_count += 1

# 获取所有的服务器数据
def get_all_data():
    return filter_data(list(data_dict.keys()))

# 根据key过滤所需的服务器数据
def filter_data(title_list: list):
    result = dict()
    server_data = dict()
    for title in title_list:
        server_data[title] = {}
        # 不存在该title的数据
        if title not in data_dict:
            server_data[title]['err_info'] = f'title \'{title}\' not exist!'
            continue

        # 记录数据 ----------------------------------------------------
        data_updated = data_dict[title].get('updated', False)
        # 是否更新
        server_data[title]['updated'] = data_updated
        # 报错信息
        err_info = data_dict[title].get('err_info', None)
        if err_info is not None:
            server_data[title]['err_info'] = err_info
        # 显卡
        gpu_info_list = data_dict[title].get('gpu_info_list', None)
        if gpu_info_list is not None:
            server_data[title]['gpu_info_list'] = gpu_info_list
        # 硬盘
        storage_info_list = data_dict[title].get('storage_info_list', None)
        if storage_info_list is not None:
            server_data[title]['storage_info_list'] = storage_info_list
        # 内存
        memory_info = data_dict[title].get('memory_info', None)
        if memory_info is not None:
            server_data[title]['memory_info'] = memory_info
        # 网络
        network_info = data_dict[title].get('network_info', None)
        if network_info is not None:
            server_data[title]['network_info'] = network_info

    result['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result['server_data'] = server_data
    return result

def start_connect():
    # 加载json
    with open(server_list_path, 'r') as f:
        server_list = json.load(f)

    global data_dict
    # 开启线程
    for i, server_data in enumerate(server_list):
        data_dict[server_data['title']] = {}
        data_dict[server_data['title']]['server_data'] = server_data
        thread = threading.Thread(target=keep_check_one, args=(server_data, data_dict, server_data['title'], check_interval))
        thread.daemon = True
        thread.start()

    print('start connect')

# 测试
def test():
    start_connect()
    app.run(debug=True, host='0.0.0.0', port=port)

if __name__ == '__main__':
    test()