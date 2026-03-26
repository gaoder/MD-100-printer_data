#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
液体回流任务脚本
用于执行液体回流操作（从培养基容器回流到培养皿储存容器）
泵旋转方向与填充相反
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


async def tube_backflow_workflow(volume: float):
    """
    液体回流工作流
    
    Args:
        volume: 回流体积（ml）
    
    Returns:
        bool: 是否成功
    """
    robot = Robot()
    
    try:
        robot_logger.info("=" * 70)
        robot_logger.info("开始液体回流任务")
        robot_logger.info(f"回流体积: {volume} ml")
        robot_logger.info("=" * 70)
        
        # 检查 Klipper 状态
        state = await robot.check_klippy_state()
        if not state:
            robot_logger.error("Klipper 未就绪，无法执行回流")
            print("ERROR: Klipper not ready")
            return False
        
        robot_logger.info("Klipper 状态检查通过")
        
        # 执行回流（反向旋转）
        robot_logger.info(f"开始回流液体，体积: {volume} ml（反向旋转）")
        print(f"开始回流液体，体积: {volume} ml")
        
        # 回流使用反向旋转，自动排到培养皿储存容器中
        result = await robot.backflow_tube(backflow_volume=volume)
        
        if result:
            robot_logger.info("✅ 液体回流完成")
            print("SUCCESS: Tube backflow completed")
            return True
        else:
            robot_logger.error("❌ 液体回流失败")
            print("ERROR: Tube backflow failed")
            return False
            
    except Exception as e:
        robot_logger.error(f"液体回流异常: {e}")
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
    parser = argparse.ArgumentParser(description='液体回流任务')
    parser.add_argument('--volume', type=float, help='回流体积（ml）')
    parser.add_argument('--config', type=str, help='配置文件路径（预留，当前未使用）')
    
    args = parser.parse_args()
    
    # 获取回流体积
    if args.volume is not None:
        volume = args.volume
        print(f"使用命令行指定的回流体积: {volume} ml")
    else:
        # 从配置文件读取默认值
        loader = ConfigLoader.get_instance()
        volume_raw = loader.get_variable('process_end_back_volume', default=10.0, namespace='robot')
        volume = float(volume_raw) if volume_raw is not None else 10.0
        print(f"使用配置文件默认回流体积: {volume} ml")
    
    # 验证体积
    if volume <= 0:
        print(f"ERROR: Invalid volume: {volume} ml")
        sys.exit(1)
    
    # 执行回流
    try:
        result = asyncio.run(tube_backflow_workflow(volume))
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n回流任务被用户中断")
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

