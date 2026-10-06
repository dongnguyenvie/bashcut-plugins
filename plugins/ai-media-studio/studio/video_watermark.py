"""Local, frame-by-frame Gemini watermark removal for video files."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import numpy as np
from PIL import Image

from .media import get_ffmpeg_path


ProgressCallback = Callable[[int, Optional[int]], None]
CancelCallback = Callable[[], bool]


@dataclass(frozen=True)
class VideoInfo:
    width: int
    height: int
    fps: float
    duration: Optional[float]


def get_veo_video_watermark_info(width: int, height: int) -> Dict[str, int]:
    """Gemini/Veo's video anchor; intentionally independent of image code."""
    min_dimension = min(width, height)
    size = max(24, min(int(round(min_dimension / 15.0)), min_dimension))
    margin = int(round(min_dimension / 10.0))
    return {
        "size": size,
        "x": max(0, width - margin - size),
        "y": max(0, height - margin - size),
        "width": size,
        "height": size,
    }


def get_veo3_text_box(width: int, height: int) -> Dict[str, int]:
    """Small bottom-right Veo wordmark seen in 720p landscape and portrait exports."""
    factor = min(width, height) / 720.0
    box_width = max(8, round(34 * factor))
    box_height = max(8, round(15 * factor))
    right_margin = max(1, round(16 * factor))
    bottom_margin = max(1, round(16 * factor))
    return {
        "x": max(0, width - right_margin - box_width),
        "y": max(0, height - bottom_margin - box_height),
        "width": min(box_width, width - 1),
        "height": min(box_height, height - 1),
    }


def resolve_video_box(
    anchor: Dict[str, int], width: int, height: int,
    scale: float, offset_x: int, offset_y: int,
) -> Dict[str, int]:
    """Match the web video's centre-based size and position adjustment."""
    size = max(8, min(int(round(anchor["size"] * scale)), min(width, height)))
    center_x = anchor["x"] + anchor["size"] / 2.0 + round(offset_x)
    center_y = anchor["y"] + anchor["size"] / 2.0 + round(offset_y)
    return {
        "size": size,
        "x": max(0, min(int(round(center_x - size / 2.0)), width - size)),
        "y": max(0, min(int(round(center_y - size / 2.0)), height - size)),
        "width": size,
        "height": size,
    }


def heal_upscaled_video_edge_seam(
    frame: np.ndarray, box: Dict[str, int], border: int = 1
) -> np.ndarray:
    """Soften only the narrow boundary where a cleaned ROI meets its frame."""
    if border < 1:
        return frame

    height, width, _ = frame.shape
    x, y = box["x"], box["y"]
    right, bottom = x + box["width"], y + box["height"]
    xs, xe = max(0, x - border), min(width, right + border)
    ys, ye = max(0, y - border), min(height, bottom + border)
    rows, cols = np.mgrid[ys:ye, xs:xe]
    band = ~((cols >= x + border) & (cols < right - border) &
             (rows >= y + border) & (rows < bottom - border))
    rows, cols = rows[band], cols[band]
    sums = np.zeros((len(rows), 3), dtype=np.float32)
    counts = np.zeros(len(rows), dtype=np.float32)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            rr, cc = rows + dy, cols + dx
            valid = (rr >= 0) & (rr < height) & (cc >= 0) & (cc < width)
            sums[valid] += frame[rr[valid], cc[valid]]
            counts[valid] += 1
    healed = frame.copy()
    healed[rows, cols] = np.clip(frame[rows, cols].astype(np.float32) * 0.35 +
                                (sums / counts[:, None]) * 0.65, 0, 255).astype(np.uint8)
    return healed


