#!/usr/bin/env python3
"""
Translate lyrics to Chinese with line-by-line format
Uses modular translators from modules.translators
"""

import io
import re
import sys
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import from modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.translators import TranslationManager
from modules.utils import load_config, is_section_marker, parse_lyrics_file


def main():
    if len(sys.argv) < 2:
        print("Usage: python translate_lyrics.py <input_file> [output_path]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else Path(input_file).parent
    config = load_config()

    print(f"Reading: {input_file}")

    result = parse_lyrics_file(input_file)
    if not result:
        sys.exit(1)

    artist, song, lines = result
    print(f"Found: {artist} - {song}")
    print(f"Lines: {len(lines)}")

    # Filter lines to translate (skip empty and section markers)
    to_translate = []
    for line in lines:
        stripped = line.strip()
        if stripped and not is_section_marker(stripped):
            to_translate.append(stripped)

    print(f"Translatable: {len(to_translate)}")

    # Initialize translation manager
    translation_config = config.get("translation", {})
    manager = TranslationManager(translation_config)

    print(f"Using: {manager.primary_translator}")
    print(f"Available: {', '.join(manager.available_translators)}")

    # Translate
    translations = manager.translate_batch(to_translate, delay=0.3)

    # Build output - FIX: section markers only appear once
    output_lines = []
    trans_idx = 0

    for line in lines:
        stripped = line.strip()

        if not stripped:
            output_lines.append('')  # Empty line for paragraph break
        elif is_section_marker(stripped):
            output_lines.append(stripped)  # Section marker - only once!
            output_lines.append('')  # Empty line after marker
        else:
            orig = to_translate[trans_idx]
            trans = translations.get(orig, orig)
            output_lines.append(orig)
            output_lines.append(trans)
            trans_idx += 1

    # Save
    safe_artist = re.sub(r'[<>:"/\\|?*]', '', artist).strip()
    safe_song = re.sub(r'[<>:"/\\|?*]', '', song).strip()
    filename = f"{safe_artist} - {safe_song} (translated chinese).txt"
    filepath = Path(output_path) / filename
    Path(output_path).mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"[OK] Saved: {filepath}")


if __name__ == "__main__":
    main()
