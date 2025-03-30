# install uv
apt-get update
apt-get install curl rsync
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# install python
uv python install 3.12.7

# prepare env in source folder
cd /autograder/source

# create environment
uv python pin 3.12.7
uv init --bare
uv add numpy matplotlib scipy nbconvert otter-grader ipykernel python-dotenv htmlmin bleach pillow

# move provided files to /autograder/source
moved_files=()
for file in ./files/*; do
    cp -r "$file" ./ 
    moved_files+=("$(basename "$file")")
done

# generate autograder.zip
files_list=$(printf " %s" "${moved_files[@]}")
uv run otter generate $files_list

# move run_autograder to correct location
mv /autograder/source/run_autograder /autograder
