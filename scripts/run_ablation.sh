#!/bin/bash
# Abort on error
set -e

# Configuration
TOTAL_SAMPLES=10000
EPOCHS=1
EVAL_SAMPLES=100               # internal RC-task eval (evaluate.py)

HUMANEVAL_N=20                 # completions/problem for pass@k
HUMANEVAL_K="1 5 10"
HUMANEVAL_TEMP=0.8
CRUXEVAL_N=1
CRUXEVAL_TEMP=0.0
EXTERNAL_RESULTS="experiments/external_eval_results.csv"

# 'baseline' trains on main_data ALONE (no synthetic aux) -- required to
# compute meaningful deltas for the other arms. 'all' equal-mixes all 4 tasks.
TASKS=("baseline" "all" "CodeRunnability" "CodeExecution" "CodeInputDeduction" "Consolidation")

mkdir -p experiments

for TASK in "${TASKS[@]}"; do
    echo "=========================================================="
    echo "Starting Pipeline for: $TASK"
    echo "=========================================================="

    DATASET_DIR="experiments/dataset_${TASK}"
    MODEL_DIR="experiments/model_${TASK}"

    if [ "$TASK" == "baseline" ]; then
        # 1. No generation step -- baseline has no synthetic aux data.
        echo "--> [1/4] baseline arm: no aux data to generate."

        # 2. Mix Data (main_data only)
        if [ ! -d "$DATASET_DIR" ]; then
            echo "--> [2/4] Building main_data-only dataset..."
            python data_mixing.py --out_dir "$DATASET_DIR"
        else
            echo "--> [2/4] $DATASET_DIR already exists. Skipping mixing."
        fi
    else
        AUX_DATA_FILE="experiments/aux_data_${TASK}.jsonl"

        # 1. Generate Data
        if [ ! -f "$AUX_DATA_FILE" ]; then
            echo "--> [1/4] Generating $TOTAL_SAMPLES samples for $TASK..."
            python data_generation.py --task "$TASK" --samples $TOTAL_SAMPLES --out "$AUX_DATA_FILE"
        else
            echo "--> [1/4] $AUX_DATA_FILE already exists. Skipping generation."
        fi

        # 2. Mix Data
        if [ ! -d "$DATASET_DIR" ]; then
            echo "--> [2/4] Mixing with Magicoder-OSS-Instruct-75K..."
            python data_mixing.py --aux_data "$AUX_DATA_FILE" --out_dir "$DATASET_DIR"
        else
            echo "--> [2/4] $DATASET_DIR already exists. Skipping mixing."
        fi
    fi

    # 3. Train
    if [ ! -d "$MODEL_DIR" ]; then
        echo "--> [3/4] Fine-tuning SmolLM2-135M on $TASK..."
        python train.py --dataset_dir "$DATASET_DIR" --output_model "$MODEL_DIR" --epochs $EPOCHS
    else
        echo "--> [3/4] $MODEL_DIR already exists. Skipping training."
    fi

    # 4. Evaluate & Record Metrics
    echo "--> [4/4] Evaluating $MODEL_DIR..."
    echo "    -- internal RC-task accuracy --"
    python evaluate.py --model_dir "$MODEL_DIR" --trained_task "$TASK" --samples $EVAL_SAMPLES

    echo "    -- external benchmarks (HumanEval pass@k, CRUXEval I+O) --"
    python evaluate_external.py \
        --model_dir "$MODEL_DIR" \
        --trained_task "$TASK" \
        --humaneval_n $HUMANEVAL_N \
        --humaneval_k $HUMANEVAL_K \
        --humaneval_temperature $HUMANEVAL_TEMP \
        --cruxeval_n $CRUXEVAL_N \
        --cruxeval_temperature $CRUXEVAL_TEMP \
        --results_file "$EXTERNAL_RESULTS"

    echo "Finished pipeline for $TASK."
done

echo "=========================================================="
echo "Ablation study complete! Summarizing influence vs. baseline..."
echo "=========================================================="
python summarize_external_results.py --results_file "$EXTERNAL_RESULTS" --out experiments/EXTERNAL_INFLUENCE.md
echo "Check experiments/ablation_results.csv (internal) and experiments/EXTERNAL_INFLUENCE.md (HumanEval/CRUXEval ranking)."