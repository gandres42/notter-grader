apt-get update
apt-get install curl
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

uv python install 3.12.7
uv init && rm hello.py README.md
uv add numpy matplotlib scipy nbconvert otter-grader ipykernel