import re
with open("src/dashboard_server.py", "r") as f:
    content = f.read()

# Remove the duplicated int_fields
content = re.sub(r'elif key in int_fields:\s+setattr\(settings, key, int\(value\)\)\s+applied\[key\] = int\(value\)', '', content)

# Inject settings.save() right before self.send_response(200) for /api/settings
content = re.sub(r'(applied\[key\] = int\(float\(value\)\)\s+)self\.send_response\(200\)', r'\1\n        settings.save()\n        self.send_response(200)', content)

# Inject settings.save() for /api/camera
content = re.sub(r'(elif action == "night_vision": setattr\(settings, "cam_night", val is True or val == "on"\)\s+)', r'\1\n                settings.save()\n                ', content)

with open("src/dashboard_server.py", "w") as f:
    f.write(content)
