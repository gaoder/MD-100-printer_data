#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管路填充任务脚本
用于执行管路填充操作（排空管路中的空气，填充培养基）
"""
import sys
import os
import asyncio
import argparse

# 添加父目录到模块搜索路径
sys.path.append('/home/pi/xlab-bot/xlab/components/')

from klipper_basic import Robot
from log_manage import robot_logger
from config_loader import ConfigLoader


async def tube_filling_workflow(volume: float):
    """
    管路填充工作流
    
    Args:
        volume: 填充体积（ml）
    
    Returns:
        bool: 是否成功
    """
    robot = Robot()
    
    try:
        robot_logger.info("=" * 70)
        robot_logger.info("开始管路填充任务")
        robot_logger.info(f"填充体积: {volume} ml")
        robot_logger.info("=" * 70)
        
        # 检查 Klipper 状态
        state = await robot.check_klippy_state()
        if not state:
            robot_logger.error("Klipper 未就绪，无法执行填充")
            print("ERROR: Klipper not ready")
            return False
        
        robot_logger.info("Klipper 状态检查通过")
        
        # 执行填充
        robot_logger.info(f"开始填充管路，体积: {volume} ml")
        print(f"开始填充管路，体积: {volume} ml")
        
        # 填充管路使用与清洗相同的泵操作，只是液体来源不同
        # 填充是从培养基容器抽液到管路中
        result = await robot.fill_tube(fill_volume=volume)
        
        if result:
            robot_logger.info("✅ 管路填充完成")
            print("SUCCESS: Tube filling completed")
            return True
        else:
            robot_logger.error("❌ 管路填充失败")
            print("ERROR: Tube filling failed")
            return False
            
    except Exception as e:
        robot_logger.error(f"管路填充异常: {e}")
        print(f"ERROR: {e}")
        import traceback
        robot_logger.error(traceback.format_exc())
        return False
    finally:
        # 确保资源清理
        try:
            await robot.close()
        except Exception:
            pass


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='管路填充任务')
    parser.add_argument('--volume', type=float, help='填充体积（ml）')
    parser.add_argument('--config', type=str, help='配置文件路径（预留，当前未使用）')
    
    args = parser.parse_args()
    
    # 获取填充体积
    if args.volume is not None:
        volume = args.volume
        print(f"使用命令行指定的填充体积: {volume} ml")
    else:
        # 从配置文件读取默认值
        loader = ConfigLoader.get_instance()
        volume_raw = loader.get_variable('tube_filling_volume', default=10.0, namespace='robot')
        volume = float(volume_raw) if volume_raw is not None else 10.0
        print(f"使用配置文件默认填充体积: {volume} ml")
    
    # 验证体积
    if volume <= 0:
        print(f"ERROR: Invalid volume: {volume} ml")
        sys.exit(1)
    
    # 执行填充
    try:
        result = asyncio.run(tube_filling_workflow(volume))
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n填充任务被用户中断")
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

