# Load modules first
module load python/3.11
module load micromamba
eval "$(micromamba shell hook --shell bash)"
micromamba activate /groups/tylermillhouse/micromamba_envs/myenv

# Verify correct Python
python3 --version
# Should show Python 3.11.x

# Now generate prompts
python3 generate_prompts.py --game chicken_game