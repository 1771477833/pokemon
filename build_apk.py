#!/usr/bin/env python3
"""使用 python-for-android 构建 APK"""

import os
import sys
import subprocess

# 设置环境变量
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-26'
os.environ['ANDROID_HOME'] = r'E:\Trea\Android'

def build_apk():
    print("开始构建 APK...")
    
    # 确保在项目目录
    os.chdir(r'e:\pokemon\baokemeng')
    
    # 使用 python-for-android 的 p4a 命令
    cmd = [
        sys.executable, '-m', 'pythonforandroid.toolchain',
        'apk',
        '--private', '.',
        '--package', 'org.pokemonbao',
        '--name', 'PokemonBAO',
        '--version', '0.1',
        '--requirements', 'python3,pygame',
        '--arch', 'armeabi-v7a',
        '--arch', 'arm64-v8a',
        '--android-api', '33',
        '--ndk-api', '21',
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("APK 构建成功！")
        print("标准输出:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e.returncode}")
        print("错误输出:", e.stderr)
        print("标准输出:", e.stdout)
        sys.exit(1)

if __name__ == '__main__':
    build_apk()
