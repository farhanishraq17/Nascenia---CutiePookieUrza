# Phase 2 reproduction image — Nascenia Bengali Medical Dialogue
#
# Builds BOTH interpreters the routed pipeline needs, in one image:
#
#   /opt/nascenia/bin/python      transformers 4.57.3   -> champion branch (BanglaT5)
#   /opt/nascenia_q35/bin/python  transformers 5.14.1   -> specialist branch (Qwen3.5-2B)
#
# They cannot be merged. transformers 4.57 ties BanglaT5's shared/lm_head weights and 5.14 does
# not, so the two versions decode from DIFFERENT weights; rules §5.2 requires this pipeline to
# reproduce the submitted leaderboard CSV, and one shared env would silently break that.
#
# The base is plain python:3.11-slim, NOT a CUDA image: torch 2.8.0+cu128 ships its whole CUDA
# 12.8 userspace as the nvidia-*-cu12 wheels already pinned in the requirements files. Only the
# host NVIDIA driver is needed (>= 570 for cu128).
#
#   BUILD   docker build -t nascenia-phase2 -f env/Dockerfile .      # from the bundle root
#   RUN     docker run --rm --gpus all -v "$PWD:/bundle" nascenia-phase2 \
#             /bundle/scripts/run_bundle.sh /bundle/lookup/test.parquet /bundle/work/out.csv
#
# The image sets P2_ENV_CHAMPION / P2_ENV_SPECIALIST, so run_bundle.sh needs no arguments beyond
# its two paths.

FROM python:3.11-slim

# git: the csebuetnlp normalizer is pinned as a git+https requirement in BOTH envs and the
# champion branch hard-fails without it (omitting it left 16/1000 rows differing from the CSV).
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 🔴 torch==2.8.0+cu128 does NOT exist on plain PyPI. Without this index every `pip install -r`
# dies on the very first torch line. This is the single most likely way a fresh machine fails to
# reproduce, so it is baked in rather than left to the reader.
ENV PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cu128 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

COPY env/requirements_nascenia.txt     /tmp/req_champion.txt
COPY env/requirements_nascenia_q35.txt /tmp/req_specialist.txt

RUN python -m venv /opt/nascenia \
    && /opt/nascenia/bin/pip install --upgrade pip \
    && /opt/nascenia/bin/pip install -r /tmp/req_champion.txt

RUN python -m venv /opt/nascenia_q35 \
    && /opt/nascenia_q35/bin/pip install --upgrade pip \
    && /opt/nascenia_q35/bin/pip install -r /tmp/req_specialist.txt

# Fail at BUILD time, not three hours into a decode, if either stack resolved wrong.
RUN /opt/nascenia/bin/python -c \
      "import transformers,torch,normalizer; assert transformers.__version__.startswith('4.57'), transformers.__version__; print('champion  ok', transformers.__version__, torch.__version__)" \
 && /opt/nascenia_q35/bin/python -c \
      "import transformers,torch; assert transformers.__version__.startswith('5.14'), transformers.__version__; print('specialist ok', transformers.__version__, torch.__version__)"

ENV P2_ENV_CHAMPION=/opt/nascenia \
    P2_ENV_SPECIALIST=/opt/nascenia_q35 \
    HF_HOME=/tmp/hf \
    TOKENIZERS_PARALLELISM=false \
    PYTHONUNBUFFERED=1

WORKDIR /bundle
CMD ["bash", "-lc", "echo 'Mount the bundle at /bundle and run scripts/run_bundle.sh <test.parquet> <out.csv>'; echo; /opt/nascenia/bin/python -c 'import transformers;print(\"champion  transformers\", transformers.__version__)'; /opt/nascenia_q35/bin/python -c 'import transformers;print(\"specialist transformers\", transformers.__version__)'"]
