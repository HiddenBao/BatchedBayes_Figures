# BatchedBayes_Personal

Analysis and figure work for the BatchedBayes microemulsion campaigns.

The Bayesian optimiser itself is **not** in this repo — it lives upstream at
[mcgillresearchgroup/BatchedBayes](https://github.com/mcgillresearchgroup/BatchedBayes).
This repo keeps the measured data, the scoring and analysis pipeline, and the figure suites.

See [CLAUDE.md](CLAUDE.md) for the layout, the campaign distinctions, and how to query upstream.

## Run

```
conda run -n BatchedBayes python analysis/build_score_datasets.py
conda run -n BatchedBayes python average_dataset_scores.py
conda run -n BatchedBayes python analysis/export_leaderboard_data.py

conda run -n BatchedBayes marimo edit analysis/campaign_comparison.py
```
