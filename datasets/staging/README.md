---
configs:
- config_name: rc13
  default: true
  data_files:
  - split: train
    path: data/rc13/*.parquet
- config_name: pre-rc13
  data_files:
  - split: train
    path: data/shard-*.parquet
---

Raw generator output behind [procedural-pile](https://huggingface.co/datasets/reasoning-core/procedural-pile), one configuration per build, before deduplication and the train/test split.

```python
load_dataset("reasoning-core/staging", "rc13", split="train", streaming=True)
```
