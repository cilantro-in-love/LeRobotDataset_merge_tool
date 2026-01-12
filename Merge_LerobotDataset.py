import shutil
import os
import json

import pandas as pd
src_dir = "/home/dudu/.cache/huggingface/lerobot/zhengzi/lerobot_second_0"  # 原始文件所在文件夹
dst_dir = "/home/dudu/.cache/huggingface/lerobot/zhengzi/lerobot_second"  # 目标文件夹

videos_path = "videos/chunk-000/observation.images.front"
data_path = "data/chunk-000"
meta_path = "meta"

os.makedirs(src_dir, exist_ok=True)
os.makedirs(dst_dir, exist_ok=True)
src_start = 0
src_data_path = os.path.join(src_dir, data_path)
dst_data_path = os.path.join(dst_dir, data_path)
src_videos_path = os.path.join(src_dir, videos_path)
dst_videos_path = os.path.join(dst_dir, videos_path)
src_meta_path = os.path.join(src_dir, meta_path)
dst_meta_path = os.path.join(dst_dir, meta_path)

src_files_count = len(os.listdir(src_data_path)) 
dst_files_count = len(os.listdir(dst_data_path))

print("合并data数据")
for i in range(src_start, src_files_count):
    # 构建原始文件名，例如 episode_000000.parquet
    src_filename = f"episode_{i:06d}.parquet"
    src_path = os.path.join(src_data_path, src_filename)
    
    # 构建目标文件名，例如 episode_000042.parquet
    new_index = i + dst_files_count
    dst_filename = f"episode_{new_index:06d}.parquet"
    dst_path = os.path.join(dst_data_path, dst_filename)
    
    if os.path.exists(src_path):
        # 使用 copy2 可以保留文件元数据，如果想直接移动请用 shutil.move
        shutil.copy2(src_path, dst_path)
        print(f"已复制并重命名: {src_filename} -> {dst_filename}")
    else:
        print(f"警告: 找不到文件 {src_filename}")
print("合并data数据完成")

print("合并videos数据")
for i in range(src_start, src_files_count):
    src_filename = f"episode_{i:06d}.mp4"
    src_path = os.path.join(src_videos_path, src_filename)
    new_index = i + dst_files_count
    dst_filename = f"episode_{new_index:06d}.mp4"
    dst_path = os.path.join(dst_videos_path, dst_filename)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"已复制并重命名: {src_filename} -> {dst_filename}")
    else:
        print(f"警告: 找不到文件 {src_filename}")
print("合并videos数据完成")
print("合并meta数据")
print("合并info.json数据")

src_info_json = os.path.join(src_meta_path, "info.json")
dst_info_json = os.path.join(dst_meta_path, "info.json")
if os.path.exists(src_info_json) and os.path.exists(dst_info_json):
    with open(src_info_json, 'r', encoding='utf-8') as s:
        with open(dst_info_json, 'r', encoding='utf-8') as d:
            src_data = json.load(s)
            dst_data = json.load(d)
            global_index_offset = dst_data["total_frames"]
            dst_data["total_episodes"] = dst_data["total_episodes"] + src_data["total_episodes"]
            dst_data["total_frames"] = dst_data["total_frames"] + src_data["total_frames"]
            dst_data["total_videos"] = dst_data["total_videos"] + src_data["total_videos"]
            dst_data["splits"]["train"] = f"0:{dst_data['total_videos']}"
        with open(dst_info_json, 'w', encoding='utf-8') as d:
            json.dump(dst_data, d, indent=4, ensure_ascii=False)
print("合并info.json数据完成")

print("合并episodes_stats.json数据")
src_episodes_stats = os.path.join(src_meta_path, "episodes_stats.jsonl")
dst_episodes_stats = os.path.join(dst_meta_path, "episodes_stats.jsonl")
processed_count = 0
episode_offset = dst_files_count
if os.path.exists(src_episodes_stats) and os.path.exists(dst_episodes_stats):
    with open(dst_episodes_stats, 'a', encoding='utf-8') as f_out:
        with open(src_episodes_stats, 'r', encoding='utf-8') as f_in:
            for line in f_in:
                if not line.strip():
                    continue
                
                data = json.loads(line)
                
                # 1. 修改根节点的 episode_index
                old_ep_idx = data["episode_index"]
                new_ep_idx = old_ep_idx + episode_offset
                data["episode_index"] = new_ep_idx
                
                # 2. 修改 stats -> episode_index (统计信息同步平移)
                if "episode_index" in data.get("stats", {}):
                    e_stats = data["stats"]["episode_index"]
                    e_stats["min"] = [int(new_ep_idx)]
                    e_stats["max"] = [int(new_ep_idx)]
                    e_stats["mean"] = [float(new_ep_idx)]
                
                # 3. 修改 stats -> index (全局帧索引平移)
                if "index" in data.get("stats", {}):
                    i_stats = data["stats"]["index"]
                    # 对原有的每个值加上偏移量
                    i_stats["min"] = [v + global_index_offset for v in i_stats["min"]]
                    i_stats["max"] = [v + global_index_offset for v in i_stats["max"]]
                    i_stats["mean"] = [v + global_index_offset for v in i_stats["mean"]]
                
                # 将修改后的字典转换为一行 JSON 写入
                f_out.write(json.dumps(data) + '\n')
                processed_count += 1
                print(f"已追加: 原 Episode {old_ep_idx} -> 新 {new_ep_idx}")

    print(f"\n--- 任务完成 ---")
           
src_episodes = os.path.join(src_meta_path, "episodes.jsonl")
dst_episodes = os.path.join(dst_meta_path, "episodes.jsonl")
if os.path.exists(src_episodes) and os.path.exists(dst_episodes):
    with open(dst_episodes, 'a', encoding='utf-8') as f_out:
        with open(src_episodes, 'r', encoding='utf-8') as f_in:
            for line in f_in:
                if not line.strip():
                    continue
                
                data = json.loads(line)
                
                # 1. 修改根节点的 episode_index
                old_ep_idx = data["episode_index"]
                new_ep_idx = old_ep_idx + episode_offset
                data["episode_index"] = new_ep_idx
                
                # 将修改后的字典转换为一行 JSON 写入
                f_out.write(json.dumps(data) + '\n')
                processed_count += 1
                print(f"已追加: 原 Episode {old_ep_idx} -> 新 {new_ep_idx}")

    print(f"\n--- 任务完成 ---")

for i in range(dst_files_count, dst_files_count+src_files_count):
    source_file = f"{dst_data_path}/episode_{i:06d}.parquet"
    df = pd.read_parquet(source_file)
    df["index"] = df["index"] + global_index_offset
    df["episode_index"] = df["episode_index"] + episode_offset
    df.to_parquet(f"{dst_data_path}/episode_{i:06d}.parquet", index=False)
    print(f"{dst_data_path}/episode_{i:06d}.parquet 已追加")

