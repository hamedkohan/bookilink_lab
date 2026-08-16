import numpy as np

from bookilink.core import Chunk
from bookilink.store import BookStore


def test_store_and_vector_search(tmp_path):
    db = tmp_path / "test.db"
    store = BookStore(str(db))
    chunks = [
        Chunk(0, "cats", "page 1"),
        Chunk(1, "dogs", "page 2"),
    ]
    store.save_book(
        book_id="abc",
        title="Test",
        author=None,
        filename="test.pdf",
        file_type="pdf",
        file_hash="hash",
        chunks=chunks,
        embeddings=[[1.0, 0.0], [0.0, 1.0]],
    )
    hits = store.search_by_vector("abc", [1.0, 0.0], top_k=1)
    assert hits[0].text == "cats"
    assert np.isclose(hits[0].score, 1.0)
