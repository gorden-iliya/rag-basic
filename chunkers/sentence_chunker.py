"""Sentence chunker - used for explanatory text. 3-8 sentences per chunk"""

from typing import List

from chunkers.chunker import Chunker

class SentenceChunker(Chunker):
    def chunk(self, text: List[str]):
        pass