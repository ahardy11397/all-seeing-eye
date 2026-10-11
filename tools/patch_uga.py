import re
from pathlib import Path

# Files to patch
files = ["src/main.py", "src/dashboard.py", "run_stream.py"]

for f in files:
    path = Path(f)
    if not path.exists(): continue
    content = path.read_text()
    
    # 1. Add import
    if "from uga_logo import UgaLogo" not in content:
        content = re.sub(r'(from dancing_skeleton import DancingSkeleton)', r'\1\nfrom uga_logo import UgaLogo', content)
        
    # 2. Add instantiation
    # find where dancing_skeleton is created
    # elif current_eye_type == "dancing_skeleton": eye = DancingSkeleton(...)
    if "current_eye_type == \"uga_logo\"" not in content:
        content = re.sub(
            r'(elif current_eye_type == "dancing_skeleton":[^ \n]* [^ \n]* = DancingSkeleton\([^)]+\))',
            r'\1\n\n                elif current_eye_type == "uga_logo": eye = UgaLogo(settings.width, settings.height)',
            content
        )
        # Note: the regex for instantiation might need to be adjusted based on formatting
        
    path.write_text(content)

# Patch dashboard_server.py
server_path = Path("src/dashboard_server.py")
if server_path.exists():
    server_content = server_path.read_text()
    if 'value="uga_logo"' not in server_content:
        server_content = server_content.replace(
            '<option value="dancing_skeleton">Dancing Skeleton</option>',
            '<option value="dancing_skeleton">Dancing Skeleton</option>\n            <option value="uga_logo">UGA Logo</option>'
        )
        server_path.write_text(server_content)

print("Patching complete.")
