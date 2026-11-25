# CLAUDE.md - conventions for the data/handbook *.md files test rubrics

- this folder contains `rubrics.json`, a list of rubrics to test the answers
- each rubric will contain a question that may have an answer in one of the *.md data files in data/handbook
- `rubrics.json` is a JSON array of objects: `{"question": "...", "answer": "..."}`
- `answer` is the **expected source**, not the answer text.
- the list should contain 50 records of question-answer: ~35 answered by a handbook file, ~10 "no-content-found", ~5 "content-not-relevant".
- cover every file in data/handbook at least once.
- Question answered by a handbook file → `answer` is the file name, e.g. `"benefits-and-perks.md"`.
- if the answer is present in more than one file, the answer must be the single file with the highest relevance score for the question (the file that covers the topic most directly and in the most detail)
- Question about NovaOps, but not covered in any handbook file → `"no-content-found"`.
- Chit-chat or anything unrelated to NovaOps (e.g. "hello", "what's the weather?") → `"content-not-relevant"`.
