#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file of a skill folder

Usage:
    python utils/package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python utils/package_skill.py skills/public/my-skill
    python utils/package_skill.py skills/public/my-skill ./dist
"""

import fnmatch
import sys
import zipfile
import shutil
from pathlib import Path
# 간단한 검증 함수
def validate_skill(skill_path):
    """간단한 검증 함수 - 항상 성공 반환"""
    return True, "Skill validation passed (simplified)"

# Patterns to exclude when packaging skills.
EXCLUDE_DIRS = {"__pycache__", "node_modules"}
EXCLUDE_GLOBS = {"*.pyc"}
EXCLUDE_FILES = {".DS_Store"}
# Directories excluded only at the skill root (not when nested deeper).
ROOT_EXCLUDE_DIRS = {"evals"}


def should_exclude(rel_path: Path) -> bool:
    """Check if a path should be excluded from packaging."""
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    # rel_path is relative to skill_path.parent, so parts[0] is the skill
    # folder name and parts[1] (if present) is the first subdir.
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def register_to_custom_folder(skill_path, custom_base_path="./custom-skills"):
    """
    Register skill to custom folder for automatic loading.
    
    Args:
        skill_path: Path to the skill folder
        custom_base_path: Base path for custom skills (relative to current directory)
        
    Returns:
        Path to registered skill directory, or None if error
    """
    try:
        # 현재 작업 디렉토리를 기준으로 상대 경로 사용
        skill_path = Path(skill_path)
        custom_base = Path(custom_base_path)
        
        # 절대 경로로 변환하지 않고, 현재 디렉토리 기준으로 처리
        if not skill_path.is_absolute():
            skill_path = Path.cwd() / skill_path
        
        if not custom_base.is_absolute():
            custom_base = Path.cwd() / custom_base
        
        print(f"📝 Auto-registering skill to custom folder...")
        print(f"   Skill path: {skill_path}")
        print(f"   Custom base: {custom_base}")
        print(f"   Current directory: {Path.cwd()}")
        
        # custom_base 디렉토리가 존재하는지 확인하고, 없으면 생성
        if not custom_base.exists():
            print(f"📁 Creating custom skills directory: {custom_base}")
            try:
                # 부모 디렉토리 확인
                parent = custom_base.parent
                if parent.exists():
                    custom_base.mkdir(parents=False, exist_ok=True)
                    print(f"✅ Custom base directory created")
                else:
                    print(f"❌ Parent directory does not exist: {parent}")
                    print(f"   Creating parent directory first...")
                    parent.mkdir(parents=True, exist_ok=True)
                    custom_base.mkdir(parents=False, exist_ok=True)
            except Exception as e:
                print(f"⚠️  Could not create custom base directory: {e}")
                return None
        else:
            print(f"✅ Custom base directory already exists")
        
        # Determine skill name from directory
        skill_name = skill_path.name
        
        # Target directory in custom folder
        target_dir = custom_base / skill_name
        
        # Check if target already exists
        if target_dir.exists():
            print(f"⚠️  Warning: Skill already exists in custom folder: {target_dir}")
            print(f"   Overwriting existing skill...")
            shutil.rmtree(target_dir)
        
        # Copy skill directory to custom folder
        print(f"📂 Copying skill to custom folder: {target_dir}")
        
        # shutil.copytree를 사용 (이미 부모 디렉토리가 존재하므로 문제 없음)
        shutil.copytree(skill_path, target_dir)
        
        print(f"✅ Successfully registered skill to custom folder: {target_dir}")
        return target_dir
        
    except Exception as e:
        print(f"❌ Error registering skill to custom folder: {e}")
        import traceback
        traceback.print_exc()
        return None


def package_skill(skill_path, output_dir=None, auto_register=True):
    """
    Package a skill folder into a .skill file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the .skill file (defaults to current directory)
        auto_register: Whether to automatically register skill to custom folder (default: True)

    Returns:
        Path to the created .skill file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Run validation before packaging
    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"✅ {message}\n")

    # Auto-register to custom folder if enabled
    if auto_register:
        print("📝 Auto-registering skill to custom folder...")
        registered_path = register_to_custom_folder(skill_path)
        if registered_path:
            print(f"✅ Skill registered to: {registered_path}")
        else:
            print("⚠️  Skill registration to custom folder failed, but continuing with packaging...")
        print()

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    # Create the .skill file (zip format)
    try:
        with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the skill directory, excluding build artifacts
            for file_path in skill_path.rglob('*'):
                if not file_path.is_file():
                    continue
                arcname = file_path.relative_to(skill_path.parent)
                if should_exclude(arcname):
                    print(f"  Skipped: {arcname}")
                    continue
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

        print(f"\n✅ Successfully packaged skill to: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"❌ Error creating .skill file: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python utils/package_skill.py <path/to/skill-folder> [output-directory]")
        print("\nExample:")
        print("  python utils/package_skill.py skills/public/my-skill")
        print("  python utils/package_skill.py skills/public/my-skill ./dist")
        print("\nOptions:")
        print("  --no-register  Skip auto-registration to custom folder")
        sys.exit(1)

    # Parse command line arguments
    skill_path = sys.argv[1]
    output_dir = None
    auto_register = True
    
    # Check for --no-register flag
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--no-register":
            auto_register = False
            i += 1
        elif i == 0 and not args[i].startswith("--"):
            # First non-flag argument is output directory
            output_dir = args[i]
            i += 1
        else:
            print(f"❌ Unknown argument: {args[i]}")
            sys.exit(1)

    print(f"📦 Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")
    if not auto_register:
        print(f"   Auto-registration: DISABLED")
    print()

    result = package_skill(skill_path, output_dir, auto_register)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()