#!/bin/bash

# 等待前端服务完全启动
echo "等待前端服务启动..."
max_attempts=60  # 最多等待60次（2分钟）
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo "前端服务已就绪，启动全屏模式"
        break
    fi
    
    echo "等待前端服务... (尝试 $((attempt + 1))/$max_attempts)"
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "警告：前端服务启动超时，但仍尝试启动全屏模式"
fi

# 额外等待2秒确保服务完全稳定
sleep 2

chromium-browser --kiosk --noerrdialogs --disable-infobars --no-first-run --start-maximized http://localhost:8080/