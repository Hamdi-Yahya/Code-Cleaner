# Code Cleaner

Enterprise-grade multi-language comment removal tool that safely removes comments from source code files.

## Features

- **Multi-language Support**: Python, JavaScript/TypeScript, PHP, Java, C/C++, Go, HTML, CSS
- **Safe Comment Removal**: Removes comments outside string literals only
- **Syntax Validation**: Validates code syntax before overwriting files
- **Auto-excluded Folders**: Automatically protects critical directories:
  - `node_modules`, `vendor`, `.git`, `venv`, `dist`, `build`, `.next`, `storage`, `bootstrap`
- **Parallel Processing**: Multi-core support for high performance
- **Backup Mode**: Creates backups before modifying files
- **Dry-run Mode**: Preview changes without applying them

## Requirements

- Python 3.9+

Optional (for syntax validation):
- Node.js (for JS/TS validation)
- PHP CLI (for PHP validation)
- GCC (for C/C++ validation)

## Installation

```
bash
git clone https://github.com/yourusername/code-cleaner.git
cd code-cleaner
```

## Usage

### Basic Usage
Removes comments and directly overwrites files without backup or syntax validation.
```
bash
python code_cleaner.py --path "/your/project/path"
```

### Recommended Safe Mode
Removes comments, validates syntax before saving, and creates backup files.
Files that fail validation will be skipped automatically.
```
bash
python code_cleaner.py --path "/your/project/path" --validate --backup
```

### Dry Run (Preview Only)
Shows which files would be processed without modifying any file.
```
bash
python code_cleaner.py --path "/your/project/path" --dry-run
```

## Example

```
bash
python code_cleaner.py --path "D:\Project" --validate --backup 
```

## Important Notes

- Always test using `--dry-run` first
- Use `--backup` when running on production projects
- Excluded folders will never be modified
- Syntax validation skips files that would become invalid
