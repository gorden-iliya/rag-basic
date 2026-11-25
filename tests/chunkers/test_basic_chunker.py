from unittest.mock import patch

import pytest

from chunkers.basic_chunker import BasicChunker

STRING_100_WORDS = ("""
    ## Eligibility
    NovaOps benefits are designed for a remote-first company with employees in Israel, Germany,
    the United Kingdom, and the United States. Full-time employees are eligible for the company
    benefits in their country from their first day unless a local plan document says otherwise.
    Contractors receive the equipment and access needed for the engagement, but do not receive
    employee insurance, retirement, or leave benefits.

    Questions about your own eligibility should go to People Operations at
    sara.cohen@novaops.example or through [BambooHR](https://bamboohr.novaops.example).
    If a local law provides a stronger benefit than this handbook, NovaOps follows the local law.
    If a signed employment agreement, local plan document, or statutory rule conflicts with this handbook,
    People Operations confirms which rule controls before payroll or reimbursement is processed.
"""
)

def test_chunk_less_than_chunk_max():
    # arrange
    SINGLE_CHUNK = 1
    chunker = BasicChunker()

    # act
    chunks = chunker.chunk(STRING_100_WORDS)
    # test
    assert len(chunks) == SINGLE_CHUNK

def test_chunk_multiple_chunks():
    # arrange
    TEXT_LENGTH_MORE_THAN_SINGLE_CHUNK = f"{STRING_100_WORDS} {STRING_100_WORDS} {STRING_100_WORDS}"
    TWO_CHUNKS = 2
    chunker = BasicChunker()

    # act
    chunks = chunker.chunk(TEXT_LENGTH_MORE_THAN_SINGLE_CHUNK)
    # test
    assert len(chunks) == TWO_CHUNKS