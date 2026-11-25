"""Doc chunker - used for documents with clear structure. split on \n\n, headings, bullets, sentence ends"""

from typing import List

from chunkers.chunker import Chunker

class DocChunker(Chunker):
    def chunk(self, text: List[str]):
        pass