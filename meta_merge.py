import json
import os

# --- 配置区 ---
source_file = "/home/dudu/.cache/huggingface/lerobot/zhengzi/lerobot_second_0/meta/episodes_stats.jsonl" #追加的文件
target_file = "/home/dudu/.cache/huggingface/lerobot/zhengzi/lerobot_second/meta/episodes_stats.jsonl"   #被追加的文件

# 偏移量配置
episode_offset = 41    # episode 0 -> 41
global_index_offset = 35540  # index 0 -> 35540
# --------------

if not os.path.exists(source_file):
    print(f"错误: 找不到源文件 {source_file}")
    exit()

# 确保目标文件夹存在
os.makedirs(os.path.dirname(target_file), exist_ok=True)

processed_count = 0

# 使用 'a' 模式追加写入
with open(target_file, 'a', encoding='utf-8') as f_out:
    with open(source_file, 'r', encoding='utf-8') as f_in:
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
print(f"成功将 {processed_count} 条 episode 数据追加至: {target_file}")