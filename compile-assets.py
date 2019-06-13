#coding: utf-8
# 编译材质的脚本，将 input 目录下的脚本拷贝至 output 目录下
# usage: <source>
import sys
import os
import argparse
import subprocess
import re
import shutil


def check_need_update(input, output, name):
    """
    判断 output 文件夹下的 asset 是否需要更新
    """
    output_path = os.path.join(output, name)
    # 如果输出文件不存在，认为需要构建文件
    if not os.path.exists(output_path):
        return True
    input_path = os.path.join(input, name)
    # 比较两者的时间
    return os.path.getmtime(input_path) > os.path.getmtime(output_path)


# 编译 shader 的脚本
def compile_shader(input, output, name):
    """
    input: 输入文件夹
    output: 输出文件夹
    name: 文件名
    """
    # 输出文件的绝对路径
    path = os.path.join(output, name)

    # 检查文件夹是否存在，如若不存在，则新建一个路径
    path_dir = os.path.dirname(path)
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

    args = {
        "output": path.replace("glsl", "spv"),
        "input": os.path.join(input, name)
    }
    # 比较一下二者最后的修改时间
    if os.path.exists(args["output"]) and os.path.getmtime(args["output"]) > os.path.getmtime(args["input"]):
        return

    # 编译 shader
    cmd = "glslangValidator.exe -V -o {output} {input}".format(**args)
    result = subprocess.getstatusoutput(cmd)
    # 根据 glslangValidator 执行的结果来打印日志信息
    if result[0] == 0:
        print("compile shader: {}".format(name))
    else:
        print("compile failed: {}".format(result[1]))


def copy_asset(input, output, name):
    """
    复制资源
    """
    if not check_need_update(input, output, name):
        return
    # 输出文件的绝对路径
    path = os.path.join(output, name)

    # 检查文件夹是否存在，如若不存在，则新建一个路径
    path_dir = os.path.dirname(path)
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

    print("copy file: {}".format(name))
    shutil.copyfile(os.path.join(input, name), path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str,
                        help="input directory", dest="input")
    parser.add_argument("--output", type=str,
                        help="output directory", dest="output")
    args = parser.parse_args(sys.argv[1:])
    # compile(".", "../Assets/", __file__)
    for root, dirs, files in os.walk(args.input, topdown=False):
        for name in files:
            # 源文件的绝对路径
            source = os.path.abspath(os.path.join(root, name))
            # 在输入文件夹下的相对路径
            source = os.path.relpath(source, args.input)
            # 处理以 glsl 结尾的文件
            if re.match(".*glsl$", source):
                compile_shader(args.input, args.output, source)
                continue
            # 复制 asset
            if re.match(".*(png|glb|jpeg|ttf)$", source):
                copy_asset(args.input, args.output, source)
                continue
