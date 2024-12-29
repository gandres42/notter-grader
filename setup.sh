# # install uv
# apt-get update
# apt-get install curl
# curl -LsSf https://astral.sh/uv/install.sh | sh
# source $HOME/.local/bin/env

# # install python
# uv python install 3.12.7

# delete env for testing purposes
rm -rf .venv pyproject.toml uv.lock .python-version

# create environment
uv init && rm hello.py README.md
uv add numpy matplotlib scipy nbconvert otter-grader ipykernel

# move everything in ./files to ./, create autograder.zip
moved_files=()
for file in ./files/*; do
    if [ -f "$file" ]; then
        mv "$file" ./ 
        moved_files+=("$(basename "$file")")
    fi
done
files_list=$(printf " %s" "${moved_files[@]}")
uv run otter generate $files_list