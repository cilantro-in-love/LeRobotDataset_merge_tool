"""
完整合并多个 LeRobot 数据集的脚本（包括更新 parquet 文件内容）
"""
import json
import shutil
import pandas as pd
from pathlib import Path
from lerobot.datasets.lerobot_dataset import LeRobotDataset

def merge_lerobot_datasets(
    source_paths: list[str],
    target_repo_id: str,
    target_root: str,
):
    """
    完整合并多个 LeRobot 数据集（包括更新所有文件内容）
    
    Args:
        source_paths: 源数据集的本地路径列表
        target_repo_id: 目标数据集的 repo_id
        target_root: 目标数据集的本地根路径
    """
    # 1. 加载所有源数据集
    print("📚 加载源数据集...")
    datasets = [LeRobotDataset(path) for path in source_paths]
    
    # 2. 验证数据集兼容性
    print("✅ 验证数据集兼容性...")
    base_ds = datasets[0]
    for i, ds in enumerate(datasets[1:], 1):
        if ds.fps != base_ds.fps:
            raise ValueError(f"数据集 {i} 的 fps ({ds.fps}) 与第一个数据集 ({base_ds.fps}) 不匹配")
        if ds.meta.robot_type != base_ds.meta.robot_type:
            print(f"⚠️  警告: 数据集 {i} 的 robot_type 不同")
    
    # 3. 创建目标目录
    target_path = Path(target_root)
    if target_path.exists():
        print(f"⚠️  目标路径 {target_path} 已存在，将被覆盖...")
        shutil.rmtree(target_path)
    target_path.mkdir(parents=True)
    
    # 4. 准备合并的元数据
    print("📝 准备元数据...")
    merged_info = base_ds.meta.info.copy()
    merged_episodes = {}
    merged_episodes_stats = {}
    merged_tasks = {}
    merged_task_to_task_index = {}
    
    total_episodes = 0
    total_frames = 0
    episode_offset = 0
    frame_offset = 0
    
    # 5. 逐个处理每个数据集
    for ds_idx, ds in enumerate(datasets):
        print(f"\n📦 处理数据集 {ds_idx + 1}/{len(datasets)}: {ds.repo_id}")
        
        # 合并 tasks
        for task_idx, task in ds.meta.tasks.items():
            if task not in merged_task_to_task_index:
                new_task_idx = len(merged_tasks)
                merged_tasks[new_task_idx] = task
                merged_task_to_task_index[task] = new_task_idx
        
        # 处理每个 episode
        for ep_idx in range(ds.meta.total_episodes):
            new_ep_idx = episode_offset + ep_idx
            
            # 🔧 关键修复：读取并更新 parquet 文件内容
            src_data = ds.root / ds.meta.get_data_file_path(ep_idx)
            dst_data = target_path / base_ds.meta.get_data_file_path(new_ep_idx)
            dst_data.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取 parquet 文件
            df = pd.read_parquet(src_data)
            ep_length = len(df)
            
            # 更新 episode_index 列
            df['episode_index'] = new_ep_idx
            
            # 更新 index 列（全局帧索引）
            df['index'] = range(frame_offset, frame_offset + ep_length)
            
            # 保存更新后的 parquet 文件
            df.to_parquet(dst_data, index=False)
            
            # 复制视频文件
            if ds.meta.video_keys:
                for vid_key in ds.meta.video_keys:
                    src_video = ds.root / ds.meta.get_video_file_path(ep_idx, vid_key)
                    if src_video.exists():
                        dst_video = target_path / base_ds.meta.get_video_file_path(new_ep_idx, vid_key)
                        dst_video.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_video, dst_video)
            
            # 更新 episodes 元数据
            ep_dict = ds.meta.episodes[ep_idx].copy()
            ep_dict["episode_index"] = new_ep_idx
            merged_episodes[new_ep_idx] = ep_dict
            
            # 更新 episodes_stats
            ep_stats = ds.meta.episodes_stats[ep_idx].copy()
            
            # 更新 stats 中的 episode_index 字段
            if "episode_index" in ep_stats:
                ep_stats["episode_index"]["min"] = [new_ep_idx]
                ep_stats["episode_index"]["max"] = [new_ep_idx]
                ep_stats["episode_index"]["mean"] = [float(new_ep_idx)]
            
            # 更新 stats 中的 index 字段
            if "index" in ep_stats:
                new_min = frame_offset
                new_max = frame_offset + ep_length - 1
                
                ep_stats["index"]["min"] = [new_min]
                ep_stats["index"]["max"] = [new_max]
                ep_stats["index"]["mean"] = [(new_min + new_max) / 2.0]
                # std 需要重新计算
                import numpy as np
                ep_stats["index"]["std"] = [np.std(np.arange(new_min, new_max + 1)).item()]
            
            merged_episodes_stats[new_ep_idx] = ep_stats
            
            total_frames += ep_length
            frame_offset += ep_length
            
            print(f"  ✓ Episode {ep_idx} -> {new_ep_idx} (frames {new_min}-{new_max}, {ep_length} frames)")
        
        episode_offset += ds.meta.total_episodes
        total_episodes += ds.meta.total_episodes
    
    # 6. 更新并保存 info.json
    print("\n💾 保存元数据...")
    merged_info["total_episodes"] = total_episodes
    merged_info["total_frames"] = total_frames
    merged_info["total_tasks"] = len(merged_tasks)
    merged_info["total_chunks"] = (total_episodes - 1) // merged_info["chunks_size"] + 1
    merged_info["splits"] = {"train": f"0:{total_episodes}"}
    if merged_info.get("total_videos"):
        merged_info["total_videos"] = total_episodes * len(base_ds.meta.video_keys)
    
    (target_path / "meta").mkdir(exist_ok=True)
    with open(target_path / "meta" / "info.json", "w") as f:
        json.dump(merged_info, f, indent=2)
    
    # 7. 保存 tasks.jsonl
    import jsonlines
    with jsonlines.open(target_path / "meta" / "tasks.jsonl", "w") as writer:
        for task_idx, task in merged_tasks.items():
            writer.write({"task_index": task_idx, "task": task})
    
    # 8. 保存 episodes.jsonl
    with jsonlines.open(target_path / "meta" / "episodes.jsonl", "w") as writer:
        for ep_idx in sorted(merged_episodes.keys()):
            writer.write(merged_episodes[ep_idx])
    
    # 9. 保存 episodes_stats.jsonl
    def serialize_stats(stats):
        """递归序列化 numpy 数组为列表"""
        import numpy as np
        if isinstance(stats, dict):
            return {k: serialize_stats(v) for k, v in stats.items()}
        elif isinstance(stats, (np.ndarray, list)):
            return np.array(stats).tolist()
        elif isinstance(stats, np.generic):
            return stats.item()
        return stats
    
    with jsonlines.open(target_path / "meta" / "episodes_stats.jsonl", "w") as writer:
        for ep_idx in sorted(merged_episodes_stats.keys()):
            writer.write({
                "episode_index": ep_idx,
                "stats": serialize_stats(merged_episodes_stats[ep_idx])
            })
    
    # 10. 聚合统计信息
    try:
        from lerobot.datasets.compute_stats import aggregate_stats
        import numpy as np
        
        # 将 stats 从 list 转换回 numpy array
        def convert_to_numpy(stats):
            """递归地将 list 转换为 numpy array"""
            if isinstance(stats, dict):
                return {k: convert_to_numpy(v) for k, v in stats.items()}
            elif isinstance(stats, list):
                return np.array(stats)
            return stats
        
        # 转换所有 episodes_stats 为 numpy 格式
        numpy_episodes_stats = [
            convert_to_numpy(ep_stats) 
            for ep_stats in merged_episodes_stats.values()
        ]
        
        # 聚合统计信息
        merged_stats = aggregate_stats(numpy_episodes_stats)
        with open(target_path / "meta" / "stats.json", "w") as f:
            json.dump(serialize_stats(merged_stats), f, indent=2)
    except ImportError:
        print("⚠️  无法导入 aggregate_stats，跳过 stats.json 生成")
    except Exception as e:
        print(f"⚠️  生成 stats.json 时出错: {e}")
        print("⚠️  跳过 stats.json 生成，但数据集仍然可用")
    
    print(f"\n🎉 合并完成！")
    print(f"  总 episodes: {total_episodes}")
    print(f"  总 frames: {total_frames}")
    print(f"  总 tasks: {len(merged_tasks)}")
    print(f"  保存路径: {target_path}")
    
    return target_path


