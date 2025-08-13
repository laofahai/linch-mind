"""
基础内容分析服务
提供实体提取、关键词分析等基础文本处理功能
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ContentAnalysisService:
    """
    基础内容分析服务

    提供不依赖复杂AI模型的基础文本分析功能：
    - URL识别和提取
    - 文件路径检测
    - 关键词提取
    - 实体识别（基于正则表达式）
    - 内容分类
    """

    def __init__(self):
        # URL正则表达式
        self.url_pattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )

        # 文件路径正则表达式
        self.file_path_patterns = [
            re.compile(
                r'(?:[a-zA-Z]:\\)?(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*'
            ),  # Windows路径
            re.compile(r"(?:/[^/\n\r]*)+"),  # Unix路径
            re.compile(r"[~]?/[^/\s\n\r]*(?:/[^/\s\n\r]*)*"),  # 扩展Unix路径
        ]

        # 邮箱正则表达式
        self.email_pattern = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        )

        # 电话号码正则表达式（简单版本）
        self.phone_pattern = re.compile(
            r"(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})|\b\d{11}\b"
        )

        # 常见停用词
        self.stop_words = {
            "的",
            "了",
            "在",
            "是",
            "我",
            "有",
            "和",
            "就",
            "不",
            "人",
            "都",
            "一",
            "一个",
            "上",
            "也",
            "很",
            "到",
            "说",
            "要",
            "去",
            "你",
            "会",
            "着",
            "没有",
            "看",
            "好",
            "自己",
            "这",
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "this",
            "that",
            "these",
            "those",
            "is",
            "am",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
        }

        # 敏感内容关键词
        self.sensitive_keywords = {
            "password",
            "passwd",
            "pwd",
            "secret",
            "token",
            "key",
            "api_key",
            "access_token",
            "refresh_token",
            "jwt",
            "credential",
            "auth",
            "密码",
            "密钥",
            "口令",
            "令牌",
            "凭据",
        }

    def analyze_content(
        self, content: str, content_type: str = "text"
    ) -> Dict[str, Any]:
        """
        分析内容并提取各种信息

        Args:
            content: 要分析的内容
            content_type: 内容类型（text, url, file_path等）

        Returns:
            分析结果字典
        """
        try:
            if not content or not content.strip():
                return self._empty_analysis()

            # 基础信息
            result = {
                "content_length": len(content),
                "word_count": len(content.split()),
                "line_count": len(content.splitlines()),
                "is_sensitive": self._is_sensitive_content(content),
                "content_category": self._categorize_content(content),
                "analysis_timestamp": datetime.utcnow().isoformat(),
            }

            # 实体提取
            entities = self._extract_entities(content)
            result["entities"] = entities

            # 关键词提取
            keywords = self._extract_keywords(content)
            result["keywords"] = keywords

            # 如果是URL内容，进行URL分析
            if content_type == "url" or entities.get("urls"):
                result["url_analysis"] = self._analyze_urls(entities.get("urls", []))

            # 如果是文件路径，进行路径分析
            if content_type == "file_path" or entities.get("file_paths"):
                result["file_analysis"] = self._analyze_file_paths(
                    entities.get("file_paths", [])
                )

            logger.debug(
                f"内容分析完成，提取到 {len(entities)} 个实体类型，{len(keywords)} 个关键词"
            )
            return result

        except Exception as e:
            logger.error(f"内容分析失败: {e}")
            return self._error_analysis(str(e))

    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """提取实体"""
        entities = {
            "urls": [],
            "emails": [],
            "phones": [],
            "file_paths": [],
            "numbers": [],
            "dates": [],
        }

        # URL提取
        urls = self.url_pattern.findall(content)
        entities["urls"] = list(set(urls))

        # 邮箱提取
        emails = self.email_pattern.findall(content)
        entities["emails"] = list(set(emails))

        # 电话号码提取
        phones = self.phone_pattern.findall(content)
        # 处理元组结果
        if phones and isinstance(phones[0], tuple):
            phones = ["-".join(phone) for phone in phones if any(phone)]
        entities["phones"] = list(set(phones))

        # 文件路径提取
        file_paths = []
        for pattern in self.file_path_patterns:
            matches = pattern.findall(content)
            for match in matches:
                if self._is_likely_file_path(match):
                    file_paths.append(match)
        entities["file_paths"] = list(set(file_paths))

        # 数字提取
        numbers = re.findall(r"\b\d+(?:\.\d+)?\b", content)
        entities["numbers"] = list(set(numbers))

        # 简单日期提取
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
            r"\d{2}-\d{2}-\d{4}",  # MM-DD-YYYY
        ]
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            dates.extend(matches)
        entities["dates"] = list(set(dates))

        # 过滤空值
        entities = {k: v for k, v in entities.items() if v}

        return entities

    def _extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        try:
            # 简单的关键词提取：移除标点符号，分词，去重，过滤停用词
            text = re.sub(r"[^\w\s]", " ", content.lower())
            words = text.split()

            # 过滤停用词和短词
            keywords = []
            for word in words:
                word = word.strip()
                if (
                    len(word) >= 2
                    and word not in self.stop_words
                    and not word.isdigit()
                ):
                    keywords.append(word)

            # 统计词频并排序
            word_freq = {}
            for word in keywords:
                word_freq[word] = word_freq.get(word, 0) + 1

            # 按频率排序并返回前N个
            sorted_keywords = sorted(
                word_freq.items(), key=lambda x: x[1], reverse=True
            )
            return [word for word, freq in sorted_keywords[:max_keywords]]

        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return []

    def _categorize_content(self, content: str) -> str:
        """内容分类"""
        content_lower = content.lower()

        # URL内容
        if self.url_pattern.search(content):
            if any(
                domain in content_lower
                for domain in ["github.com", "gitlab.com", "bitbucket.org"]
            ):
                return "code_repository"
            elif any(
                domain in content_lower
                for domain in ["youtube.com", "youtu.be", "vimeo.com"]
            ):
                return "video"
            elif any(
                domain in content_lower
                for domain in ["medium.com", "blog.", "wordpress.com"]
            ):
                return "article"
            else:
                return "url"

        # 文件路径
        file_extensions = re.findall(r"\.([a-zA-Z0-9]+)(?:\s|$)", content)
        if file_extensions:
            ext = file_extensions[0].lower()
            if ext in ["jpg", "jpeg", "png", "gif", "bmp", "svg"]:
                return "image_path"
            elif ext in ["mp4", "avi", "mov", "mkv", "wmv"]:
                return "video_path"
            elif ext in ["pdf", "doc", "docx", "txt", "md"]:
                return "document_path"
            elif ext in ["py", "js", "html", "css", "java", "cpp", "c"]:
                return "code_path"
            else:
                return "file_path"

        # 代码内容
        if any(
            keyword in content
            for keyword in [
                "def ",
                "function ",
                "class ",
                "import ",
                "#include",
                "var ",
                "const ",
            ]
        ):
            return "code"

        # 邮箱
        if self.email_pattern.search(content):
            return "contact"

        # 数字列表或表格
        if len(re.findall(r"\d+", content)) / len(content.split()) > 0.3:
            return "data"

        # 长文本
        if len(content) > 500:
            return "long_text"

        return "text"

    def _is_sensitive_content(self, content: str) -> bool:
        """检查是否包含敏感内容"""
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in self.sensitive_keywords)

    def _is_likely_file_path(self, path: str) -> bool:
        """判断是否是有效的文件路径"""
        if len(path) < 3:
            return False

        # 检查是否包含文件扩展名
        if "." in path and not path.endswith("."):
            return True

        # 检查是否是目录路径
        if "/" in path or "\\" in path:
            return True

        return False

    def _analyze_urls(self, urls: List[str]) -> Dict[str, Any]:
        """分析URL"""
        analysis = {"count": len(urls), "domains": [], "protocols": [], "paths": []}

        for url in urls:
            try:
                parsed = urlparse(url)
                if parsed.netloc:
                    analysis["domains"].append(parsed.netloc)
                if parsed.scheme:
                    analysis["protocols"].append(parsed.scheme)
                if parsed.path:
                    analysis["paths"].append(parsed.path)
            except Exception:
                continue

        # 去重
        analysis["domains"] = list(set(analysis["domains"]))
        analysis["protocols"] = list(set(analysis["protocols"]))

        return analysis

    def _analyze_file_paths(self, paths: List[str]) -> Dict[str, Any]:
        """分析文件路径"""
        analysis = {"count": len(paths), "extensions": [], "directories": []}

        for path in paths:
            # 提取文件扩展名
            if "." in path:
                ext = path.split(".")[-1].lower()
                if len(ext) <= 5:  # 合理的扩展名长度
                    analysis["extensions"].append(ext)

            # 提取目录
            if "/" in path:
                dir_path = "/".join(path.split("/")[:-1])
                if dir_path:
                    analysis["directories"].append(dir_path)
            elif "\\" in path:
                dir_path = "\\".join(path.split("\\")[:-1])
                if dir_path:
                    analysis["directories"].append(dir_path)

        # 去重
        analysis["extensions"] = list(set(analysis["extensions"]))
        analysis["directories"] = list(set(analysis["directories"]))

        return analysis

    def _empty_analysis(self) -> Dict[str, Any]:
        """空内容的分析结果"""
        return {
            "content_length": 0,
            "word_count": 0,
            "line_count": 0,
            "is_sensitive": False,
            "content_category": "empty",
            "entities": {},
            "keywords": [],
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    def _error_analysis(self, error_message: str) -> Dict[str, Any]:
        """错误分析结果"""
        return {
            "error": True,
            "error_message": error_message,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }


# ServiceFacade现在负责管理服务单例，不再需要本地单例模式
