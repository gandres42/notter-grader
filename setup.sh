# install uv
apt-get update
apt-get install curl rsync
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# install python
uv python install 3.12.8

# prepare env in source folder
cd /autograder/source

# create environment
uv python pin 3.12.8
uv init --bare
uv add numpy matplotlib scipy nbconvert otter-grader ipykernel python-dotenv

# move provided files to /autograder/source
moved_files=()
for file in /autograder/source/files/*; do
    if [ -f "$file" ]; then
        cp "$file" ./ 
        moved_files+=("$(basename "$file")")
    fi
done

# generate autograder.zip
files_list=$(printf " %s" "${moved_files[@]}")
uv run otter generate $files_list

# move run_autograder to correct location
mv /autograder/source/run_autograder /autograder
