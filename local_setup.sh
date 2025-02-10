# create environment
uv python pin 3.12.8
uv init --bare
uv add numpy matplotlib scipy nbconvert otter-grader ipykernel python-dotenv

# move provided files to /autograder/source
moved_files=()
for file in ./files/*; do
    if [ -f "$file" ]; then
        cp "$file" ./ 
        moved_files+=("$(basename "$file")")
    fi
done

# generate autograder.zip
files_list=$(printf " %s" "${moved_files[@]}")

# generate autograder.zip
uv run otter generate $files_list