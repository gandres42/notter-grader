# create environment
uv python pin 3.12.7
uv venv
uv pip install numpy matplotlib scipy nbconvert otter-grader ipykernel python-dotenv htmlmin

# move provided files to /autograder/source
source_dir="./files"
dest_dir="."
moved_files=()
while IFS= read -r item; do
  relative_path="${item#$source_dir/}"
  dest_item="$dest_dir/$relative_path"
  if [ ! -e "$dest_item" ]; then
    if [ -d "$item" ]; then
      mkdir -p "$dest_item"
    else
      cp "$item" "$dest_item"
      # escaped_path=$(echo "$dest_item" | sed 's/ /\ /g' | sed 's/[^a-zA-Z0-9_\/.-]/\\&/g')
      moved_files+=("$dest_item")
    fi
  fi
done < <(find "$source_dir" -mindepth 1 -type f -o -type d)

# generate autograder.zip
echo "${moved_files[@]}"
uv run otter generate "${moved_files[@]}"