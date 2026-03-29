from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def _interpolate_missing_timestamps(words: list, seg_start: float, seg_end: float) -> list:
    """
    Ensures every word has start/end timestamps.
    Words missing timestamps get interpolated from neighbours or segment bounds.
    This is the LAST LINE OF DEFENCE against silent word drops.
    """
    if not words:
        return words

    result = []
    for i, w in enumerate(words):
        w = dict(w)  # shallow copy
        if 'start' not in w or 'end' not in w or w.get('start') is None or w.get('end') is None:
            # Find previous word with timestamps
            prev_end = seg_start
            for j in range(i - 1, -1, -1):
                if 'end' in result[j] and result[j]['end'] is not None:
                    prev_end = result[j]['end']
                    break

            # Find next word with timestamps
            next_start = seg_end
            for j in range(i + 1, len(words)):
                if 'start' in words[j] and words[j]['start'] is not None:
                    next_start = words[j]['start']
                    break

            # Count consecutive unaligned words in this gap
            gap_count = 1
            for j in range(i + 1, len(words)):
                if 'start' not in words[j] or words[j].get('start') is None:
                    gap_count += 1
                else:
                    break

            gap_dur = (next_start - prev_end) / max(gap_count, 1)
            offset = 0
            for j in range(i, -1, -1):
                if j < len(result) and ('start' not in result[j] or result[j].get('_interpolated')):
                    offset += 1
                else:
                    break

            w['start'] = round(prev_end + offset * gap_dur, 3)
            w['end'] = round(w['start'] + gap_dur, 3)
            w['_interpolated'] = True
            logger.debug(f"Interpolated timestamp for word '{w.get('word', '')}': {w['start']}-{w['end']}")

        result.append(w)

    return result


def format_timestamp(seconds: float, use_comma: bool = True) -> str:
    """
    Formats seconds into WebVTT/SRT timestamp format.
    use_comma: True for SRT (00:00:00,000), False for WebVTT (00:00:00.000)
    """
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds_int = divmod(remainder, 60)
    milliseconds = int(td.microseconds / 1000)
    
    separator = ',' if use_comma else '.'
    return f"{hours:02d}:{minutes:02d}:{seconds_int:02d}{separator}{milliseconds:03d}"

def generate_srt(segments: list, word_level: bool = True) -> str:
    """Generates SubRip Text (SRT) format. Supports word-level resolution."""
    lines = []
    index = 1
    
    for seg in segments:
        if word_level and 'words' in seg:
            seg_start = seg.get('start', 0)
            seg_end = seg.get('end', seg_start + 1)
            words = _interpolate_missing_timestamps(seg['words'], seg_start, seg_end)
            for w in words:
                start = format_timestamp(w['start'], use_comma=True)
                end = format_timestamp(w['end'], use_comma=True)
                word_text = w.get('word', '').strip()
                if not word_text:
                    continue
                lines.append(f"{index}")
                lines.append(f"{start} --> {end}")
                lines.append(f"{word_text}")
                lines.append("")
                index += 1
        else:
            start = format_timestamp(seg['start'], use_comma=True)
            end = format_timestamp(seg['end'], use_comma=True)
            text = seg['text'].strip()
            if not text:
                continue
            lines.append(f"{index}")
            lines.append(f"{start} --> {end}")
            lines.append(f"{text}")
            lines.append("")
            index += 1
            
    return "\n".join(lines)

def generate_vtt(segments: list, word_level: bool = True) -> str:
    """Generates Web Video Text Tracks (WebVTT) format. Supports word-level resolution."""
    lines = ["WEBVTT", ""]
    for seg in segments:
        if word_level and 'words' in seg:
            seg_start = seg.get('start', 0)
            seg_end = seg.get('end', seg_start + 1)
            words = _interpolate_missing_timestamps(seg['words'], seg_start, seg_end)
            for w in words:
                start = format_timestamp(w['start'], use_comma=False)
                end = format_timestamp(w['end'], use_comma=False)
                word_text = w.get('word', '').strip()
                if not word_text:
                    continue
                lines.append(f"{start} --> {end}")
                lines.append(f"{word_text}")
                lines.append("")
        else:
            start = format_timestamp(seg['start'], use_comma=False)
            end = format_timestamp(seg['end'], use_comma=False)
            text = seg['text'].strip()
            if not text:
                continue
            lines.append(f"{start} --> {end}")
            lines.append(f"{text}")
            lines.append("")
        
    return "\n".join(lines)
