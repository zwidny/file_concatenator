#!/usr/bin/env python3
"""
命令行接口模块
"""

import os
import argparse
from .core import DirectoryToMarkdown


def main():
    """主命令行函数"""
    parser = argparse.ArgumentParser(
        description="将目录结构及内容转换为Markdown文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  dir-to-md ./skills/pdf/                    # 基本用法
  dir-to-md ./skills/pdf/ -o output.md       # 指定输出文件名
  dir-to-md ./project/ --ignore "*.log"      # 忽略日志文件
  dir-to-md ./docs/ --ignore-file .gitignore # 使用.gitignore作为忽略文件
  dir-to-md ./data/ --no-markitdown          # 禁用markitdown转换
        """,
    )

    parser.add_argument("directory", help="要处理的目录路径")
    parser.add_argument("-o", "--output", help="输出文件名（可选）")
    parser.add_argument("--no-markitdown", action="store_true", help="不使用markitdown转换非文本文件")
    parser.add_argument("--ignore", action="append", default=[], help="忽略模式（支持通配符），可多次使用")
    parser.add_argument("--ignore-file", default=None, help="忽略规则文件路径（如.gitignore）")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")

    args = parser.parse_args()

    # 设置详细模式
    if args.verbose:
        import logging

        logging.basicConfig(level=logging.DEBUG)

    # 确定输出文件名
    if args.output:
        output_file = args.output
    else:
        dir_name = args.directory.rstrip("/\\")
        dir_name = os.path.basename(dir_name) if os.path.basename(dir_name) else dir_name
        output_file = f"{dir_name.replace('/', '_').replace('\\', '_')}_combined.md"

    # 创建处理器实例
    processor = DirectoryToMarkdown(
        use_markitdown=not args.no_markitdown, ignore_patterns=args.ignore, ignore_file=args.ignore_file, verbose=args.verbose
    )

    # 处理目录
    success = processor.process(args.directory, output_file)

    if success:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
