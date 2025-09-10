import requests
import zipfile
import re
import platform
from tqdm import tqdm
from pathlib import Path
import shutil

# ---------------------------
# 统一路径管理
# ---------------------------
working_dir = Path(__file__).parent.parent.parent
download_dir = working_dir / "download"
fw_dir = working_dir / "deps"
mfa_dir = working_dir / "MFA"
fw_download_dir = download_dir / "MaaFramework"
mfa_download_dir = download_dir / "MFAAvalonia"

# ---------------------------
# 获取架构
# ---------------------------
def get_architecture():
    arch = platform.machine().lower()
    arch_mapping = {
        "amd64": "x86_64",
        "x86_64": "x86_64",
        "aarch64": "aarch64",
        "arm64": "aarch64",
    }
    return arch_mapping.get(arch, arch)

# ---------------------------
# 通用下载函数
# ---------------------------
def download_file(url, output_path, file_size=None, desc=""):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        with tqdm(
            total=file_size,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
            desc=desc,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                pbar.update(size)

# ---------------------------
# 下载 MaaFramework
# ---------------------------
def download_maa_framework():
    fw_dir.mkdir(parents=True, exist_ok=True)
    fw_download_dir.mkdir(parents=True, exist_ok=True)

    # 清空旧压缩包
    shutil.rmtree(fw_download_dir, ignore_errors=True)
    fw_download_dir.mkdir(parents=True, exist_ok=True)

    api_url = "https://api.github.com/repos/MaaXYZ/MaaFramework/releases/latest"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        release_data = response.json()

        arch = get_architecture()
        pattern = f"MAA-win-{arch}"
        matching_assets = [
            asset for asset in release_data["assets"] if pattern in asset["name"]
        ]

        if not matching_assets:
            raise Exception(f"No matching assets found for: {pattern}")

        asset = matching_assets[0]
        download_url = asset["browser_download_url"]
        filename = asset["name"]
        file_size = asset.get("size", None)

        file_path = fw_download_dir / filename
        if file_path.exists():
            print(f"MaaFramework 压缩包已存在: {file_path}")
        else:
            print("MaaFramework 需要下载")
            download_file(download_url, file_path, file_size, desc=filename)

        # 清空旧解压目录
        shutil.rmtree(fw_dir, ignore_errors=True)
        fw_dir.mkdir(parents=True, exist_ok=True)

        # 解压
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            file_list = zip_ref.namelist()
            with tqdm(total=len(file_list), desc="Extracting MaaFramework", unit="files") as pbar:
                for file in file_list:
                    zip_ref.extract(file, fw_dir)
                    pbar.update(1)

        print(f"MaaFramework 解压完成到 {fw_dir}")

    except Exception as e:
        print(f"下载 MaaFramework 出错: {e}")

# ---------------------------
# 下载 MFAAvalonia
# ---------------------------
def download_mfa_avalonia():
    mfa_dir.mkdir(parents=True, exist_ok=True)
    mfa_download_dir.mkdir(parents=True, exist_ok=True)

    # 清空旧压缩包
    shutil.rmtree(mfa_download_dir, ignore_errors=True)
    mfa_download_dir.mkdir(parents=True, exist_ok=True)

    api_url = "https://api.github.com/repos/SweetSmellFox/MFAAvalonia/releases/latest"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        release_data = response.json()

        pattern = "MFAAvalonia.*-win-x64"
        matching_assets = [
            asset
            for asset in release_data["assets"]
            if re.search(pattern, asset["name"], re.IGNORECASE)
        ]

        if not matching_assets:
            raise Exception(f"No matching assets found for: {pattern}")

        asset = matching_assets[0]
        download_url = asset["browser_download_url"]
        filename = asset["name"]
        file_size = asset.get("size", None)

        file_path = mfa_download_dir / filename
        if file_path.exists():
            print(f"MFAAvalonia 压缩包已存在: {file_path}")
        else:
            print("MFAAvalonia 需要下载")
            download_file(download_url, file_path, file_size, desc=filename)

        # 清空旧解压目录
        shutil.rmtree(mfa_dir, ignore_errors=True)
        mfa_dir.mkdir(parents=True, exist_ok=True)

        # 解压
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            file_list = zip_ref.namelist()
            with tqdm(total=len(file_list), desc="Extracting MFAAvalonia", unit="files") as pbar:
                for file in file_list:
                    zip_ref.extract(file, mfa_dir)
                    pbar.update(1)

        print(f"MFAAvalonia 解压完成到 {mfa_dir}")

    except Exception as e:
        print(f"下载 MFAAvalonia 出错: {e}")

# ---------------------------
# 主函数
# ---------------------------
if __name__ == "__main__":
    arch = get_architecture()

    if platform.system() == "Windows" and arch == "x86_64":
        download_maa_framework()
        download_mfa_avalonia()
    else:
        print(f"当前系统不是 x86_64 的 Windows 系统（检测到 {platform.system()} {arch}），请等待后续开发")
