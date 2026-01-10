import shutil
import os

src_dir = "/home/dudu/.cache/huggingface/lerobot/zhengzi/lerobot_second_0/videos/chunk-000/observation.images.front"  # 原始文件所在文件夹
dst_dir = "/home/dudu/.cache/huggingface/lerobot/zhengzi/lerobot_second/videos/chunk-000/observation.images.front"  # 目标文件夹


src_start = 0
src_end = 26
dst_start = 41

# 确保目标文件夹存在
os.makedirs(dst_dir, exist_ok=True)

for i in range(src_start, src_end + 1):
    # 构建原始文件名，例如 episode_000000.parquet
    # src_filename = f"episode_{i:06d}.parquet"
    src_filename = f"episode_{i:06d}.mp4"
    src_path = os.path.join(src_dir, src_filename)
    
    # 构建目标文件名，例如 episode_000042.parquet
    new_index = i + dst_start
    # dst_filename = f"episode_{new_index:06d}.parquet"
    dst_filename = f"episode_{new_index:06d}.mp4"
    dst_path = os.path.join(dst_dir, dst_filename)
    
    if os.path.exists(src_path):
        # 使用 copy2 可以保留文件元数据，如果想直接移动请用 shutil.move
        shutil.copy2(src_path, dst_path)
        print(f"已复制并重命名: {src_filename} -> {dst_filename}")
    else:
        print(f"警告: 找不到文件 {src_filename}")

print("任务完成！")