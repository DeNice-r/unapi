import os
import glob
import importlib

# Get the path to the platforms directory
platforms_dir = os.path.dirname(__file__)

# Find all platform directories in the platforms directory
platform_dirs = glob.glob(os.path.join(platforms_dir, "*"))

# Import all platform packages
for platform_dir in platform_dirs:
    platform_name = os.path.basename(platform_dir)
    if os.path.exists(os.path.join(platform_dir, "__init__.py")):
        package_name = f"{__package__}.{platform_name}"
        importlib.import_module(package_name)
