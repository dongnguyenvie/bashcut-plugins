from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import numpy as np
from PIL import Image

# Embedded Gemini / Imagen watermark templates

def get_watermark_info(width: int, height: int) -> Dict[str, int]:
    a = min(width, height) / 1536.0
    size = max(16, int(round(96 * a)))
    margin = max(8, int(round(64 * a)))
    return {
        "size": size,
        "x": max(0, width - margin - size),
        "y": max(0, height - margin - size),
        "width": size,
        "height": size
    }

def get_adaptive_image_preset(mode: str, width: int, height: int) -> Dict[str, Any]:
    if mode == "classic":
        return {"gain": 0.6, "offsetX": 0, "offsetY": 0, "sizeScale": 1.0}
    min_dim = min(width, height)
    max_dim = max(width, height)
    ratio = max_dim / max(1.0, float(min_dim))

    if min_dim >= 1800 or max_dim >= 2400:
        if ratio >= 1.65:
            scale, offset = 0.5, -1
        elif ratio >= 1.42:
            scale, offset = 0.46, 6
        elif ratio >= 1.18:
            scale, offset = 0.43, 13
        else:
            scale, offset = 0.38, 25
        return {"gain": 0.6, "offsetX": offset, "offsetY": offset, "sizeScale": scale}

    if ratio >= 1.65:
        scale, offset = 1.01, -41
    elif ratio >= 1.42:
        scale, offset = 0.92, -38
    elif ratio >= 1.18:
        scale, offset = 0.86, -35
    else:
        scale, offset = 0.75, -27
    return {"gain": 0.6, "offsetX": offset, "offsetY": offset, "sizeScale": scale}

def resolve_box(base_info: Dict[str, int], width: int, height: int, preset: Dict[str, Any]) -> Dict[str, int]:
    scale = preset.get("sizeScale", 1.0)
    size = max(8, min(int(round(base_info["size"] * scale)), min(width, height)))
    center_x = base_info["x"] + base_info["size"] / 2.0 + preset.get("offsetX", 0)
    center_y = base_info["y"] + base_info["size"] / 2.0 + preset.get("offsetY", 0)
    x = max(0, min(int(round(center_x - size / 2.0)), width - size))
    y = max(0, min(int(round(center_y - size / 2.0)), height - size))
    return {"size": size, "x": x, "y": y, "width": size, "height": size}

class GeminiWatermarkRemover:
    """Thuật toán loại bỏ Watermark Google Gemini / Imagen từ hình ảnh."""

    def __init__(self):
        self.bg48_img = Image.open(Path(__file__).resolve().parent.parent / "assets/bg_48.png").convert("RGBA")
        self.bg96_img = Image.open(Path(__file__).resolve().parent.parent / "assets/bg_96.png").convert("RGBA")

    def remove_watermark(
        self,
        input_image: Image.Image,
        gain: float = 0.6,
        scale: Optional[float] = None,
        offset_x: Optional[int] = None,
        offset_y: Optional[int] = None,
        preset_mode: str = "auto"
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        w, h = input_image.size
        has_alpha = (input_image.mode == "RGBA")
        img_rgb = input_image.convert("RGB")
        img_arr = np.array(img_rgb, dtype=np.uint8)

        base_info = get_watermark_info(w, h)
        adaptive_preset = get_adaptive_image_preset(preset_mode, w, h)

        final_preset = {
            "gain": gain if gain is not None else adaptive_preset["gain"],
            "sizeScale": scale if scale is not None else adaptive_preset["sizeScale"],
            "offsetX": offset_x if offset_x is not None else adaptive_preset["offsetX"],
            "offsetY": offset_y if offset_y is not None else adaptive_preset["offsetY"]
        }

        target_box = resolve_box(base_info, w, h, final_preset)
        bx, by, bw, bh = target_box["x"], target_box["y"], target_box["width"], target_box["height"]

        tpl = self.bg48_img if bw <= 48 else self.bg96_img
        resized_tpl = tpl.resize((bw, bh), resample=Image.Resampling.BICUBIC)
        tpl_arr = np.array(resized_tpl, dtype=np.float32)

        rgb_max = np.maximum(np.maximum(tpl_arr[:, :, 0], tpl_arr[:, :, 1]), tpl_arr[:, :, 2])
        alpha = (rgb_max / 255.0) * final_preset["gain"]

        crop = img_arr[by:by+bh, bx:bx+bw, :].astype(np.float32)

        mask = alpha >= 0.002
        alpha_clipped = np.clip(alpha, 0.0, 0.99)

        t = alpha_clipped / 0.2
        smooth_val = t * t * (3.0 - 2.0 * t) * alpha_clipped
        effective_alpha = np.where(alpha_clipped < 0.2, smooth_val, alpha_clipped)

        inv_factor = 1.0 / (1.0 - effective_alpha)
        logo_val = 255.0 * effective_alpha

        for c in range(3):
            orig_c = crop[:, :, c]
            cleaned_c = (orig_c - logo_val) * inv_factor
            cleaned_c = np.clip(cleaned_c + 0.5, 0, 255).astype(np.uint8)
            img_arr[by:by+bh, bx:bx+bw, c] = np.where(mask, cleaned_c, img_arr[by:by+bh, bx:bx+bw, c])

        result_img = Image.fromarray(img_arr)
        if has_alpha:
            alpha_ch = input_image.split()[3]
            result_img.putalpha(alpha_ch)

        return result_img, {
            "box": target_box,
            "preset": final_preset,
            "image_size": (w, h)
        }

    def process_file(
        self,
        file_path: Path,
        output_path: Path,
        gain: float = 0.60,
        preset_mode: str = "auto"
    ) -> Dict[str, Any]:
        """Xử lý gỡ watermark cho 1 file ảnh và lưu kết quả."""
        try:
            with Image.open(file_path) as img:
                cleaned_img, meta = self.remove_watermark(img, gain=gain, preset_mode=preset_mode)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                cleaned_img.save(output_path, format="PNG")
                return {
                    "success": True,
                    "input_path": str(file_path),
                    "output_path": str(output_path),
                    "size": meta["image_size"],
                    "box": meta["box"]
                }
        except Exception as e:
            return {
                "success": False,
                "input_path": str(file_path),
                "error": str(e)
            }
