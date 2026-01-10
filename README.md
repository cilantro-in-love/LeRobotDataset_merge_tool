# LeRobotDataset 数据集合并工具

一个用于将多个 LeRobotDataset 合并为单个统一 LeRobotDataset 的 Python 工具。该工具能够正确处理视频文件、parquet 数据文件和元数据，确保合并后的数据集完整性。

## 功能特性

- ✅ 合并多个 LeRobot 数据集，同时保留数据结构
- ✅ 自动处理 episode 索引偏移
- ✅ 更新元数据（info.json、episodes.jsonl、episodes_stats.jsonl）
- ✅ 复制和重命名视频文件及 parquet 数据文件
- ✅ 维护正确的全局帧索引
- ✅ 通过路径变量进行简单配置

## 数据集结构

该工具期望的 LeRobot 数据集结构如下：

```
lerobot_dataset/
├── data/
│   └── chunk-000/
│       ├── episode_000000.parquet
│       ├── episode_000001.parquet
│       └── ...
├── videos/
│   └── chunk-000/
│       └── observation.images.front/
│           ├── episode_000000.mp4
│           ├── episode_000001.mp4
│           └── ...
└── meta/
    ├── info.json
    ├── episodes.jsonl
    └── episodes_stats.jsonl
```

## 安装

除 Python 标准库外无需额外依赖：

```bash
git clone https://github.com/yourusername/lerobot-dataset-merge-tool.git
cd lerobot-dataset-merge-tool
```

## 使用方法

### 完整数据集合并

使用 `Merge_LerobotDataset.py` 将整个源数据集合并到目标数据集：

```python
# 在脚本中编辑这些路径
src_dir = "/path/to/source/lerobot_dataset"  # 源数据集路径
dst_dir = "/path/to/destination/lerobot_dataset"  # 目标数据集路径

# 运行合并
python Merge_LerobotDataset.py
```

### 部分视频和数据合并

使用 `data_video_merge.py` 可以分别合并`videos`和`data`，需要分别指定源和目标路径，以及源和目标的起始和结束索引。

```python
# 在脚本中配置
src_dir = "/path/to/source/videos"  # 源视频路径
dst_dir = "/path/to/destination/videos"  # 目标视频路径
src_start = 0      # 源起始 episode
src_end = 26       # 源结束 episode
dst_start = 41     # 目标起始索引

python data_video_merge.py
```

### 手动元数据合并

使用 `meta_merge.py` 仅合并元数据文件并自定义偏移量：
可以分别合并 `episodes.jsonl` 和 `episodes_stats.jsonl` 文件，需要指定 `episode_offset` `global_index_offset`。
```python
# 配置偏移量
source_file = "/path/to/source/meta/episodes_stats.jsonl"  # 源文件
target_file = "/path/to/destination/meta/episodes_stats.jsonl"  # 目标文件
episode_offset = 41  # episode 偏移量
global_index_offset = 35540  # 全局索引偏移量

python meta_merge.py
```

## 重要说明

⚠️ **备份数据**：合并前务必备份目标数据集

⚠️ **Episode 偏移**：工具会根据目标数据集中现有的 episode 自动计算偏移量

⚠️ **全局帧索引**：帧索引会被正确偏移，以保持合并数据集的连续性

⚠️ **文件操作**：脚本使用 `shutil.copy2` 来保留元数据。如果想移动而非复制，可改为 `shutil.move`

## 使用示例

```bash
# 将新数据集合并到现有数据集
python Merge_LerobotDataset.py

```
## English Version

[Click here for English README](README_EN.md)