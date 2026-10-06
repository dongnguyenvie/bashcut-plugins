"""Scene parsing and timing ported from Editor-AI-App; no renderer or UI dependencies."""
import re, json, subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from .scene_motion import normalize_motion

def parse_srt_time(time_str: str) -> float:
    """Chuyển đổi chuỗi thời gian SRT (HH:MM:SS,mmm hoặc .mmm) sang giây float."""
    time_str = time_str.strip()
    match = re.match(r"^(\d+):(\d+):(\d+)[,\.](\d+)$", time_str)
    if not match:
        raise ValueError(f"Định dạng thời gian không hợp lệ: '{time_str}'")
    hours, minutes, seconds, millis = match.groups()
    if int(minutes) > 59 or int(seconds) > 59:
        raise ValueError("SRT minutes and seconds must be 0–59.")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / (10 ** len(millis))

def format_time(seconds: float) -> str:
    """Format số giây thành chuỗi MM:SS.mmm hoặc HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{secs:06.3f}"
    return f"{mins:02d}:{secs:06.3f}"

def parse_srt_file(srt_path: Path) -> Dict[int, Dict[str, Any]]:
    """Strict parsing: malformed/duplicate cues never silently disappear from a build."""
    if not srt_path.is_file():
        raise ValueError("Choose an existing SRT file.")
    if srt_path.stat().st_size > 4 * 1024 * 1024:
        raise ValueError("SRT is larger than 4 MiB.")
    content = srt_path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", content.strip())
    result = {}
    for index, block in enumerate(blocks, start=1):
        lines = block.splitlines()
        if not lines:
            raise ValueError("SRT contains no captions.")
        sub_id = int(lines.pop(0)) if lines[0].strip().isdigit() else index
        if sub_id in result or len(lines) < 2:
            raise ValueError("SRT cue is incomplete or its ID is duplicated.")
        timing = lines.pop(0).split("-->")
        if len(timing) != 2:
            raise ValueError("SRT cue timing is invalid.")
        start, end = map(parse_srt_time, timing)
        if end <= start:
            raise ValueError("SRT cue must have positive duration.")
        text = "\n".join(lines)
        if not text.strip():
            raise ValueError("SRT cue text is empty.")
        result[sub_id] = dict(id=sub_id,start=start,end=end,text=text)
    return result

def get_audio_duration(ffmpeg_exe: str, audio_path: Path) -> float:
    """Lấy tổng thời lượng (giây) của file âm thanh qua ffmpeg."""
    cmd = [ffmpeg_exe, "-i", str(audio_path)]
    proc = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", proc.stderr)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"Không thể đo thời lượng của file âm thanh: {audio_path}")

def parse_sub_string(s: str) -> List[int]:
    """Parse chuỗi như '1-3, 5' thành [1, 2, 3, 5]"""
    result = []
    parts = s.split(",")
    for p in parts:
        p = p.strip()
        if "-" in p:
            start_s, end_s = p.split("-", 1)
            try:
                result.extend(range(int(start_s), int(end_s) + 1))
            except ValueError:
                pass
        elif p.isdigit():
            result.append(int(p))
    return sorted(list(set(result)))

def parse_json_mapping(json_path: Path, available_subs: List[int]) -> List[Dict[str, Any]]:
    """
    Parse file JSON ánh xạ Scene sang phụ đề.
    Hỗ trợ các định dạng:
    Format 1 (Dict):
      {"SC01": [1, 2], "SC02": [3, 4]}
    Format 2 (List of objects):
      [{"id": "SC01", "subtitles": [1, 2]}, {"id": "SC02", "subtitles": [3]}]
    Format 3 (List of scenes chưa có subtitles):
      Tự động phân bổ phụ đề chia đều cho các scenes.
    Format 4 (List of scenes có start_at/end_at):
      Dùng mốc cắt chính xác từ JSON, kể cả khi nhiều cảnh dùng cùng một subtitle.
    """
    if not json_path.exists():
        raise FileNotFoundError(f"File JSON không tồn tại: {json_path}")

    raw_data = json.loads(json_path.read_text(encoding="utf-8", errors="ignore"))
    return parse_json_data(raw_data, available_subs)


def parse_json_data(raw_data: Any, available_subs: List[int]) -> List[Dict[str, Any]]:
    """Phân tích dữ liệu JSON đã nạp sẵn theo schema kịch bản cảnh."""
    scenes = []

    timed_fields = (
        "id", "character", "character_info", "prompt",
        "subtitle_ids", "start_at", "end_at",
    )
    if isinstance(raw_data, list) and any(
        isinstance(item, dict) and any(
            field in item for field in ("character", "character_info", "start_at", "end_at")
        )
        for item in raw_data
    ):
        previous_end = None
        for index, item in enumerate(raw_data, start=1):
            if not isinstance(item, dict) or tuple(key for key in item if key != "motion") != timed_fields:
                raise ValueError("Mỗi cảnh phải có 7 trường bắt buộc theo thứ tự quy định.")
            if item["id"] != f"SC{index:02d}":
                raise ValueError(f"ID cảnh thứ {index} phải là SC{index:02d}.")
            if not all(isinstance(item[field], str) for field in ("character", "character_info", "prompt")):
                raise ValueError("character, character_info và prompt phải là chuỗi.")
            subs = item["subtitle_ids"]
            if not isinstance(subs, list) or any(type(sub_id) is not int for sub_id in subs):
                raise ValueError("subtitle_ids phải là mảng số nguyên.")
            start_at = item["start_at"]
            end_at = item["end_at"]
            time_pattern = r"\d{2}:\d{2}:\d{2},\d{3}"
            if not isinstance(start_at, str) or not re.fullmatch(time_pattern, start_at):
                raise ValueError(f"start_at của {item['id']} không đúng định dạng HH:MM:SS,mmm.")
            if index == 1 and start_at != "00:00:00,000":
                raise ValueError("SC01 phải bắt đầu tại 00:00:00,000.")
            if previous_end is not None and start_at != previous_end:
                raise ValueError(f"start_at của {item['id']} phải bằng end_at của cảnh trước.")
            is_last = index == len(raw_data)
            if is_last:
                if end_at != "AUDIO_END":
                    raise ValueError("Cảnh cuối phải có end_at là AUDIO_END.")
            elif not isinstance(end_at, str) or not re.fullmatch(time_pattern, end_at):
                raise ValueError(f"end_at của {item['id']} không đúng định dạng HH:MM:SS,mmm.")
            if not is_last and parse_srt_time(end_at) <= parse_srt_time(start_at):
                raise ValueError(f"end_at của {item['id']} phải sau start_at.")
            if available_subs and any(sub_id not in available_subs for sub_id in subs):
                raise ValueError(f"{item['id']} tham chiếu subtitle_id không có trong SRT.")
            scenes.append({
                "id": item["id"], "prompt": item["prompt"],
                "subtitles": subs, "start_at": start_at, "end_at": end_at,
                "motion": normalize_motion(item.get("motion")),
            })
            previous_end = end_at
        return scenes

    if isinstance(raw_data, dict):
        for sc_id, subs in raw_data.items():
            if isinstance(subs, int):
                subs = [subs]
            elif isinstance(subs, str):
                subs = parse_sub_string(subs)
            scenes.append({
                "id": str(sc_id).strip(),
                "subtitles": sorted(list(subs))
            })
    elif isinstance(raw_data, list):
        for idx, item in enumerate(raw_data, start=1):
            if isinstance(item, dict):
                sc_id = item.get("id") or item.get("scene") or item.get("name") or f"SC{idx:02d}"
                subs = (
                    item.get("subtitles")
                    or item.get("subtitle_ids")
                    or item.get("subs")
                    or item.get("sub_ids")
                    or []
                )
                if isinstance(subs, int):
                    subs = [subs]
                elif isinstance(subs, str):
                    subs = parse_sub_string(subs)
                scenes.append({
                    "id": str(sc_id).strip(),
                    "prompt": item.get("prompt", ""),
                    "subtitles": sorted(list(subs)),
                    "motion": normalize_motion(item.get("motion")),
                })
            elif isinstance(item, str):
                scenes.append({"id": item.strip(), "subtitles": []})

    if not scenes:
        return []

    # Nếu tất cả scenes đều chưa có subtitles
    has_subs = any(len(s.get("subtitles", [])) > 0 for s in scenes)
    if not has_subs and available_subs:
        num_scenes = len(scenes)
        sub_count = len(available_subs)
        chunk_size = sub_count // num_scenes
        remainder = sub_count % num_scenes
        
        cur = 0
        for i in range(num_scenes):
            take = chunk_size + (1 if i < remainder else 0)
            assigned = available_subs[cur:cur + take]
            cur += take
            scenes[i]["subtitles"] = assigned

    return scenes

def find_image_for_scene(image_dir: Path, scene_id: str, scene_idx: int) -> Optional[Path]:
    """
    Tìm file ảnh tương ứng với scene_id:
    - Tách tiền tố trước dấu gạch dưới '_' hoặc '-' (ví dụ 'SC01_20260910165946_clean.png' -> 'SC01')
    - Đối chiếu chính xác với ID cảnh (SC01).
    - Hỗ trợ tìm cả trong thư mục chính và thư mục con (ví dụ images/cleaned hoặc images/clean).
    - Ưu tiên chọn ảnh bản 'clean' nếu có nhiều phiên bản.
    """
    valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    
    all_images = []
    if image_dir.is_dir():
        for f in sorted(image_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in valid_exts:
                all_images.append(f)
        for sub in sorted(image_dir.iterdir()):
            if sub.is_dir():
                for f in sorted(sub.iterdir()):
                    if f.is_file() and f.suffix.lower() in valid_exts:
                        all_images.append(f)

    norm_target = scene_id.upper().strip()
    target_num_match = re.search(r"\d+", norm_target)
    target_num = int(target_num_match.group()) if target_num_match else None

    matched_images = []
    for img in all_images:
        stem_upper = img.stem.upper()
        prefix = re.split(r"[-_]", stem_upper)[0].strip()

        if prefix == norm_target:
            matched_images.append(img)
            continue

        prefix_num_match = re.search(r"\d+", prefix)
        if prefix_num_match and target_num is not None:
            if int(prefix_num_match.group()) == target_num:
                matched_images.append(img)
                continue

        if re.match(rf"^{re.escape(norm_target)}(?:[-_.]|$)", stem_upper):
            matched_images.append(img)
            continue

    if matched_images:
        clean_images = [img for img in matched_images if "clean" in img.stem.lower()]
        if clean_images:
            return clean_images[0]
        return matched_images[0]

    # Fallback: theo thứ tự index (1-based)
    direct_files = sorted([f for f in image_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_exts])
    if 0 <= scene_idx - 1 < len(direct_files):
        return direct_files[scene_idx - 1]

    return None

def compute_timeline(
    scenes: List[Dict[str, Any]],
    subtitles: Dict[int, Dict[str, Any]],
    total_audio_duration: float,
    image_dir: Path
) -> List[Dict[str, Any]]:
    """
    Tính toán mốc thời gian hiển thị từng ảnh:
    - Cảnh có start_at/end_at: dùng trực tiếp điểm cắt từ JSON.
    - Cảnh 1: từ giây 0.000 đến lúc phụ đề đầu tiên của cảnh 2 bắt đầu.
    - Cảnh thứ i: từ phụ đề đầu tiên của cảnh i đến phụ đề đầu tiên của cảnh (i+1).
    - Cảnh cuối cùng: từ phụ đề đầu tiên của nó đến hết thời lượng file âm thanh.
    """
    timeline = []
    num_scenes = len(scenes)

    # Bước 1: Xác định start_time của từng scene
    for i, sc in enumerate(scenes):
        sc_id = sc["id"]
        subs = sc.get("subtitles", [])
        
        img_path = find_image_for_scene(image_dir, sc_id, i + 1)

        if "start_at" in sc:
            start_time = parse_srt_time(sc["start_at"])
        elif i == 0:
            start_time = 0.0
        else:
            if subs and subs[0] in subtitles:
                start_time = subtitles[subs[0]]["start"]
            else:
                prev_start = timeline[i - 1]["start"] if timeline else 0.0
                start_time = prev_start + 1.0

        timeline.append({
            "index": i + 1,
            "id": sc_id,
            "subtitles": subs,
            "image": img_path,
            "motion": normalize_motion(sc.get("motion")),
            "start": start_time,
            "end": 0.0,
            "duration": 0.0
        })

    # Bước 2: Xác định end_time và duration cho từng scene
    for i in range(num_scenes):
        if "end_at" in scenes[i] and scenes[i]["end_at"] != "AUDIO_END":
            timeline[i]["end"] = parse_srt_time(scenes[i]["end_at"])
        elif "end_at" in scenes[i]:
            timeline[i]["end"] = total_audio_duration
        elif i < num_scenes - 1:
            timeline[i]["end"] = timeline[i + 1]["start"]
        else:
            timeline[i]["end"] = max(total_audio_duration, timeline[i]["start"] + 0.5)

        dur = round(timeline[i]["end"] - timeline[i]["start"], 3)
        if dur <= 0 and "end_at" in scenes[i]:
            raise ValueError(f"Thời lượng âm thanh không đủ cho {scenes[i]['id']}.")
        if dur <= 0:
            dur = 0.5
            timeline[i]["end"] = timeline[i]["start"] + dur
        timeline[i]["duration"] = dur

    return timeline