def verify_merged_dataset(dataset_path: str, check_episodes: list[int] = None):
    """验证合并后的数据集索引是否正确"""
    print(f"\n🔍 验证数据集: {dataset_path}")
    ds = LeRobotDataset(dataset_path)
    
    if check_episodes is None:
        # 检查第一个、最后一个和中间的几个 episode
        check_episodes = [0, ds.meta.total_episodes // 2, ds.meta.total_episodes - 1]
    
    for ep_idx in check_episodes:
        # 读取 parquet 文件
        data_file = ds.root / ds.meta.get_data_file_path(ep_idx)
        df = pd.read_parquet(data_file)
        
        # 检查索引
        ep_index_values = df['episode_index'].unique()
        index_min = df['index'].min()
        index_max = df['index'].max()
        
        print(f"\n  Episode {ep_idx}:")
        print(f"    Data file: {data_file.name}")
        print(f"    Episode index in data: {ep_index_values}")
        print(f"    Global index range: [{index_min}, {index_max}]")
        print(f"    Frames: {len(df)}")
        
        # 验证
        assert len(ep_index_values) == 1 and ep_index_values[0] == ep_idx, \
            f"Episode index 不匹配！期望 {ep_idx}，实际 {ep_index_values}"
        
        # 检查 index 连续性
        expected_indices = list(range(index_min, index_max + 1))
        actual_indices = df['index'].tolist()
        assert actual_indices == expected_indices, \
            f"Index 不连续！"
        
        print(f"    ✅ 验证通过")
    
    print(f"\n✅ 数据集验证完成！")


def push_merged_dataset(target_path: str, repo_id: str):
    """推送合并后的数据集到 Hub"""
    print(f"\n📤 推送到 Hub: {repo_id}")
    merged_ds = LeRobotDataset(repo_id, root=target_path)
    merged_ds.push_to_hub(
        tags=["robotics", "merged-dataset"],
        license="apache-2.0"
    )
    print("✅ 推送完成！")


if __name__ == "__main__":
    # 使用示例
    source_datasets = [
        "/home/dudu/.cache/huggingface/lerobot/zhengzi/lerobot_second_0",
        "/home/dudu/.cache/huggingface/lerobot/zhengzi/lerobot_second_1",
    ]
    
    target_repo = "zhengzi/lerobot_second_train"
    target_root = "/home/dudu/.cache/huggingface/lerobot/zhengzi/lerobot_second_train"
    
    # 合并数据集
    merged_path = merge_lerobot_datasets(
        source_paths=source_datasets,
        target_repo_id=target_repo,
        target_root=target_root
    )
    
    # 验证合并结果
    verify_merged_dataset(
        str(merged_path),
        check_episodes=[0, 26, 27, 67]  # 检查关键的 episodes
    )
    
    # 推送到 Hub（可选）
    push_choice = input("\n是否推送到 HuggingFace Hub? (y/n): ")
    if push_choice.lower() == 'y':
        push_merged_dataset(str(merged_path), target_repo)
