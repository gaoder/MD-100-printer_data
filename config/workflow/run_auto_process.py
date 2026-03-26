#!/usr/bin/env python3
"""
自动流程执行脚本
从命令行参数或环境变量读取流程参数，然后执行 auto_media_filling()
"""

import sys
import asyncio
import json
from pathlib import Path

# 添加组件路径
sys.path.insert(0, '/home/pi/xlab-bot/xlab/components')

from klipper_basic import Robot


async def main():
    """
    主函数：读取参数并执行流程
    
    注意：本脚本已不再由前端调用（已改为直接使用 SystemController 的 Robot 实例）
    保留此脚本仅用作独立测试工具
    """
    robot = None  # 用于 finally 块清理资源
    try:
        # 从命令行参数读取流程参数（JSON 格式）
        if len(sys.argv) < 2:
            print("错误: 缺少流程参数", file=sys.stderr)
            print(f"使用方法: {sys.argv[0]} '<json_params>'", file=sys.stderr)
            return False
        
        # 解析 JSON 参数
        params_json = sys.argv[1]
        params = json.loads(params_json)
        
        print(f"=" * 70)
        print(f"  启动自动流程（独立测试模式）")
        print(f"=" * 70)
        print(f"流程参数:")
        print(f"  培养皿数量: {params.get('dish_number')}")
        print(f"  加液体积: {params.get('pump_volume')} ml")
        print(f"  泵速: {params.get('pump_speed')}%")
        print(f"  液体类型: {params.get('liquid_type')}")
        print(f"  管子规格: {params.get('tube_spec')}")
        print(f"=" * 70)
        print(f"⚠️  注意: 此脚本创建新的 Robot 实例，可能与主程序冲突")
        print(f"=" * 70)
        
        # 创建 Robot 实例
        robot = Robot()
        
        # 执行流程
        result = await robot.auto_media_filling(**params)
        
        if result:
            print(f"\n✅ 流程执行成功")
            return True
        else:
            print(f"\n❌ 流程执行失败")
            return False
        
    except json.JSONDecodeError as e:
        print(f"❌ 参数解析失败: {e}", file=sys.stderr)
        return False
    except Exception as e:
        # 检查是否是紧急停止异常
        if e.__class__.__name__ == 'EmergencyStopException':
            print(f"\n⛔ 流程因紧急停止而中止", file=sys.stderr)
            print(f"   急停原因: {e}", file=sys.stderr)
            return False
        
        # 其他异常
        print(f"❌ 流程异常: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 🔑 关键：清理 CAN socket 资源（方案1：资源清理）
        if robot:
            try:
                await robot.close()
                print(f"\n🧹 资源已清理（CAN socket 已关闭）")
                # 额外延迟，确保操作系统完全释放资源
                await asyncio.sleep(0.5)
            except Exception as cleanup_error:
                print(f"⚠️  资源清理失败: {cleanup_error}", file=sys.stderr)


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)

