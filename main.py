#!/usr/bin/env python3
"""THALASSA poster: hand the finished image to the grader, unchanged.

The picture itself lives beside this file as entry.png. It was painted
beforehand by the offline script draw_variants.py (variant B, in the
build folder) and this program only delivers those exact bytes: read
them, check they are the 1024x1024 PNG we expect and no bigger than
1 MiB, and write them where the grader looks (MAKEFUN_OUTPUT_DIR when
it is set, /output otherwise).

THALASSA is a travel poster for a place that does not exist: a dusk
sea under a crescent moon, and one landmark, a sleeping whale whose
back is an island — a lighthouse, three pines and two warm windows on
it, a little rowboat with a lantern below. The name is set huge across
the top with one short line underneath, so it still reads at the
300px thumbnail size the judge sees first.

Pure Python 3.13 standard library, no network, no randomness, no
clock: two runs write identical bytes. On success it prints the byte
count and sha256 and exits zero; on any problem it explains itself on
stderr and exits one.
"""

import hashlib
import os
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024
WANT = (1024, 1024)


def die(message):
    print("entry failed: " + message, file=sys.stderr)
    return 1


def png_dimensions(blob):
    """(width, height) from a PNG's IHDR chunk, or None when malformed."""
    if len(blob) < 33 or blob[:8] != PNG_MAGIC:
        return None
    if blob[12:16] != b"IHDR":
        return None
    width = int.from_bytes(blob[16:20], "big")
    height = int.from_bytes(blob[20:24], "big")
    depth = blob[24]
    colour = blob[25]
    if depth != 8 or colour != 2:
        return None
    return width, height


def main():
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    if not source.is_file():
        return die("entry.png is missing next to main.py")
    blob = source.read_bytes()
    if len(blob) > MAX_BYTES:
        return die("entry.png is %d bytes, over the 1 MiB limit"
                   % len(blob))
    size = png_dimensions(blob)
    if size is None:
        return die("entry.png is not a whole 8-bit RGB PNG")
    if size != WANT:
        return die("entry.png is %dx%d, want 1024x1024" % size)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    target.write_bytes(blob)
    # Write-verify: re-read what landed and confirm it is the same image.
    # A partial or interrupted write must never pass as a good delivery.
    landed = target.read_bytes()
    if hashlib.sha256(landed).hexdigest() != hashlib.sha256(blob).hexdigest():
        return die("wrote %s but the bytes on disk do not match entry.png"
                   % target)
    digest = hashlib.sha256(blob).hexdigest()
    print("wrote %d bytes to %s sha256 %s" % (len(blob), target, digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
