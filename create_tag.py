from huggingface_hub import HfApi

hub_api = HfApi()
hub_api.create_tag(
    "zhengzi/lerobot_second_train", 
    tag="v2.0",  # 替换成你的实际版本号
    repo_type="dataset"
)