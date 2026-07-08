#!/bin/bash
set -e

NFS_BASE="/mnt/nfs_share_magnet2/rrajanah"
REPO="${NFS_BASE}/reasoning-core/scripts"
RESULTS="${NFS_BASE}/results"
LOGS="${RESULTS}/logs"
CONDA_DIR="${NFS_BASE}/envs/miniconda3"
ENV_DIR="${NFS_BASE}/envs/rc_exp"

export HF_HOME="${NFS_BASE}/hf_cache"
export HF_DATASETS_CACHE="${NFS_BASE}/hf_cache/datasets"
export TRANSFORMERS_CACHE="${NFS_BASE}/hf_cache/hub"
export TOKENIZERS_PARALLELISM="false"
export WANDB_MODE=disabled

mkdir -p "${LOGS}" "${REPO}/experiments"

eval "$("${CONDA_DIR}/bin/conda" shell.bash hook)"
conda activate "${ENV_DIR}"

cd "${REPO}"

TOKEN_BUDGET="300_000_000"
AUX_RATIO="0.2"
EVAL_SAMPLES=100
EXTERNAL_RESULTS="${RESULTS}/external_eval_results.csv"
INTERNAL_RESULTS="${RESULTS}/ablation_results.csv"

TASKS=("baseline" "all" "code_runnability" "code_execution" "code_input_deduction" "code_consolidation")

find_latest_checkpoint() {
    # Find the most recently modified checkpoint across all run hashes
    find "${REPO}/checkpoints" -type d -name "checkpoint-*" 2>/dev/null \
        | xargs -I{} stat --format="%Y {}" {} 2>/dev/null \
        | sort -n | tail -1 | awk '{print $2}'
}

run_arm() {
    local TASK=$1
    local LOG="${LOGS}/${TASK}.log"

    echo "==========================================" | tee "${LOG}"
    echo "Arm: ${TASK}  started: $(date)" | tee -a "${LOG}"
    echo "Machine: $(hostname)" | tee -a "${LOG}"
    nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader | tee -a "${LOG}"
    echo "==========================================" | tee -a "${LOG}"

    # ── Map run_sft task name to data_generation.py class name ─────────────
    case "${TASK}" in
        code_runnability)     CLASS="CodeRunnability" ;;
        code_execution)       CLASS="CodeExecution" ;;
        code_input_deduction) CLASS="CodeInputDeduction" ;;
        code_consolidation)   CLASS="Consolidation" ;;
        all)                  CLASS="all" ;;
        baseline)             CLASS="" ;;
    esac

    AUX_JSONL="experiments/aux_data_${TASK}.jsonl"

    # ── Step 1: Data generation ─────────────────────────────────────────────
    if [ "${TASK}" == "baseline" ]; then
        echo "[1/4] baseline: no aux data needed" | tee -a "${LOG}"
    else
        if [ ! -f "${AUX_JSONL}" ]; then
            echo "[1/4] Generating ${CLASS} (80/10/10 level split)..." | tee -a "${LOG}"
            WORKERS=2
            [ "${CLASS}" != "Consolidation" ] && WORKERS=4
            python3 data_generation.py \
                --task "${CLASS}" --samples 10000 \
                --workers "${WORKERS}" --out "${AUX_JSONL}" 2>&1 | tee -a "${LOG}"
        else
            echo "[1/4] ${AUX_JSONL} exists, skipping" | tee -a "${LOG}"
        fi
    fi

    # ── Step 2: Training via run_sft.py ────────────────────────────────────
    echo "[2/4] Training (run_sft.py, token_budget=${TOKEN_BUDGET})..." | tee -a "${LOG}"

    # Touch a marker so we can find the checkpoint created by this run
    MARKER=$(mktemp)

    if [ "${TASK}" == "baseline" ]; then
        python3 run_sft.py \
            --model_name smol135 \
            --main_data dolci \
            --aux_ratio 0.0 \
            --token_budget "${TOKEN_BUDGET}" \
            --from_scratch False \
            2>&1 | tee -a "${LOG}"
    else
        python3 run_sft.py \
            --model_name smol135 \
            --main_data dolci \
            --aux_ratio "${AUX_RATIO}" \
            --token_budget "${TOKEN_BUDGET}" \
            --aux_data_path "${AUX_JSONL}" \
            --aux_task "${TASK}" \
            --from_scratch False \
            2>&1 | tee -a "${LOG}"
    fi

    # Find the checkpoint that was just written (newer than our marker)
    CKPT=$(find "${REPO}/checkpoints" -type d -name "checkpoint-*" -newer "${MARKER}" 2>/dev/null \
           | xargs -I{} stat --format="%Y {}" {} 2>/dev/null \
           | sort -n | tail -1 | awk '{print $2}')
    rm -f "${MARKER}"

    if [ -z "${CKPT}" ]; then
        echo "ERROR: no checkpoint found for ${TASK}. Check ${LOG}." | tee -a "${LOG}"
        return 1
    fi
    echo "Checkpoint: ${CKPT}" | tee -a "${LOG}"

    # ── Step 3: Internal RC-task accuracy ──────────────────────────────────
    echo "[3/4] Internal eval..." | tee -a "${LOG}"
    python3 evaluate.py \
        --model_dir "${CKPT}" \
        --trained_task "${TASK}" \
        --samples "${EVAL_SAMPLES}" \
        --results_file "${INTERNAL_RESULTS}" 2>&1 | tee -a "${LOG}"

    # ── Step 4: External benchmarks (HumanEval + CRUXEval) ─────────────────
    echo "[4/4] External eval..." | tee -a "${LOG}"
    python3 evaluate_external.py \
        --model_dir "${CKPT}" \
        --trained_task "${TASK}" \
        --humaneval_n 20 \
        --humaneval_k 1 5 10 \
        --humaneval_temperature 0.8 \
        --cruxeval_n 1 \
        --cruxeval_temperature 0.0 \
        --results_file "${EXTERNAL_RESULTS}" 2>&1 | tee -a "${LOG}"

    echo "Arm ${TASK} done at $(date)" | tee -a "${LOG}"
}

# ── Run all arms sequentially ───────────────────────────────────────────────
for TASK in "${TASKS[@]}"; do
    echo ""
    echo "=========================================="
    echo "  Starting arm: ${TASK}  ($(date))"
    echo "=========================================="
    run_arm "${TASK}"
    echo "Cooling 3 minutes before next arm..."
    sleep 180
done

echo ""
echo "All arms complete at $(date)"
python3 summarize_external_results.py \
    --results_file "${EXTERNAL_RESULTS}" \
    --out "${RESULTS}/EXTERNAL_INFLUENCE.md"
cat "${RESULTS}/EXTERNAL_INFLUENCE.md"