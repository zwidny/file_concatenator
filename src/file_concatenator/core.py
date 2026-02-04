"""
核心处理逻辑
"""

import os
import re
import fnmatch
from datetime import datetime
from typing import List, Optional, Dict, Any


class DirectoryToMarkdown:
    """目录转Markdown处理器"""

    def __init__(
        self,
        use_markitdown: bool = True,
        ignore_patterns: Optional[List[str]] = None,
        ignore_file: Optional[str] = None,
        verbose: bool = False,
    ):
        self.use_markitdown = use_markitdown
        self.ignore_patterns = ignore_patterns or []
        self.ignore_file = ignore_file
        self.verbose = verbose

        # 初始化 markitdown
        self.markitdown_instance = None
        self.markitdown_available = False

        if self.use_markitdown:
            self._init_markitdown()

    def _init_markitdown(self):
        """初始化 markitdown"""
        try:
            from markitdown import MarkItDown

            self.markitdown_instance = MarkItDown(enable_plugins=False)
            self.markitdown_available = True
            if self.verbose:
                print("✓ markitdown已成功加载")
        except ImportError:
            if self.verbose:
                print("⚠ markitdown未安装，PDF等文件将无法自动转换")
                print("  使用: pip install markitdown 进行安装")
            self.markitdown_available = False
        except Exception as e:
            if self.verbose:
                print(f"⚠ 加载markitdown时出错: {str(e)}")
            self.markitdown_available = False

    def process(self, input_dir: str, output_file: str) -> bool:
        """处理目录并生成Markdown文件"""
        input_dir = os.path.normpath(input_dir)

        if not os.path.exists(input_dir):
            print(f"✗ 错误: 目录 '{input_dir}' 不存在")
            return False

        # 加载忽略模式
        all_ignore_patterns = self._load_ignore_patterns()
        all_ignore_patterns.append(output_file)

        print(f"📁 处理目录: {input_dir}")
        print(f"📄 输出文件: {output_file}")

        # 统计信息
        stats = self._init_stats()

        try:
            with open(output_file, "w", encoding="utf-8") as md_file:
                # 写入头部信息
                self._write_header(md_file, input_dir)

                # 生成目录树
                self._write_directory_tree(md_file, input_dir, all_ignore_patterns)

                # 处理所有文件
                self._process_files(md_file, input_dir, all_ignore_patterns, stats)

                # 写入统计信息
                self._write_statistics(md_file, stats)

            # 打印统计信息
            self._print_statistics(stats, output_file)
            return True

        except Exception as e:
            print(f"✗ 处理过程中出错: {str(e)}")
            if self.verbose:
                import traceback

                traceback.print_exc()
            return False

    def _load_ignore_patterns(self) -> List[str]:
        """加载所有忽略模式"""
        all_ignore_patterns = []

        # 从文件加载
        if self.ignore_file and os.path.exists(self.ignore_file):
            all_ignore_patterns.extend(self._load_ignore_file(self.ignore_file))

        # 添加命令行指定的忽略模式
        all_ignore_patterns.extend(self.ignore_patterns)

        # 添加默认忽略模式
        default_patterns = [".git", "__pycache__", ".DS_Store", "*.pyc", "*.pyo"]
        for pattern in default_patterns:
            if pattern not in all_ignore_patterns:
                all_ignore_patterns.append(pattern)

        return all_ignore_patterns

    def _load_ignore_file(self, filepath: str) -> List[str]:
        """从文件加载忽略模式"""
        patterns = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception as e:
            if self.verbose:
                print(f"✗ 读取忽略文件时出错: {str(e)}")
        return patterns

    def _init_stats(self) -> Dict[str, Any]:
        """初始化统计信息"""
        return {
            "total_dirs": 0,
            "total_files": 0,
            "text_files": 0,
            "converted_files": 0,
            "ignored_paths": 0,
            "failed_files": 0,
            "start_time": datetime.now(),
        }

    def _write_header(self, md_file, input_dir: str):
        """写入文件头部信息"""
        dir_name = os.path.basename(input_dir) if os.path.basename(input_dir) else input_dir
        md_file.write(f"# 📁 目录: {dir_name}\n\n")
        md_file.write(f"**原始路径**: `{os.path.abspath(input_dir)}`  \n")
        md_file.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n\n")

    def _write_directory_tree(self, md_file, input_dir: str, ignore_patterns: List[str]):
        """写入目录树"""
        md_file.write("## 📊 目录结构\n\n")
        md_file.write("```\n")

        tree_lines = self._generate_directory_tree(input_dir, ignore_patterns)
        md_file.write("\n".join(tree_lines))

        md_file.write("\n```\n\n")
        md_file.write("---\n\n")

    def _generate_directory_tree(
        self, root_dir: str, ignore_patterns: List[str], prefix: str = "", current_rel_path: str = ""
    ) -> List[str]:
        """生成目录树"""
        items = []

        try:
            entries = sorted(os.listdir(root_dir))
        except (PermissionError, OSError) as e:
            return [f"{prefix}└── (无法访问: {str(e)})"]

        for i, entry in enumerate(entries):
            path = os.path.join(root_dir, entry)
            rel_entry_path = os.path.join(current_rel_path, entry) if current_rel_path else entry

            # 检查是否应该忽略
            if self._should_ignore(path, rel_entry_path, ignore_patterns):
                continue

            is_last = i == len(entries) - 1

            try:
                if os.path.isdir(path):
                    items.append(f"{prefix}{'└── ' if is_last else '├── '}{entry}/")
                    # 递归处理子目录
                    extension = self._generate_directory_tree(
                        path, ignore_patterns, prefix + ("    " if is_last else "│   "), rel_entry_path
                    )
                    items.extend(extension)
                else:
                    items.append(f"{prefix}{'└── ' if is_last else '├── '}{entry}")
            except Exception as e:
                items.append(f"{prefix}{'└── ' if is_last else '├── '}{entry} (错误: {str(e)})")

        return items

    def _should_ignore(self, path: str, relative_path: str, ignore_patterns: List[str]) -> bool:
        """检查路径是否应该被忽略"""
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(relative_path, pattern):
                return True
            for part in path.split(os.sep):
                if fnmatch.fnmatch(part, pattern):
                    return True
        return False

    def _process_files(self, md_file, input_dir: str, ignore_patterns: List[str], stats: dict):
        """处理所有文件"""
        current_paths = []

        for root, dirs, files in os.walk(input_dir):
            rel_path = os.path.relpath(root, input_dir)

            # 过滤目录
            original_dirs_count = len(dirs)
            dirs[:] = [
                d
                for d in dirs
                if not self._should_ignore(
                    os.path.join(root, d), os.path.join(rel_path, d) if rel_path != "." else d, ignore_patterns
                )
            ]
            stats["ignored_paths"] += original_dirs_count - len(dirs)

            # 排序
            dirs.sort()
            files.sort()

            # 计算深度
            depth = 0 if rel_path == "." else len(rel_path.split(os.sep))

            # 更新路径栈
            while current_paths and len(current_paths) >= depth + 1:
                current_paths.pop()

            dir_name = os.path.basename(root) if os.path.basename(root) else root
            if rel_path != ".":
                current_paths.append(dir_name)

            # 检查目录是否被忽略
            if self._should_ignore(root, rel_path, ignore_patterns):
                stats["ignored_paths"] += 1
                continue

            stats["total_dirs"] += 1

            # 写入目录标题
            if rel_path != ".":
                heading_level = min(depth + 1, 6)
                heading_prefix = "#" * heading_level
                path_str = " / ".join(current_paths)
                md_file.write(f"{heading_prefix} 📂 目录: {path_str}\n\n")

            # 过滤文件
            original_files_count = len(files)
            files = [
                f
                for f in files
                if not self._should_ignore(
                    os.path.join(root, f), os.path.join(rel_path, f) if rel_path != "." else f, ignore_patterns
                )
            ]
            stats["ignored_paths"] += original_files_count - len(files)

            # 处理文件
            for filename in files:
                self._process_file(md_file, root, filename, input_dir, depth, stats)

    def _process_file(self, md_file, root: str, filename: str, input_dir: str, depth: int, stats: dict):
        """处理单个文件"""
        filepath = os.path.join(root, filename)
        rel_file_path = os.path.relpath(filepath, input_dir)

        stats["total_files"] += 1

        # 写入文件标题
        file_heading_level = min(depth + 2, 6)
        file_heading_prefix = "#" * file_heading_level
        file_ext = os.path.splitext(filename)[1].lower()

        md_file.write(f"{file_heading_prefix} {self._get_file_icon(file_ext)} 文件: {filename}\n\n")
        md_file.write(f"**路径**: `{rel_file_path}`  \n")

        try:
            file_size = self._get_file_size(filepath)
            md_file.write(f"**大小**: {file_size}  \n")
        except:
            md_file.write(f"**大小**: 未知  \n")

        md_file.write(f"**类型**: {self._get_file_type_description(file_ext)}\n\n")

        # 处理文件内容
        self._process_file_content(md_file, filepath, filename, stats)

        md_file.write("---\n\n")

    def _process_file_content(self, md_file, filepath: str, filename: str, stats: dict):
        """处理文件内容"""
        ext = os.path.splitext(filename)[1].lower()

        # 判断是否需要转换
        should_convert = self._should_convert_to_markdown(ext) and self.markitdown_available

        if should_convert:
            stats["converted_files"] += 1
            self._convert_with_markitdown(md_file, filepath, stats)
        else:
            # 尝试读取文本文件
            content = self._read_text_file(filepath)
            if content is not None:
                stats["text_files"] += 1
                self._write_text_content(md_file, content, filename)
            else:
                if self.markitdown_available and self._should_convert_to_markdown(ext):
                    md_file.write("*(二进制文件，需要markitdown进行转换但转换失败)*\n\n")
                else:
                    md_file.write("*(二进制文件，内容无法直接显示)*\n\n")
                stats["failed_files"] += 1

    def _convert_with_markitdown(self, md_file, filepath: str, stats: dict):
        """使用markitdown转换文件"""
        try:
            result = self.markitdown_instance.convert(filepath)
            content = result.text_content

            if content:
                md_file.write("*(使用markitdown转换后的内容)*\n\n")
                separator = self._get_safe_separator(content)
                md_file.write(f"{separator}markdown\n")
                md_file.write(content)
                if not content.endswith("\n"):
                    md_file.write("\n")
                md_file.write(f"{separator}\n\n")
            else:
                md_file.write("*(转换成功但返回空内容)*\n\n")
                stats["failed_files"] += 1
        except Exception as e:
            md_file.write(f"*(使用markitdown转换失败: {str(e)})*\n\n")
            stats["failed_files"] += 1

    def _write_text_content(self, md_file, content: str, filename: str):
        """写入文本内容"""
        language = self._get_language_from_extension(filename)
        separator = self._get_safe_separator(content)
        md_file.write(f"{separator}{language}\n")
        md_file.write(content)
        if not content.endswith("\n"):
            md_file.write("\n")
        md_file.write(f"{separator}\n\n")

    def _get_safe_separator(self, content: str) -> str:
        """获取安全的代码块分隔符"""
        max_backticks = self._find_longest_backtick_sequence(content)
        backtick_count = max(3, max_backticks + 1)
        separator = "`" * backtick_count

        # 确保分隔符唯一
        lines = content.split("\n")
        while any(line.strip() == separator for line in lines) and backtick_count < 20:
            backtick_count += 1
            separator = "`" * backtick_count

        return separator

    def _find_longest_backtick_sequence(self, content: str) -> int:
        """找出内容中连续反引号的最大数量"""
        if not content:
            return 0
        matches = re.findall(r"(`+)", content)
        return max([len(match) for match in matches], default=0)

    def _should_convert_to_markdown(self, ext: str) -> bool:
        """判断文件扩展名是否需要转换为Markdown"""
        convert_extensions = {
            ".pdf",
            ".doc",
            ".docx",
            ".ppt",
            ".pptx",
            ".xls",
            ".xlsx",
            ".odt",
            ".ods",
            ".odp",
            ".rtf",
            ".epub",
            ".mobi",
            ".azw3",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".tiff",
            ".tif",
            ".svg",
            ".webp",
            ".ico",
            ".heic",
            ".heif",
        }
        return ext in convert_extensions

    def _read_text_file(self, filepath: str, encodings=None) -> Optional[str]:
        """尝试使用多种编码读取文本文件"""
        if encodings is None:
            encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "gbk", "gb2312"]

        for encoding in encodings:
            try:
                with open(filepath, "r", encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, LookupError):
                continue
            except Exception:
                break
        return None

    def _get_language_from_extension(self, filename: str) -> str:
        """根据文件扩展名获取语言"""
        ext_map = {
            ".py": "python",
            ".md": "markdown",
            ".txt": "text",
            ".js": "javascript",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".sh": "bash",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".sql": "sql",
        }
        return ext_map.get(os.path.splitext(filename)[1].lower(), "")

    def _get_file_size(self, filepath: str) -> str:
        """获取文件大小的人类可读格式"""
        try:
            size = os.path.getsize(filepath)
            for unit in ["B", "KB", "MB", "GB"]:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "未知"

    def _get_file_type_description(self, ext: str) -> str:
        """获取文件类型描述"""
        type_map = {
            ".py": "Python脚本",
            ".md": "Markdown文档",
            ".txt": "文本文件",
            ".pdf": "PDF文档",
            ".doc": "Word文档",
            ".docx": "Word文档",
            ".xls": "Excel表格",
            ".xlsx": "Excel表格",
            ".jpg": "JPEG图像",
            ".png": "PNG图像",
            ".gif": "GIF图像",
            ".zip": "压缩文件",
            ".json": "JSON数据",
            ".html": "HTML网页",
            ".css": "样式表",
            ".js": "JavaScript脚本",
        }
        return type_map.get(ext, "未知类型")

    def _get_file_icon(self, ext: str) -> str:
        """获取文件图标"""
        icon_map = {
            ".py": "🐍",
            ".md": "📝",
            ".txt": "📄",
            ".pdf": "📕",
            ".doc": "📘",
            ".docx": "📘",
            ".xls": "📊",
            ".xlsx": "📊",
            ".jpg": "🖼️",
            ".png": "🖼️",
            ".gif": "🖼️",
            ".zip": "🗜️",
            ".json": "🗂️",
            ".html": "🌐",
            ".css": "🎨",
            ".js": "⚡",
            ".java": "☕",
            ".cpp": "⚙️",
            ".c": "⚙️",
            ".go": "🐹",
            ".rs": "🦀",
        }
        return icon_map.get(ext, "📄")

    def _write_statistics(self, md_file, stats: dict):
        """写入统计信息"""
        md_file.write(f"\n\n## 📈 统计信息\n\n")
        md_file.write(f"- **总目录数**: {stats['total_dirs']}\n")
        md_file.write(f"- **总文件数**: {stats['total_files']}\n")
        # md_file.write(f"- **文本文件**: {stats['text_files']}\n")
        # md_file.write(f"- **转换文件**: {stats['converted_files']}\n")
        # md_file.write(f"- **失败文件**: {stats['failed_files']}\n")
        # md_file.write(f"- **忽略项目**: {stats['ignored_paths']}\n")

        # end_time = datetime.now()
        # duration = (end_time - stats["start_time"]).total_seconds()
        # md_file.write(f"- **处理耗时**: {duration:.2f}秒\n")
        # md_file.write(f"- **处理完成**: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    def _print_statistics(self, stats: dict, output_file: str):
        """打印统计信息"""
        print(f"\n✅ 完成! 已生成 {output_file}")
        print(f"📊 统计信息:")
        print(f"  - 总目录数: {stats['total_dirs']}")
        print(f"  - 总文件数: {stats['total_files']}")
        print(f"  - 文本文件: {stats['text_files']}")
        print(f"  - 转换文件: {stats['converted_files']}")
        print(f"  - 失败文件: {stats['failed_files']}")
        print(f"  - 忽略项目: {stats['ignored_paths']}")

        duration = (datetime.now() - stats["start_time"]).total_seconds()
        print(f"  - 处理耗时: {duration:.2f}秒")
