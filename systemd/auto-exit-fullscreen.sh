#!/bin/bash

pkill -f chromium
# 启动自动全屏服务
echo "关闭自动全屏服务..."
sudo systemctl stop auto-fullscreen.service

