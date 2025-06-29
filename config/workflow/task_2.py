
# -*- coding: utf-8 -*-
import sys
import os
import asyncio

# 添加父目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.append('/home/pi/xlab-bot/xlab/components/')
from klipper_basic import Robot
from io_control import IOController
from log_manage import robot_logger


async def workflow_A():
    robot = Robot()
    io = IOController()
    # 调用 firmware_restart 方法
    print("---单盘任务启动---")
    
    state = await robot.check_klippy_state()
    if state:
    # 调用 home 方法
        print("---homing---")
        await robot.home()
        
        print("---homing end---")
       
        # await robot.task_decap_aspirate(8, 6, 1, 1)
        await robot.task_decap_aspirate(8, 6, 1, 2)
        await robot.task_decap_aspirate(8, 6, 1, 3)
        await robot.task_decap_aspirate(8, 6, 1, 4)
        
        await robot.task_decap_aspirate(8, 6, 2, 1)
        await robot.task_decap_aspirate(8, 6, 2, 2)
        await robot.task_decap_aspirate(8, 6, 2, 3)
        await robot.task_decap_aspirate(8, 6, 2, 4)
        
        
        await robot.mov_parking_pos()
    
       
        print("---单盘任务完成---")
    
    
if __name__ == "__main__":
    asyncio.run(workflow_A())




