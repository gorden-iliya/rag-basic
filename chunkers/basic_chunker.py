"""Basic chunker - used for simple demos / baseline. splits every 300-800 tokens"""

from typing import List

from chunkers.chunker import Chunker

class BasicChunker(Chunker):
    CHUNK_WORDS = 250

    def chunk(self, text: List[str]):
        words = text.split()
        step = self.CHUNK_WORDS - self.OVERLAP_WORDS
        chunks = []
        for start in range(0, len(words), step):
            chunks.append(" ".join(words[start:start + self.CHUNK_WORDS]))
            if start + self.CHUNK_WORDS > len(words):
                break
        return chunks