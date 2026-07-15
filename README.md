# learn-by-building-samples

Static, worked examples of the exercises produced by the **[learn-by-building](https://github.com/csacademy-ma/learn-by-building)** Claude skill — read-only walkthroughs you can follow on your own, no AI required.

Each exercise below is a single markdown file containing every stage of a "build the concept from scratch" project: the concept explained just enough to attempt it, a function/class signature with worked examples, and a pointer to the matching test file. A `starter/` folder has the stub code to fill in, and a `tests/` folder has the (leetcode-style) automated tests that check your work, stage by stage.

**Want the interactive version instead?** These markdown files are frozen snapshots — there's no one to ask for a hint, no one to check your reasoning, and no one to grade your finished code. For that, install the **[learn-by-building](https://github.com/csacademy-ma/learn-by-building)** in Claude and just ask to learn something by building it (e.g. "help me understand hash tables by implementing one") — it'll design a project like these live, tailored to your time budget and experience level, and review your code when you're done.

## Exercises

| Exercise | Domain | Stages | Est. time |
|---|---|---|---|
| [CNN from scratch](exercises/cnn-from-scratch/EXERCISE.md) | ML / math | 7 | 1-2 hours |
| [Multithreading from scratch](exercises/multithreading-from-scratch/EXERCISE.md) | Concurrency | 4 | 45-60 min |
| [Hash table from scratch](exercises/hash-table-from-scratch/EXERCISE.md) | Data structures | 6 | 60-90 min |
| [Digital signatures from scratch](exercises/digital-signatures-from-scratch/EXERCISE.md) | Cryptography | 6 | 90 min - 2 hours |

## How to use one

1. Open the exercise's `EXERCISE.md` and read Stage 1.
2. Open the matching file in that exercise's `starter/` folder and implement the function/class described — don't peek at later stages first.
3. Run that stage's tests (see the exact command in the exercise's `EXERCISE.md`, or just run everything with `pytest tests/ -v` from inside the exercise's folder).
4. Once the tests pass, move to the next stage. Repeat until you hit the "bridge to the real library" stage at the end.

Each exercise folder is self-contained — the only shared dependency across all of them is Python 3.10+ and `pytest` (`pip install pytest`); a couple also need `numpy` (noted at the top of their `EXERCISE.md`).

## Repo structure

```
exercises/
└── <exercise-name>/
    ├── EXERCISE.md      <- the full walkthrough, every stage
    ├── starter/         <- one file per stage, signature + TODO for you to fill in
    └── tests/           <- one test file per stage, run with pytest
```

## License

MIT — see `LICENSE`.
