from bookilink.chunking import chunk_segments
from bookilink.core import Segment


def test_chunk_segments_preserves_locator():
    segments = [Segment(text=("Hello world. " * 500), locator="page 1", order_index=0)]
    chunks = chunk_segments(segments, target_chars=500, overlap_chars=50)
    assert len(chunks) > 1
    assert all(c.locator == "page 1" for c in chunks)
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))
