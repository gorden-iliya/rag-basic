from unittest.mock import patch

import pytest

from chunkers.basic_chunker import BasicChunker
from chunkers.chunker_factory import ChunkerFactory, ChunkType
from chunkers.doc_chunker import DocChunker
from chunkers.semantic_chunker import SemanticChunker
from chunkers.sentence_chunker import SentenceChunker


def test_chunk_type_values_are_lowercase_names():
    # Arrange / Act
    values = [chunk_type.value for chunk_type in ChunkType]

    # Assert
    assert values == ["basic", "doc", "sentence", "semantic"]


@pytest.mark.parametrize(
    "chunk_type, expected_class",
    [
        (ChunkType.BASIC, BasicChunker),
        (ChunkType.DOC, DocChunker),
        (ChunkType.SENTENCE, SentenceChunker),
        (ChunkType.SEMANTIC, SemanticChunker),
    ],
)
def test_factory_creates_matching_chunker(chunk_type, expected_class):
    factory = ChunkerFactory(chunk_type)

    assert isinstance(factory._chunker, expected_class)


def test_make_chunks_delegates_to_chunker():
    # Replace the real chunk() so this test doesn't depend on its implementation
    with patch.object(BasicChunker, "chunk", return_value=["a", "b"]) as fake_chunk:
        factory = ChunkerFactory(ChunkType.BASIC)
        result = factory.make_chunks("some text")

    fake_chunk.assert_called_once_with("some text")
    assert result == ["a", "b"]
