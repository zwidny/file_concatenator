# file concatenator

将目录结构及所有文件内容转换为单个Markdown文件。

## 功能特性

- 📁 递归遍历目录和子目录
- 📝 将文件内容嵌入到Markdown代码块中
- 🔤 根据文件扩展名自动代码高亮
- 🔄 支持PDF、Word、Excel等文件转换（使用markitdown）
- 🚫 支持忽略特定文件和目录
- 📊 生成目录树和统计信息
- 🎯 保持文件的层级结构

## 安装

```bash
pip install file_concatenator
```

## 使用方法

### 基本用法
```bash
file_concatenator ./your_directory/
```

### 指定输出文件
```bash
file_concatenator ./your_directory/ -o output.md
```

### 忽略特定文件
```bash
file_concatenator ./your_directory/ --ignore "*.log" --ignore "*.tmp"
```

### 使用忽略文件
```bash
file_concatenator ./your_directory/ --ignore-file .gitignore
```

### 禁用markitdown转换
```bash
file_concatenator ./your_directory/ --no-markitdown
```

### 详细输出
```bash
file_concatenator ./your_directory/ -v
```

## 示例

```bash
# 处理技能目录
file_concatenator ./skills/pdf/

# 处理项目目录，忽略测试文件和日志
file_concatenator ./my_project/ --ignore "*_test.py" --ignore "*.log"

# 使用自定义忽略文件
file_concatenator ./my_project/ --ignore-file .mdignore
```

## 输出示例

生成的Markdown文件包含：
1. 目录结构树
2. 每个文件的路径、大小和类型信息
3. 文件内容（以代码块形式展示）
4. 转换的二进制文件内容
5. 处理统计信息

## 忽略文件格式

创建`.mdignore`文件，内容如：
```
# 忽略临时文件
*.tmp
*.temp
*.cache

# 忽略构建目录
build/
dist/

# 忽略测试文件
*_test.py
test_*.py
```

## 依赖

- markitdown: 用于PDF等二进制文件的转换
