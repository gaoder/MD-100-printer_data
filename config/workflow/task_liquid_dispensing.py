#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
液体加液任务脚本（用于液体校准）
用于执行液体加液操作，使用指定的速度和液体类型
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


async def liquid_dispensing_workflow(volume: float, speed_percentage: float = None, liquid_type: str = None, tube_spec: str = None):
    """
    液体加液工作流（用于液体校准）
    
    Args:
        volume: 加液体积（ml）
        speed_percentage: 泵速百分比（0-100，可选）
        liquid_type: 液体类型（可选）
        tube_spec: 泵管规格（可选）
    
    Returns:
        bool: 是否成功
    """
    robot = Robot()
    
    try:
        robot_logger.info("=" * 70)
        robot_logger.info("开始液体加液任务（液体校准）")
        robot_logger.info(f"加液体积: {volume} ml")
        if speed_percentage is not None:
            robot_logger.info(f"泵速百分比: {speed_percentage}%")
        if liquid_type is not None:
            robot_logger.info(f"液体类型: {liquid_type}")
        if tube_spec is not None:
            robot_logger.info(f"泵管规格: {tube_spec}")
        robot_logger.info("=" * 70)
        
        # 检查 Klipper 状态
        state = await robot.check_klippy_state()
        if not state:
            robot_logger.error("Klipper 未就绪，无法执行加液")
            print("ERROR: Klipper not ready")
            return False
        
        robot_logger.info("Klipper 状态检查通过")
        
        # 如果未指定速度，从配置读取默认值（80%）
        if speed_percentage is None:
            loader = ConfigLoader.get_instance()
            speed_percentage = 80.0
            robot_logger.info(f"使用默认泵速百分比: {speed_percentage}%")
        
        # 如果未指定液体类型，使用默认值
        if liquid_type is None:
            liquid_type = 'media_standard'
            robot_logger.info(f"使用默认液体类型: {liquid_type}")
        
        # 执行加液
        robot_logger.info(f"开始加液，体积: {volume} ml, 泵速: {speed_percentage}%")
        print(f"开始加液，体积: {volume} ml, 泵速: {speed_percentage}%")
        
        result = await robot.dispense_liquid(
            volume=volume,
            speed_percentage=speed_percentage,
            liquid_type=liquid_type,
            tube_spec=tube_spec
        )
        
        if result:
            robot_logger.info("✅ 液体加液完成")
            print("SUCCESS: Liquid dispensing completed")
            return True
        else:
            robot_logger.error("❌ 液体加液失败")
            print("ERROR: Liquid dispensing failed")
            return False
            
    except Exception as e:
        robot_logger.error(f"液体加液异常: {e}")
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
    parser = argparse.ArgumentParser(description='液体加液任务（液体校准）')
    parser.add_argument('--volume', type=float, required=True, help='加液体积（ml）')
    parser.add_argument('--speed', type=float, help='泵速百分比（0-100）')
    parser.add_argument('--liquid-type', type=str, help='液体类型')
    parser.add_argument('--tube-spec', type=str, help='泵管规格ID')
    parser.add_argument('--config', type=str, help='配置文件路径（预留，当前未使用）')
    
    args = parser.parse_args()
    
    # 获取加液体积（必需）
    volume = args.volume
    if volume <= 0:
        print(f"ERROR: Invalid volume: {volume} ml")
        sys.exit(1)
    
    # 获取可选参数
    speed_percentage = args.speed
    liquid_type = args.liquid_type
    tube_spec = args.tube_spec
    
    print(f"使用命令行参数:")
    print(f"  加液体积: {volume} ml")
    if speed_percentage is not None:
        print(f"  泵速百分比: {speed_percentage}%")
    if liquid_type is not None:
        print(f"  液体类型: {liquid_type}")
    if tube_spec is not None:
        print(f"  泵管规格: {tube_spec}")
    
    # 执行加液
    try:
        result = asyncio.run(liquid_dispensing_workflow(volume, speed_percentage, liquid_type, tube_spec))
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n加液任务被用户中断")
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

