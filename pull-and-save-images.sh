#!/bin/bash

# Exit on error
set -e

# Create docker directory if it doesn't exist
mkdir -p docker

# Load environment variables from vda/.env
if [ -f "vda/.env" ]; then
  echo "Loading environment variables from vda/.env..."
  while IFS= read -r line || [ -n "$line" ]; do
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$line" ]] && continue
    if [[ "$line" == *"="* ]]; then
      key=$(echo "$line" | cut -d'=' -f1 | xargs)
      val=$(echo "$line" | cut -d'=' -f2- | xargs)
      val="${val#\"}"
      val="${val%\"}"
      val="${val#\'}"
      val="${val%\'}"
      export "$key"="$val"
    fi
  done < "vda/.env"
fi

# Load environment variables from vda/.env-vda
if [ -f "vda/.env-vda" ]; then
  echo "Loading environment variables from vda/.env-vda..."
  while IFS= read -r line || [ -n "$line" ]; do
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$line" ]] && continue
    if [[ "$line" == *"="* ]]; then
      key=$(echo "$line" | cut -d'=' -f1 | xargs)
      val=$(echo "$line" | cut -d'=' -f2- | xargs)
      val="${val#\"}"
      val="${val%\"}"
      val="${val#\'}"
      val="${val%\'}"
      export "$key"="$val"
    fi
  done < "vda/.env-vda"
fi

YAML_FILE="vda-deploy.yaml"
if [ ! -f "$YAML_FILE" ]; then
  echo "Error: $YAML_FILE not found."
  exit 1
fi

echo "Parsing images from $YAML_FILE..."

# Temporary file to store raw extracted images
TEMP_IMAGES_FILE=$(mktemp)
trap 'rm -f "$TEMP_IMAGES_FILE"' EXIT

# Extract images, ignoring comments
while IFS= read -r line || [ -n "$line" ]; do
  # Skip commented lines
  if [[ "$line" =~ ^[[:space:]]*# ]]; then
    continue
  fi

  # Check if line contains image: or x-superset-image:
  if [[ "$line" =~ [[:space:]]*(image:|x-superset-image:) ]]; then
    # Extract the image name using sed
    image_raw=$(echo "$line" | sed -E 's/^[[:space:]]*(image:|x-superset-image:)[[:space:]]*(&[^[:space:]]+[[:space:]]+)?["'\'']?([^"'\''[:space:]]+)["'\'']?.*$/\3/')
    if [ -n "$image_raw" ]; then
      echo "$image_raw" >> "$TEMP_IMAGES_FILE"
    fi
  fi
done < "$YAML_FILE"

# Resolve variables and get unique images
declare -A unique_images
while IFS= read -r img_raw || [ -n "$img_raw" ]; do
  # Resolve environment variables
  resolved_img=$(eval echo "\"$img_raw\"")
  if [ -n "$resolved_img" ]; then
    unique_images["$resolved_img"]=1
  fi
done < "$TEMP_IMAGES_FILE"

echo "Found the following unique docker images:"
for img in "${!unique_images[@]}"; do
  echo "  - $img"
done

# Pull and save images
for img in "${!unique_images[@]}"; do
  echo -e "\n--- Processing $img ---"
  
  echo "Running: docker pull $img"
  if ! docker pull "$img"; then
    echo "Warning: Failed to pull $img. Skipping..."
    continue
  fi
  
  # Create a safe filename for the tar
  safe_name=$(echo "$img" | sed 's/[\/:]/_/g').tar
  tar_path="docker/$safe_name"
  
  echo "Running: docker save -o $tar_path $img"
  if docker save -o "$tar_path" "$img"; then
    echo "Successfully saved $img to $tar_path"
  else
    echo "Error: Failed to save $img"
  fi
done

echo -e "\nFinished processing all images!"
