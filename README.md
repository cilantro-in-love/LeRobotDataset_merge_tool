# LeRobot 数据集合并工具

🤖 一个用于合并多个 LeRobot 数据集的综合工具包，自动管理索引并更新元数据。

## 📋 项目简介

本仓库提供了合并多个 LeRobot 格式数据集的工具，当你在不同时间段收集了多批机器人数据，需要将它们合并为一个完整的训练集。工具会自动处理所有必要的文件操作、索引调整和元数据更新。

## ✨ 主要特性

- ✅ **完整数据集合并**：合并数据文件（.parquet）、视频文件（.mp4）和所有元数据
- 🔢 **自动索引管理**：自动调整 episode 索引和全局帧索引
- 📊 **统计信息聚合**：重新计算并聚合数据集统计信息
- 🔄 **HuggingFace Hub 集成**：直接推送合并后的数据集到 HuggingFace Hub
- 🏷️ **版本标签**：为合并的数据集创建版本标签
- ✔️ **验证工具**：内置验证功能确保合并完整性

## 📁 文件结构

```
.
├── data_merge.py              # 🌟 最新版本 - 推荐使用
├── Merge_LerobotDataset.py    # 备选的合并实现
├── meta_merge.py              # 早期版本 - 仅元数据
├── data_video_merge.py        # 早期版本 - 仅数据和视频
└── create_tag.py              # HuggingFace Hub 标签工具
```

### 文件说明

| 文件 | 用途 | 状态 |
|------|------|------|
| `data_merge.py` | **主工具** - 完整的数据集合并器，带验证功能 | ⭐ 推荐 |
| `Merge_LerobotDataset.py` | 数据集合并的备选实现 | 备选 |
| `meta_merge.py` | 仅合并元数据文件（episodes_stats.jsonl） | 早期版本 |
| `data_video_merge.py` | 仅合并数据和视频文件 | 早期版本 |
| `create_tag.py` | 在 HuggingFace Hub 上创建版本标签 | 工具 |

## 🚀 快速开始

### 前置要求

```bash
pip install lerobot pandas jsonlines numpy huggingface-hub
```

### 基本使用

#### 方式一：使用 `data_merge.py`（推荐）

```python
from data_merge import merge_lerobot_datasets, verify_merged_dataset

# 定义源数据集
source_datasets = [
    "/path/to/dataset1",
    "/path/to/dataset2",
]

# 定义目标路径
target_repo = "your-username/merged-dataset"
target_root = "/path/to/output/merged-dataset"

# 合并数据集
merged_path = merge_lerobot_datasets(
    source_paths=source_datasets,
    target_repo_id=target_repo,
    target_root=target_root
)

# 验证合并后的数据集
verify_merged_dataset(str(merged_path))
```

#### 方式二：使用 `Merge_LerobotDataset.py`

```python
# 在脚本中配置路径
src_dir = "/path/to/source/dataset"
dst_dir = "/path/to/target/dataset"

# 运行脚本
python Merge_LerobotDataset.py
```

## 📖 详细使用说明

### 1. 合并多个数据集

主脚本 `data_merge.py` 提供了 `merge_lerobot_datasets()` 函数：

```python
merge_lerobot_datasets(
    source_paths=["/path/to/dataset1", "/path/to/dataset2"],
    target_repo_id="username/merged-dataset",
    target_root="/path/to/output"
)
```

**执行内容：**
- ✅ 验证数据集兼容性（fps、robot_type）
- 📦 复制并重命名所有 episode 文件
- 🎥 处理视频文件
- 🔢 更新 episode 索引和全局帧索引
- 📊 重新计算统计信息
- 💾 生成所有必需的元数据文件

### 2. 验证合并的数据集

```python
verify_merged_dataset(
    dataset_path="/path/to/merged-dataset",
    check_episodes=[0, 10, 20]  # 指定要检查的 episodes
)
```

验证内容包括：
- Episode 索引一致性
- 全局帧索引连续性
- 数据文件完整性

### 3. 推送到 HuggingFace Hub

```python
from data_merge import push_merged_dataset

push_merged_dataset(
    target_path="/path/to/merged-dataset",
    repo_id="username/merged-dataset"
)
```

### 4. 创建版本标签

```python
from huggingface_hub import HfApi

hub_api = HfApi()
hub_api.create_tag(
    "username/merged-dataset",
    tag="v1.0",
    repo_type="dataset"
)
```
## 📊 数据结构

LeRobot 数据集遵循以下结构：

```
dataset_root/
├── data/
│   └── chunk-000/
│       ├── episode_000000.parquet
│       ├── episode_000001.parquet
│       └── ...
├── videos/
│   └── chunk-000/
│       └── observation.images.front/
│           ├── episode_000000.mp4
│           └── ...
└── meta/
    ├── info.json
    ├── episodes.jsonl
    ├── episodes_stats.jsonl
    ├── tasks.jsonl
    └── stats.json
```

## 🤝 贡献

欢迎贡献！请随时提交 issue 和 pull request。

## 📄 许可证

本项目按原样提供，用于 LeRobot 数据集。

## 🔗 相关项目

- [LeRobot](https://github.com/huggingface/lerobot) - LeRobot 官方仓库
- [HuggingFace Hub](https://huggingface.co/docs/hub) - 数据集托管平台

## 📧 联系方式

如有问题或疑问，请在 GitHub 上提交 issue。

---

**注意**：运行脚本前，请根据你的具体数据集位置和要求更新文件路径和配置参数。