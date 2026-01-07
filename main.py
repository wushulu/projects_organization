import os
import re
from pathlib import Path

# --- 章节标题定义 ---
SECTION_DIR = "## 主要目录（示例）"
SECTION_PROJ = "## 项目列表"
SECTION_DETAIL = "## 项目详细资料"
MAX_DEPTH = 5

def clean_meta_value(val):
    """
    清洗元数据：剔除抓取过程中意外包含的加粗标签、冒号以及下一行的标题
    """
    if not val:
        return ""
    # 1. 如果抓取到了下一行的标题（##），截断它
    val = val.split("##")[0]
    # 2. 剔除可能重复出现的“名称/描述/状态”等关键字标签（处理叠加bug）
    val = re.sub(r'(\*\*|)(名称|描述|状态)(\*\*|)\s*[:：]\s*', '', val)
    # 3. 剔除末尾多余的标点和空格
    return val.strip().rstrip("；").rstrip(";")

def get_meta_from_file(readme_path):
    """
    【红色框修复】精准提取用户手动修改的值，并防止重复叠加标签。
    """
    meta = {"名称": "", "描述": "", "状态": ""}
    if not readme_path.exists():
        return meta
    try:
        content = readme_path.read_text(encoding="utf-8")
        for key in meta.keys():
            # 优化正则：[^#\n\r]* 表示匹配到行尾或遇到 # 号（防止抓到下一行标题）
            pattern = rf"(?:\*\*{key}\*\*|{key})\s*[:：]\s*([^#\n\r]*)"
            match = re.search(pattern, content)
            if match:
                meta[key] = clean_meta_value(match.group(1))
    except Exception:
        pass
    return meta

def update_folder_readme(folder_path, is_hw, children_projects, base_dir):
    """
    【结构重构】组装 README。
    """
    readme_path = folder_path / "README.md"
    
    # 1. 提取元数据（带清洗功能）
    current_meta = get_meta_from_file(readme_path)
    name = current_meta["名称"] if current_meta["名称"] else folder_path.name
    desc = current_meta["描述"]
    stat = current_meta["状态"]

    # 2. 构造头部（确保标签只出现一次）
    new_lines = [
        f"# “{name}” — 项目汇总",
        "",
        f"**文件夹**：`{folder_path.name}/`",
        "",
        f"**名称**：{name}",
        "",
        f"**描述**：{desc}",
        "",
        f"**状态**：{stat}",
        ""
    ]

    # 3. 处理“主要目录”
    if is_hw:
        new_lines.append(SECTION_DIR)
        new_lines.append("")
        physical_dirs = [d.name for d in folder_path.iterdir() if d.is_dir() and not d.name.startswith(".")]
        if "hardware" in physical_dirs:
            physical_dirs.remove("hardware")
            physical_dirs.insert(0, "hardware")
        for d in physical_dirs:
            d_desc = "硬件资料（已存在）" if d == "hardware" else "资料"
            new_lines.append(f"- `{d}/` — {d_desc}")
        new_lines.append("")

    # 4. 处理“项目列表” (排除当前项目自己)
    my_rel_path = folder_path.relative_to(base_dir)
    real_children = [p for p in children_projects if str(p["rel_path"]) != str(my_rel_path)]

    if real_children:
        new_lines.append(SECTION_PROJ)
        new_lines.append("\n以下为扫描结果：\n")
        for p in real_children:
            try:
                display_path = p["rel_path"].relative_to(my_rel_path)
            except:
                display_path = p["rel_path"]
            
            depth = len(display_path.parts) - 1
            indent = "\t" * depth
            p_str = f"{display_path}/".replace("\\", "/")
            # 这里的 p['desc'] 等已经是清洗过的纯净数据
            new_lines.append(f"{indent} - `{p_str}` — 名称：{p['name']}；描述：{p['desc']}；状态：{p['stat']}")
        new_lines.append("")

    # 5. 处理“项目详细资料”
    user_detail = f"{SECTION_DETAIL}\n\n内容..."
    if readme_path.exists():
        raw_text = readme_path.read_text(encoding="utf-8")
        search = re.search(r"(## (?:项目详细资料|详细信息|详细资料).*)", raw_text, re.DOTALL)
        if search:
            user_detail = search.group(1).strip()
    
    new_lines.append(user_detail)

    # 写入
    readme_path.write_text("\n".join(new_lines), encoding="utf-8")
    return {"名称": name, "描述": desc, "状态": stat}

def scan_logic(current_dir, base_dir, depth=1):
    if depth > MAX_DEPTH:
        return False, []

    is_hw = (current_dir / "hardware").exists()
    all_descendants = []
    has_sub_projects = False

    for item in sorted(current_dir.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            sub_ok, sub_data = scan_logic(item, base_dir, depth + 1)
            if sub_ok:
                has_sub_projects = True
                all_descendants.extend(sub_data)

    if is_hw or has_sub_projects:
        # 获取最新元数据并更新文件
        meta = update_folder_readme(current_dir, is_hw, all_descendants, base_dir)
        
        my_info = {
            "rel_path": current_dir.relative_to(base_dir),
            "name": meta["名称"],
            "desc": meta["描述"],
            "stat": meta["状态"]
        }
        return True, [my_info] + all_descendants
    
    return False, []

if __name__ == "__main__":
    root = Path(".")
    print("="*40)
    print(" 项目管理助手 V6.2 - 修复叠加BUG ")
    print("="*40)
    try:
        scan_logic(root, root)
        print("\n[成功] 运行完成。")
        print("-> 已自动清洗重复的‘状态’标签。")
        print("-> 已自动截断抓取错误的标题行。")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[错误]: {e}")
    input("\n按回车键退出...")