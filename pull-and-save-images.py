import os
import re
import subprocess
import sys

def main():
    # Load env variables from vda/.env and vda/.env-vda
    env = {}
    for env_file in ['vda/.env', 'vda/.env-vda']:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, val = line.split('=', 1)
                        # Strip quotes if present
                        val = val.strip().strip('\'"')
                        env[key.strip()] = val

    # Also merge actual os.environ
    env_merged = os.environ.copy()
    env_merged.update(env)

    # Find all images in vda-deploy.yaml
    images = []
    yaml_path = 'vda-deploy.yaml'
    if not os.path.exists(yaml_path):
        print(f"Error: {yaml_path} not found.")
        sys.exit(1)

    with open(yaml_path, 'r') as f:
        for line in f:
            # Check if it's commented out
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            
            # Check image:
            img_match = re.search(r'\bimage:\s*["\']?([^"\']+)["\']?', line)
            if img_match:
                images.append(img_match.group(1).strip())
                continue
                
            # Check x-superset-image:
            sup_match = re.search(r'\bx-superset-image:\s*(?:&\S+\s+)?["\']?([^"\']+)["\']?', line)
            if sup_match:
                images.append(sup_match.group(1).strip())

    # Substitute env variables in images
    resolved_images = []
    for img in images:
        # Resolve variables like ${VAR} or $VAR
        def repl(match):
            var_name = match.group(1) or match.group(2)
            return env_merged.get(var_name, '')
        
        resolved = re.sub(r'\$\{(\w+)\}|\$(\w+)', repl, img)
        if resolved:
            resolved_images.append(resolved)

    # Deduplicate images
    unique_images = []
    for img in resolved_images:
        if img not in unique_images:
            unique_images.append(img)

    print("Found the following unique docker images:")
    for img in unique_images:
        print(f"  - {img}")

    # Create docker directory if it doesn't exist
    os.makedirs('docker', exist_ok=True)

    # Pull and save images
    for img in unique_images:
        print(f"\n--- Processing {img} ---")
        # Pull
        pull_cmd = ['docker', 'pull', img]
        print(f"Running: {' '.join(pull_cmd)}")
        try:
            subprocess.run(pull_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to pull {img}: {e}")
            continue
        
        # Save
        # Create a safe filename for the tar
        safe_name = img.replace('/', '_').replace(':', '_') + '.tar'
        tar_path = os.path.join('docker', safe_name)
        save_cmd = ['docker', 'save', '-o', tar_path, img]
        print(f"Running: {' '.join(save_cmd)}")
        try:
            subprocess.run(save_cmd, check=True)
            print(f"Saved {img} to {tar_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to save {img}: {e}")

if __name__ == '__main__':
    main()
