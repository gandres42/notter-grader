# install python
uv python install 3.12.8

# prepare env in source folder
cd /autograder/source

# create environment
uv python pin 3.12.8
uv init --bare
uv add numpy matplotlib scipy nbconvert otter-grader ipykernel python-dotenv

# generate autograder.zip
uv run otter generate $files_list