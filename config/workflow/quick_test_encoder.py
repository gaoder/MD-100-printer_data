#!/usr/bin/env python3
"""
快速测试编码器置零功能
用于验证方案2是否解决了 CAN socket 冲突问题
"""

import sys
import asyncio
from pathlib import Path

# 添加组件路径
sys.path.insert(0, '/home/pi/xlab-bot/xlab/components')

from klipper_basic import Robot


async def test_encoder_multiple_times(rounds=5):
    """
    测试多次 Home 操作，验证编码器置零稳定性
    
    Args:
        rounds: 测试轮数
    """
    print("=" * 70)
    print("  编码器置零稳定性测试")
    print("=" * 70)
    print(f"测试轮数: {rounds}")
    print("=" * 70)
    
    success_count = 0
    fail_count = 0
    
    for i in range(1, rounds + 1):
        print(f"\n🔄 第 {i}/{rounds} 轮测试")
        print("-" * 70)
        
        robot = None
        try:
            # 创建 Robot 实例
            robot = Robot()
            print("✅ Robot 实例创建成功")
            
            # 执行 Home 操作
            await robot.home()
            
            print(f"✅ 第 {i} 轮测试成功")
            success_count += 1
            
        except Exception as e:
            print(f"❌ 第 {i} 轮测试失败: {e}")
            fail_count += 1
            import traceback
            traceback.print_exc()
        finally:
            # 清理资源
            if robot:
                try:
                    await robot.close()
                    print("🧹 资源已清理")
                    # 延迟，确保资源完全释放
                    await asyncio.sleep(1.0)
                except Exception as cleanup_err:
                    print(f"⚠️  资源清理失败: {cleanup_err}")
        
        # 轮次间隔
        if i < rounds:
            print(f"⏱️  等待 2 秒后开始下一轮...")
            await asyncio.sleep(2.0)
    
    # 输出统计
    print("\n" + "=" * 70)
    print("  测试结果统计")
    print("=" * 70)
    print(f"总轮数: {rounds}")
    print(f"成功: {success_count} ✅")
    print(f"失败: {fail_count} ❌")
    print(f"成功率: {success_count / rounds * 100:.1f}%")
    print("=" * 70)
    
    if fail_count == 0:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，请检查日志")
        return False


async def test_encoder_after_delay():
    """
    测试延迟后的编码器置零（模拟流程运行后的场景）
    """
    print("=" * 70)
    print("  模拟流程运行后的编码器置零测试")
    print("=" * 70)
    
    # 第一次测试
    print("\n📍 第1次测试: 立即执行")
    robot1 = None
    try:
        robot1 = Robot()
        await robot1.home()
        print("✅ 第1次 Home 成功")
    except Exception as e:
        print(f"❌ 第1次 Home 失败: {e}")
        return False
    finally:
        if robot1:
            await robot1.close()
            print("🧹 第1个实例已清理")
    
    # 等待一段时间（模拟流程运行）
    print("\n⏱️  等待 5 秒（模拟流程运行）...")
    await asyncio.sleep(5.0)
    
    # 第二次测试
    print("\n📍 第2次测试: 延迟后执行")
    robot2 = None
    try:
        robot2 = Robot()
        await robot2.home()
        print("✅ 第2次 Home 成功")
        print("\n🎉 测试通过：流程运行后编码器置零正常！")
        return True
    except Exception as e:
        print(f"❌ 第2次 Home 失败: {e}")
        print(f"⚠️  这表明 CAN socket 冲突问题可能仍然存在")
        return False
    finally:
        if robot2:
            await robot2.close()
            print("🧹 第2个实例已清理")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--delay':
        # 延迟测试模式
        result = asyncio.run(test_encoder_after_delay())
    else:
        # 默认：多轮测试模式
        rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 5
        result = asyncio.run(test_encoder_multiple_times(rounds))
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    print("""
使用方法:
  1. 多轮测试（默认5轮）：python3 quick_test_encoder.py
  2. 指定轮数：python3 quick_test_encoder.py 10
  3. 延迟测试：python3 quick_test_encoder.py --delay
    """)
    main()

