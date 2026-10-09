import glob

for file in glob.glob("src/*eye.py"):
    with open(file, "r") as f:
        content = f.read()
    
    # Remove the `import random` line that was placed inside the if block
    content = content.replace("                import random\n", "")
    
    with open(file, "w") as f:
        f.write(content)
    print(f"Fixed {file}")