class VideoWatermarkRemover:
    """Standalone Gemini/Veo video watermark remover; it never calls image code."""

    def __init__(self, ffmpeg_path: Optional[str] = None):
        self.ffmpeg_path = ffmpeg_path or get_ffmpeg_path()
        mask_path = Path(__file__).resolve().parent.parent / "assets" / "bg_96.png"
        if not mask_path.is_file():
            raise RuntimeError(f"Không tìm thấy mask watermark video: {mask_path}")
        self.video_mask = Image.open(mask_path).convert("RGBA")
        veo_mask_path = mask_path.with_name("veo3_text_720.png")
        if not veo_mask_path.is_file():
            raise RuntimeError(f"Không tìm thấy mask watermark Veo 3: {veo_mask_path}")
        self.veo3_mask = Image.open(veo_mask_path).convert("RGBA")

    def remove_frame(
        self, frame: np.ndarray, gain: float = 0.6, scale: float = 1.01,
        offset_x: int = -24, offset_y: int = -24,
    ) -> tuple[np.ndarray, Dict[str, Any]]:
        """Inverse-alpha remove one RGB video frame using only the video mask."""
        if frame.ndim != 3 or frame.shape[2] != 3 or frame.dtype != np.uint8:
            raise ValueError("Frame phải là mảng RGB uint8 có dạng (height, width, 3).")

        height, width, _ = frame.shape
        box = resolve_video_box(
            get_veo_video_watermark_info(width, height), width, height,
            scale, offset_x, offset_y,
        )
        x, y, box_width, box_height = box["x"], box["y"], box["width"], box["height"]
        mask = np.asarray(
            self.video_mask.resize((box_width, box_height), Image.Resampling.BICUBIC),
            dtype=np.float32,
        )
        # Gemini's supplied PNG has opaque RGBA; its RGB brightness stores
        # the alpha map.  This is the same alpha used for inverse blending.
        alpha = np.clip(np.max(mask[:, :, :3], axis=2) / 255.0 * gain, 0.0, 0.99)
        active = alpha >= 0.002
        result = frame.copy()
        crop = result[y:y + box_height, x:x + box_width].astype(np.float32)
        restored = (crop - 255.0 * alpha[:, :, None]) / (1.0 - alpha[:, :, None])
        restored = np.clip(restored + 0.5, 0, 255).astype(np.uint8)
        result[y:y + box_height, x:x + box_width] = np.where(
            active[:, :, None], restored, result[y:y + box_height, x:x + box_width]
        )
        return result, {"box": box}

    def remove_veo3_frame(self, frame: np.ndarray, scale: float = 1.0, offset_x: int = 0, offset_y: int = 0) -> tuple[np.ndarray, Dict[str, Any]]:
        """Reverse the semi-transparent white Veo wordmark without blurring its box."""
        if frame.ndim != 3 or frame.shape[2] != 3 or frame.dtype != np.uint8:
            raise ValueError("Frame phải là mảng RGB uint8 có dạng (height, width, 3).")

        height, width, _ = frame.shape
        box = get_veo3_text_box(width, height)
        bw = max(1, min(width, round(box["width"] * scale)))
        bh = max(1, min(height, round(box["height"] * scale)))
        box = {"x": max(0, min(width-bw, round(box["x"] + box["width"]/2 - bw/2 + offset_x))),
               "y": max(0, min(height-bh, round(box["y"] + box["height"]/2 - bh/2 + offset_y))),
               "width": bw, "height": bh}
        x, y, box_width, box_height = box["x"], box["y"], box["width"], box["height"]
        alpha = np.asarray(
            self.veo3_mask.resize((box_width, box_height), Image.Resampling.BICUBIC).getchannel("A"),
            dtype=np.float32,
        ) / 255.0
        crop = frame[y:y + box_height, x:x + box_width].astype(np.float32)
        restored = (crop - 255.0 * alpha[:, :, None]) / (1.0 - alpha[:, :, None])
        result = frame.copy()
        result[y:y + box_height, x:x + box_width] = np.clip(restored + 0.5, 0, 255).astype(np.uint8)
        return result, {"box": box}

    def probe(self, input_path: Path) -> VideoInfo:
        import imageio_ffmpeg
        reader = imageio_ffmpeg.read_frames(str(input_path))
        try:
            metadata = next(reader)
            width, height = metadata["size"]
            fps = float(metadata["fps"])
            if fps <= 0 or width <= 0 or height <= 0:
                raise ValueError("Invalid video metadata.")
            return VideoInfo(width, height, fps, metadata.get("duration"))
        finally:
            reader.close()

    def build_decode_command(self, source: Path) -> list[str]:
        return [
            self.ffmpeg_path, "-v", "error", "-i", str(source), "-map", "0:v:0",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
        ]

    def build_encode_command(
        self, source: Path, output: Path, width: int, height: int, fps: float
    ) -> list[str]:
        return [
            self.ffmpeg_path, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{width}x{height}", "-r", f"{fps:.12g}", "-i", "-", "-i", str(source),
            "-map", "0:v:0", "-map", "1:a?", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            # Keep untouched regions close to the source without excessive encode cost.
            # FFmpeg's default x264 CRF 23 visibly damages untouched regions.
            "-preset", "medium", "-crf", "16",
            "-c:a", "copy", "-movflags", "+faststart", str(output),
        ]

    @staticmethod
    def _diagnostics(handle):
        handle.seek(0)
        return handle.read().decode(errors="replace")[-2000:]

    @staticmethod
    def _terminate(process: Optional[subprocess.Popen]) -> None:
        if process is None or process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    @staticmethod
    def temporary_output_path(source: Path, output: Path) -> Path:
        """Reserve a unique, owned temporary path beside the requested output."""
        descriptor, name = tempfile.mkstemp(
            dir=output.parent,
            prefix=f".{output.stem}.",
            suffix=output.suffix,
        )
        os.close(descriptor)
        temporary = Path(name)
        if temporary.resolve() in {source.resolve(), output.resolve()}:
            temporary.unlink(missing_ok=True)
            raise RuntimeError("Không thể tạo file tạm an toàn cho video output.")
        return temporary

    def process_file(
        self,
        input_path: Path,
        output_path: Path,
        gain: float = 0.6,
        scale: Optional[float] = None,
        offset_x: Optional[int] = None,
        offset_y: Optional[int] = None,
        preset_mode: str = "auto",
        mode: str = "gemini",
        progress_callback: Optional[ProgressCallback] = None,
        is_cancelled: Optional[CancelCallback] = None,
    ) -> Dict[str, Any]:
        source, output = Path(input_path), Path(output_path)
        if not source.is_file():
            raise FileNotFoundError(f"Không tìm thấy video đầu vào: {source}")
        if source.resolve() == output.resolve():
            raise ValueError("Đường dẫn output không được trùng video input.")
        if output.exists():
            raise FileExistsError(f"File kết quả đã tồn tại: {output}")
        if not output.parent.is_dir():
            raise FileNotFoundError(f"Thư mục output không tồn tại: {output.parent}")
        if mode not in {"gemini", "veo3"}:
            raise ValueError(f"Chế độ watermark video không hợp lệ: {mode}")

        info = self.probe(source)
        frame_bytes = info.width * info.height * 3
        total_frames = round(info.duration * info.fps) if info.duration is not None else None
        temporary = self.temporary_output_path(source, output)

        decode_log = tempfile.TemporaryFile()
        encode_log = tempfile.TemporaryFile()
        decoder: Optional[subprocess.Popen] = None
        encoder: Optional[subprocess.Popen] = None
        processed = 0
        succeeded = False
        try:
            decoder = subprocess.Popen(
                self.build_decode_command(source),
                stdout=subprocess.PIPE, stderr=decode_log
            )
            encoder = subprocess.Popen(
                self.build_encode_command(source, temporary, info.width, info.height, info.fps),
                stdin=subprocess.PIPE, stderr=encode_log,
            )
            assert decoder.stdout is not None and encoder.stdin is not None

            while True:
                if is_cancelled and is_cancelled():
                    return {"success": False, "cancelled": True, "error": "Người dùng đã hủy xử lý."}
                raw = decoder.stdout.read(frame_bytes)
                if not raw:
                    break
                if len(raw) != frame_bytes:
                    return {"success": False, "error": "Luồng frame video bị thiếu dữ liệu."}
                frame = np.frombuffer(raw, dtype=np.uint8).reshape(info.height, info.width, 3)
                if mode == "veo3":
                    cleaned, _ = self.remove_veo3_frame(frame, scale=scale or 1.0, offset_x=offset_x or 0, offset_y=offset_y or 0)
                    encoder.stdin.write(cleaned.tobytes())
                else:
                    cleaned, meta = self.remove_frame(
                        frame, gain=gain, scale=scale or 1.01, offset_x=-24 if offset_x is None else offset_x, offset_y=-24 if offset_y is None else offset_y
                    )
                    healed = heal_upscaled_video_edge_seam(cleaned, meta["box"])
                    encoder.stdin.write(healed.tobytes())
                processed += 1
                if progress_callback:
                    progress_callback(processed, total_frames)

            encoder.stdin.close()
            decoder_return = decoder.wait()
            encoder_return = encoder.wait()
            if decoder_return != 0:
                raise RuntimeError(self._diagnostics(decode_log) or "FFmpeg không thể giải mã video.")
            if encoder_return != 0:
                raise RuntimeError(self._diagnostics(encode_log) or "FFmpeg không thể mã hóa video.")
            os.replace(temporary, output)
            succeeded = True
            return {
                "success": True,
                "input_path": str(source),
                "output_path": str(output),
                "frames_processed": processed,
                "total_frames": total_frames,
                "size": (info.width, info.height),
            }
        except (BrokenPipeError, OSError, RuntimeError) as exc:
            return {"success": False, "error": str(exc), "frames_processed": processed}
        finally:
            if not succeeded:
                self._terminate(decoder)
                self._terminate(encoder)
                if temporary.exists():
                    temporary.unlink()
            decode_log.close()
            encode_log.close()
            for process in (decoder, encoder):
                if process is not None:
                    for stream in (process.stdin, process.stdout, process.stderr):
                        if stream is not None and not stream.closed:
                            stream.close()

