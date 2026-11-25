"""Semantic chunker - used for policies, legal, research. Split where the topic changes"""

from typing import List

from chunkers.chunker import Chunker

class SemanticChunker(Chunker):
    def chunk(self, text: List[str]):
        pass