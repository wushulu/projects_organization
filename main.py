import os
import re
from pathlib import Path

# --- 核心逻辑 ---

def get_metadata_from_readme(readme_path):
    info = {"名称": "", "描述": "", "状态": ""}
    if not readme_path.exists():
        return info
    try:
        content = readme_path.read_text(encoding="utf-8")
        patterns = {
            "名称": r"(?:\*\*名称\*\*|名称)\s*：\s*([^；\n]*)",
            "描述": r"(?:\*\*描述\*\*|描述)\s*：\s*([^；\n]*)",
            "状态": r"(?:\*\*状态\*\*|状态)\s*：\s*([^；\n]*)",
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                info[key] = match.group(1).strip()
    except Exception as e:
        print(f"读取 {readme_path} 出错: {e}")
    return info

def update_project_directory_list(project_path, content):
    physical_dirs = [d.name for d in project_path.iterdir() if d.is_dir() and not d.name.startswith(".")]
    existing_dirs_info = {}
    dir_list_pattern = r"- `([^/]+)/` — (.*)"
    matches = re.findall(dir_list_pattern, content)
    for folder, desc in matches:
        existing_dirs_info[folder] = desc.strip()

    new_list_lines = []
    if "hardware" in physical_dirs:
        physical_dirs.remove("hardware")
        physical_dirs.insert(0, "hardware")

    for d in physical_dirs:
        desc = existing_dirs_info.get(d, "硬件资料（已存在）" if d == "hardware" else "资料")
        new_list_lines.append(f"- `{d}/` — {desc}")

    new_list_str = "## 主要目录（示例）\n\n" + "\n".join(new_list_lines)
    section_pattern = r"## 主要目录（示例）.*?(?=\n#|$)"
    
    if "## 主要目录（示例）" in content:
        updated_content = re.sub(section_pattern, new_list_str, content, flags=re.DOTALL)
    else:
        updated_content = content.strip() + "\n\n" + new_list_str
    return updated_content

def create_or_update_project_readme(project_path):
    readme_path = project_path / "README.md"
    folder_name = project_path.name
    
    if not readme_path.exists():
        content = f"# “{folder_name}” — 项目汇总\n\n**文件夹**：`{folder_name}/`\n\n**名称**：{folder_name}\n\n**描述**：\n\n**状态**：\n\n"
        content = update_project_directory_list(project_path, content)
        readme_path.write_text(content, encoding="utf-8")
    else:
        old_content = readme_path.read_text(encoding="utf-8")
        new_content = update_project_directory_list(project_path, old_content)
        if old_content.strip() != new_content.strip():
            readme_path.write_text(new_content, encoding="utf-8")
    
    return get_metadata_from_readme(readme_path)

def scan_logic(current_dir, base_dir):
    is_project = (current_dir / "hardware").exists() and (current_dir / "hardware").is_dir()
    all_sub_info = []
    
    if is_project:
        meta = create_or_update_project_readme(current_dir)
        rel_path = current_dir.relative_to(base_dir)
        all_sub_info.append((rel_path, 0, meta["名称"], meta["描述"], meta["状态"]))

    contains_any_project = is_project
    for item in sorted(current_dir.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            sub_has_prj, sub_list = scan_logic(item, base_dir)
            if sub_has_prj:
                contains_any_project = True
                for p_path, depth, p_name, p_desc, p_stat in sub_list:
                    if not any(str(p_path) == str(existing[0]) for existing in all_sub_info):
                        all_sub_info.append((p_path, depth + 1, p_name, p_desc, p_stat))

    if len(all_sub_info) > 0:
        generate_index_readme(current_dir, all_sub_info, base_dir)

    return contains_any_project, all_sub_info

def generate_index_readme(folder_path, projects, base_dir):
    readme_path = folder_path / "README.md"
    lines = ["## 项目列表"]
    for p_path, depth, name, desc, stat in projects:
        try:
            # 计算相对于当前扫描文件夹的显示路径
            rel_to_current = p_path.relative_to(folder_path.relative_to(base_dir))
        except:
            rel_to_current = p_path
            
        indent = "  " * (len(rel_to_current.parts) - 1)
        path_str = f"{rel_to_current}/".replace("\\", "/")
        line = f"{indent}- `{path_str}` — 名称：{name}；描述：{desc}；状态：{stat}"
        lines.append(line)

    list_content = "\n".join(lines)
    if readme_path.exists():
        old_content = readme_path.read_text(encoding="utf-8")
        if "## 项目列表" in old_content:
            new_content = re.sub(r"## 项目列表.*?(?=\n#|$)", list_content, old_content, flags=re.DOTALL)
        else:
            new_content = old_content.strip() + "\n\n" + list_content
    else:
        new_content = f"# {folder_path.name} 目录汇总\n\n{list_content}"
    readme_path.write_text(new_content, encoding="utf-8")

if __name__ == "__main__":
    root_path = Path(".")
    print("="*40)
    print("项目管理大纲自动生成器")
    print("="*40)
    print(f"当前扫描目录: {root_path.absolute()}")
    try:
        scan_logic(root_path, root_path)
        print("\n[成功] 所有 README.md 已更新。")
    except Exception as e:
        print(f"\n[错误] 运行过程中出现问题: {e}")
    input("\n按回车键退出...")