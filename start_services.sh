#!/bin/bash
# 确保脚本在发生错误时终止执行
set -e

# 检查或创建 screen 会话
if ! screen -list | grep -q "218278.server"; then
    echo "screen 会话 218278.server 不存在，正在创建并启动 Python 应用..."
    screen -dmS 218278.server bash -c 'python /media/disk2/rzp/server/tool_checkgpusweb/app.py; exec bash'
else
    echo "screen 会话 218278.server 已存在，正在其中启动 Python 应用..."
    screen -S 218278.server -p 0 -X stuff $'python /media/disk2/rzp/server/tool_checkgpusweb/app.py\n'
fi

# 等待确保 Python 应用已经启动
echo "等待 Python 应用启动..."
sleep 5

# 启动 Nginx Docker 容器
echo "启动 Nginx Docker 容器..."
docker run -d -p 8080:80 -v /media/disk2/rzp/server/tool_checkgpusweb:/usr/share/nginx/html --name nginx_gpus nginx:latest

echo "所有服务已经启动完成."
