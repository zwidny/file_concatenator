"""file_concatenator package - Convert directory structure to Markdown."""

__version__ = "1.0.0"
__author__ = "zhao"

from .cli import main
from .core import DirectoryToMarkdown


__all__ = ["main", "DirectoryToMarkdown"]
