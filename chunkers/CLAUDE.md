# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Scope: the `chunkers/` package — text-chunking strategies used to build the handbook RAG index (`../rag_data_populate.py`).

## Commands

Run everything from the **repo root** (`lesson-06-homework/`), not from `chunkers/`. `pyproject.toml` sets `pythonpath = ["."]` and `testpaths = ["tests"]`, and all imports are absolute (`from chunkers.chunker import Chunker`), so running from inside `chunkers/` breaks imports.

```bash
# venv lives at repo root (Windows layout)
.venv/Scripts/python -m pip install -r requirements.txt -r requirements-dev.txt

.venv/Scripts/python -m pytest tests/chunkers                                   # all chunker tests
.venv/Scripts/python -m pytest tests/chunkers/test_basic_chunker.py::test_chunk_multiple_chunks   # single test
```

Python 3.11+ is required (`enum.StrEnum`, `match`). There is no `__init__.py` — `chunkers` is an implicit namespace package.

## Architecture
- `chunker.py` — abstract `Chunker` base with a single `chunk(text)` method and the shared `OVERLAP_WORDS = 50` constant.
- `basic_chunker.py`, `doc_chunker.py`, `sentence_chunker.py`, `semantic_chunker.py` — one strategy per file. Each module docstring states the intended use case and splitting rule (e.g. sentence: 3–8 sentences per chunk; doc: see DocChunker spec below; semantic: split on topic change). Only `BasicChunker` is implemented (250-word sliding window with 50-word overlap); the other three are stubs returning `None`.
- `chunker_factory.py` — `ChunkType` (`StrEnum` with `auto()`, so values are lowercase names) and `ChunkerFactory`, which picks the concrete chunker via `match` in `__init__` and delegates through `make_chunks(text)`.

## Chunker specs

All chunker implementations inherit from the abstract `Chunker` base class and return `list[str]`.

### DocChunker

Splits Markdown by structure. `CHUNK_WORDS = 250` (target size).

**1. Headings (first pass)**
- Split on `#`, `##` and `###` heading lines. A section runs from its heading (inclusive) to the next heading of any level (exclusive), or to the end of the document.
- Text between a heading and its first child heading becomes its own section.
- A heading with no text of its own (immediately followed by a child heading, e.g. `# Benefits and Perks` → `## Eligibility`) creates no chunk.
- Drop the YAML front matter (`---` … `---`) at the top of the file.
- If the document has no headings, treat the whole document as a single section.

**2. Heading path**
- Every chunk starts with its full heading path, e.g. `Titles for QA > Levels > QA1, Associate QA Analyst`.

**3. Oversized sections (second pass, only if the section is longer than 250 words)**
- Split the section at `\n\n` boundaries into pieces (paragraphs and bullet blocks).
- A bullet block is a run of consecutive lines starting with `- `, `* ` or `+ ` (a single bullet counts).
- Paragraphs: pack consecutive paragraphs into one chunk until adding the next one would exceed 250 words, then start a new chunk.
- Bullet blocks:
  - under 250 words → append to the previous chunk, even if that pushes it over 250 (soft limit). This keeps the intro line (e.g. `Typical QA1 expectations:`) with its bullets.
  - 250 words or more → its own chunk; move the intro line (the paragraph right before the block) into the bullet chunk.
  - if the section starts with a bullet block (no previous chunk) → start a new chunk.

**4. Overlap**
- Use `OVERLAP_WORDS = 50` (inherited from `Chunker`): when a section is split into several chunks, each chunk after the first starts (after the heading path) with the last 50 words of the previous chunk.
- No overlap across different sections — each heading section starts clean.

Callers:
- `rag_data_populate.py` iterates over **every** `ChunkType`, calls `ChunkerFactory(chunk_type).make_chunks(file_text)` per handbook file, then embeds the chunks via Bedrock. So a stub chunker returning `None` will crash the populate script — every chunker must return a `list[str]`. Note the script currently writes each chunk type to the same `data/handbook.faiss` / `handbook.json`, so the last type wins.
- `rag_data_populate.py` still contains its own `chunk_words()` duplicate of `BasicChunker`'s logic.

## Conventions / gotchas

- `chunk()` is annotated `text: List[str]` but actually receives a single `str` (file contents) and returns `list[str]`. Similarly `OVERLAP_WORDS` is annotated `Final[str]` but is an `int`. Trust the runtime behavior, not the hints.
- Adding a new chunker requires: a new module subclassing `Chunker`, a new `ChunkType` member, a new `case` in `ChunkerFactory.__init__`, and updating `tests/chunkers/test_chunker_factory.py` — `test_chunk_type_values_are_lowercase_names` asserts the exact enum values **in order**, and the parametrized factory test lists every type.
- Tests live in `tests/chunkers/test_<module>.py`, use plain pytest functions with `# arrange / # act / # assert` comments, and mock collaborators with `unittest.mock.patch.object`.
