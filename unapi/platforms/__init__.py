import os
import glob
import importlib

# Get the path to the platforms directory
platforms_dir = os.path.dirname(__file__)

# Find all platform directories in the platforms directory
platform_dirs = glob.glob(os.path.join(platforms_dir, "*"))

# Loop through the platform directories and import their event class
for platform_dir in platform_dirs:
    platform_name = os.path.basename(platform_dir)
    event_file_path = os.path.join(platform_dir, "event.py")
    if os.path.exists(event_file_path):
        module_name = f"unapi.platforms.{platform_name}.event"
        module = importlib.import_module(module_name)
        event_class_name = f"{platform_name.capitalize()}Event"
        event_class = getattr(module, event_class_name)
        globals()[event_class_name] = event_class
