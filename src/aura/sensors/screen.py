"""读屏感知传感器实现。

基于 mss 捕获当前屏幕画面，并尝试进行 OCR 提取屏幕文字。
OCR 使用可选的 pytesseract，未安装时降级为「仅图像」观测，
从而保证核心循环在缺少 OCR 依赖时依然可以运行。
"""

from __future__ import annotations

import time
from typing import Any

from .base import Observation, Sensor


class ScreenSensor(Sensor):
    """读屏传感器：捕获屏幕并提取文字（可选 OCR）。

    @param interval: 采样间隔（秒）。
    @param use_ocr: 是否启用 OCR 提取文字。
    """

    def __init__(self, interval: float = 2.0, use_ocr: bool = True):
        # 1. 保存采样配置
        self.interval = interval
        self.use_ocr = use_ocr
        # 2. 延迟导入 mss，避免无屏幕环境下导入失败
        try:
            import mss  # type: ignore

            self._sct = mss.mss()
        except Exception:
            self._sct = None

    def capture(self) -> list["Observation"]:
        """捕获当前屏幕并返回观测。

        @return: 包含屏幕图像与（可选）OCR 文本的观测列表。
        """
        # 1. 无可用屏幕捕获器时，返回空观测
        if self._sct is None:
            return []
        # 2. 抓取当前屏幕帧
        try:
            monitor = self._sct.monitors[1]  # 主显示器
            raw = self._sct.grab(monitor)
            image = self._raw_to_image(raw)
        except Exception:
            return []
        # 3. 尝试提取 OCR 文字（可选，失败时静默降级）
        text = self._ocr(image) if self.use_ocr else None
        # 4. 组装观测对象并返回
        obs = Observation(
            source="screen",
            timestamp=time.time(),
            text=text,
            image=image,
            metadata={"monitor": monitor, "use_ocr": self.use_ocr},
        )
        return [obs]

    def _raw_to_image(self, raw: Any) -> Any:
        """将 mss 原始帧转换为 PIL Image 对象。

        @param raw: mss ScreenShot 对象。
        @return: PIL Image；转换失败时返回 None。
        """
        try:
            from PIL import Image  # type: ignore

            # 1. 依据原始帧尺寸构造内存图像
            return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
        except Exception:
            return None

    def _ocr(self, image: Any) -> str | None:
        """对图像执行 OCR 提取文字。

        @param image: PIL Image 对象。
        @return: OCR 文本，失败或未安装时返回 None。
        """
        if image is None:
            return None
        try:
            import pytesseract  # type: ignore

            # 1. 调用 OCR 引擎
            return pytesseract.image_to_string(image, lang="chi_sim+eng").strip()
        except Exception:
            return None

    def close(self) -> None:
        """关闭屏幕捕获会话，释放底层资源。"""
        if self._sct is not None:
            try:
                self._sct.close()
            except Exception:
                pass
            self._sct = None
