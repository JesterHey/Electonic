import subprocess
import os
import sys

def main():
    # 确保路径正确
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pyverilog_script = os.path.join(current_dir, "pyverilog", "examples", "example_parser.py")
    verilog_file = os.path.join(current_dir, "Electonic", "examples", "m1.v")
    
    # 检查文件是否存在
    if not os.path.exists(pyverilog_script):
        print(f"错误：PyVerilog 示例脚本 {pyverilog_script} 未找到！")
        return
    if not os.path.exists(verilog_file):
        print(f"错误：Verilog 文件 {verilog_file} 未找到！")
        return
    
    # 调用命令行并生成 AST
    try:
        subprocess.run(
            [sys.executable, pyverilog_script, verilog_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败：{e}")
        print("错误输出：", e.stderr.decode())

if __name__ == "__main__":
    main()