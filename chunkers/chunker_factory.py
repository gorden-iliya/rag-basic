from enum import StrEnum, auto
from typing import List

from chunkers.chunker import Chunker
from chunkers.basic_chunker import BasicChunker
from chunkers.doc_chunker import DocChunker
from chunkers.semantic_chunker import SemanticChunker
from chunkers.sentence_chunker import SentenceChunker

"""Chunk type enum"""
class ChunkType(StrEnum):
    BASIC = auto()
    DOC = auto()
    SENTENCE = auto()
    SEMANTIC = auto()


"""Data chunk factory class for handling various chunk types"""
class ChunkerFactory:

    _chunker: Chunker

    def make_chunks(self, text: List[str]):
        return self._chunker.chunk(text)

    def __init__(self, chunk_type: ChunkType):
        match chunk_type:
            case ChunkType.BASIC:
                self._chunker = BasicChunker()
            case ChunkType.DOC:
                self._chunker = DocChunker()
            case ChunkType.SENTENCE:
                self._chunker = SentenceChunker()
            case ChunkType.SEMANTIC:
                self._chunker = SemanticChunker()
