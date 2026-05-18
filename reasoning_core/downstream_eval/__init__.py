import lm_eval
from lm_eval.models.huggingface import HFLM
from lm_eval.api.task import ConfigurableTask
import numpy as np
from transformers import DataCollatorForSeq2Seq
from datasets import disable_progress_bar, get_dataset_config_names, load_dataset
from tqdm.auto import tqdm
from torch.utils.data import DataLoader
import torch
from tabulate import tabulate
from lm_eval.evaluator import evaluate
from lm_eval.tasks import TaskManager, get_task_dict

platinum = ['gsm8k','svamp','winograd_wsc']

platinum = [
    "drop",
    "gsm8k",
    "hotpotqa",
    "mmlu_math",
    "multiarith",
    "singleop",
    "singleq",
    "squad",
    "svamp",
    "tab_fact",
    #"vqa",
    "winograd_wsc",
    "bbh_logical_deduction_three_objects",
    "bbh_navigate",
    "bbh_object_counting",
]

harness_tasks = ['leaderboard_bbh',
    "cola", "sst2", "mnli", "qnli", "rte", "boolq", "copa", "cb",'commonsense_qa',
    "swag", "piqa", "openbookqa", "sciq", "triviaqa","arc_easy",'arc_challenge', "lambada_openai","lambada_standard",
    "tinyMMLU", "tinyHellaswag", "tinyWinogrande", "tinyArc", "tinyGSM8k", "winogrande",
    "anli_r1", "anli_r2", "anli_r3",
    ]     #social_iqa wsc prost: not working

logic_custom_task_configs = {
    "wanli": {
        "task": "wanli",
        "dataset_path": "alisawuffles/WANLI",
        "validation_split": "test",
        "output_type": "multiple_choice",
        "doc_to_text": "Premise: {{premise}}\nHypothesis: {{hypothesis}}\nLabel:",
        "doc_to_choice": '["entailment", "neutral", "contradiction"]',
        "doc_to_target": '{{["entailment", "neutral", "contradiction"].index(gold)}}',
        "metric_list": [{"metric": "acc", "aggregation": "mean", "higher_is_better": True}],
    },
    "hans": {
        "task": "hans",
        "dataset_path": "hans",
        "dataset_name": "plain_text",
        "validation_split": "validation",
        "output_type": "multiple_choice",
        "doc_to_text": "Premise: {{premise}}\nHypothesis: {{hypothesis}}\nLabel:",
        "doc_to_choice": '["entailment", "non-entailment"]',
        "doc_to_target": "{{label}}",
        "metric_list": [{"metric": "acc", "aggregation": "mean", "higher_is_better": True}],
    },
    "nan_nli": {
        "task": "nan_nli",
        "dataset_path": "joey234/nan-nli",
        "training_split": "train",
        "test_split": "train",
        "output_type": "multiple_choice",
        "doc_to_text": "Premise: {{premise}}\nHypothesis: {{hypothesis}}\nLabel:",
        "doc_to_choice": '["entailment", "neutral", "contradiction"]',
        "doc_to_target": '{{["entailment", "neutral", "contradiction"].index(label)}}',
        "metric_list": [{"metric": "acc", "aggregation": "mean", "higher_is_better": True}],
    },
    "folio": {
        "task": "folio",
        "dataset_path": "tasksource/folio",
        "validation_split": "validation",
        "output_type": "multiple_choice",
        "doc_to_text": "Premises:\n{{premises}}\nConclusion: {{conclusion}}\nLabel:",
        "doc_to_choice": '["True", "False", "Uncertain"]',
        "doc_to_target": '{{["True", "False", "Uncertain"].index(label)}}',
        "metric_list": [{"metric": "acc", "aggregation": "mean", "higher_is_better": True}],
    },
    "logiqa2_nli": {
        "task": "logiqa2_nli",
        "dataset_path": "tasksource/logiqa-2.0-nli",
        "validation_split": "validation",
        "output_type": "multiple_choice",
        "doc_to_text": "Premise: {{premise}}\nHypothesis: {{hypothesis}}\nLabel:",
        "doc_to_choice": '["entailment", "not-entailment"]',
        "doc_to_target": '{{["entailment", "not-entailment"].index(label)}}',
        "metric_list": [{"metric": "acc", "aggregation": "mean", "higher_is_better": True}],
    },
    "semantic_fragments_nli": {
        "task": "semantic_fragments_nli",
        "dataset_path": "tasksource/semantic_fragments_nli",
        "validation_split": "dev",
        "output_type": "multiple_choice",
        "doc_to_text": "Premise: {{sentence1}}\nHypothesis: {{sentence2}}\nLabel:",
        "doc_to_choice": '["entailment", "neutral", "contradiction"]',
        "doc_to_target": '{{["entailment", "neutral", "contradiction"].index(gold_label)}}',
        "metric_list": [{"metric": "acc", "aggregation": "mean", "higher_is_better": True}],
    },
    "control_nli": {
        "task": "control_nli",
        "dataset_path": "tasksource/ConTRoL-nli",
        "validation_split": "validation",
        "output_type": "multiple_choice",
        "doc_to_text": "Premise: {{premise}}\nHypothesis: {{hypothesis}}\nLabel:",
        "doc_to_choice": '["entailment", "neutral", "contradiction"]',
        "doc_to_target": '{{["entailment", "neutral", "contradiction"].index(label)}}',
        "metric_list": [{"metric": "acc", "aggregation": "mean", "higher_is_better": True}],
    },
    "boardgameqa": {
        "task": "boardgameqa",
        "dataset_path": "tasksource/Boardgame-QA",
        "validation_split": "valid",
        "output_type": "multiple_choice",
        "doc_to_text": "{{example}}\nAnswer:",
        "doc_to_choice": '["proved", "disproved", "unknown"]',
        "doc_to_target": '{{["proved", "disproved", "unknown"].index(label)}}',
        "metric_list": [{"metric": "acc", "aggregation": "mean", "higher_is_better": True}],
    },
    "commonsense_qa_2": {
        "task": "commonsense_qa_2",
        "dataset_path": "tasksource/commonsense_qa_2.0",
        "validation_split": "validation",
        "output_type": "multiple_choice",
        "doc_to_text": "{{question}}\nAnswer:",
        "doc_to_choice": '["yes", "no"]',
        "doc_to_target": '{{["yes", "no"].index(answer)}}',
        "metric_list": [{"metric": "acc", "aggregation": "mean", "higher_is_better": True}],
    },
    "math_qa": {
        "task": "math_qa",
        "dataset_path": "regisss/math_qa",
        "validation_split": "validation",
        "output_type": "multiple_choice",
        "doc_to_text": "{{Problem}}\n{{options}}\nAnswer:",
        "doc_to_choice": '["a", "b", "c", "d", "e"]',
        "doc_to_target": '{{["a", "b", "c", "d", "e"].index(correct)}}',
        "metric_list": [{"metric": "acc", "aggregation": "mean", "higher_is_better": True}],
    },
}

custom_tasks = {
    name: ConfigurableTask(config={
        "task": name, "dataset_path": path,
        "output_type": "multiple_choice",
        "test_split": "train", "doc_to_text": "",
        "doc_to_choice": '["{{sentence_good}}", "{{sentence_bad}}"]',
        "doc_to_target": 0,
        "metric_list": [{"metric": "acc", "aggregation": "mean", "higher_is_better": True}],
    })
    for name, path in [
        ("blimp", "tasksource/blimp"),
        ("zorro", "tasksource/zorro"),
    ]
}
default_logic_custom_task_configs = {
    name: config for name, config in logic_custom_task_configs.items()
    if name != "hans"
}
custom_tasks.update({name: ConfigurableTask(config=config) for name, config in default_logic_custom_task_configs.items()})

tasksource = ['ConTRoL-nli', 'folio','anli/a1','WANLI','sick/label','glue/rte','glue/cola','cladder']

downstream_tasks = tasksource + platinum 

def load_downstream(config):
    if config in platinum:
        df = load_dataset("madrylab/platinum-bench", config, split='test')
        df = df.to_pandas()
        df=df[df.cleaning_status!='rejected']
        df['answer']=df.platinum_target
        df['prompt'] = df.platinum_prompt_no_cot
        def evaluate_row(x):
            return x.extracted in [str(x).lower() for x in x.platinum_target]

    if config in tasksource:
        ds = load_dataset("tasksource/tasksource-instruct-v0",split='validation')
        df=ds.rename_column('inputs','prompt').to_pandas()
        df = df[df.task==config]
        df.targets=df.targets.map(lambda x:x.rstrip('.'))
        if len(df)>200:
            df=df.sample(200, random_state=0)
        def evaluate_row(x):
            prepr = lambda x: str(x).lower().strip()
            return prepr(x.extracted) == prepr(x.targets)
        
    return evaluate_row, df



def run_platinum(model, tokenizer, tasks=platinum, limit=200, batch_size=16, use_chat_template=False):
    disable_progress_bar(), model.eval()
    tasks = get_dataset_config_names("madrylab/platinum-bench")
    tasks.remove('vqa')
    collator = DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8)
    metrics = {}

    for t in tqdm(tasks):
        ds = load_dataset("madrylab/platinum-bench", t, split=f"test[:{limit}]")
        ds = ds.filter(lambda x: x['platinum_target'] is not None)
        def process(x):
            q_text = x['platinum_prompt_no_cot'] + "\n"
            if tokenizer.chat_template and use_chat_template:
                q_ids = tokenizer.apply_chat_template([{"role":"user", "content":q_text}], tokenize=True, add_generation_prompt=True)
            else:
                q_ids = tokenizer(q_text).input_ids
            a_ids = tokenizer(x['platinum_target'][0] + tokenizer.eos_token, add_special_tokens=False).input_ids
            return {"input_ids": q_ids + a_ids, "labels": [-100]*len(q_ids) + a_ids}

        dl = DataLoader(ds.map(process, remove_columns=ds.column_names), batch_size=batch_size, collate_fn=collator)
    
        with torch.no_grad():
            losses = [model(**{k: v.to(model.device) for k,v in b.items()}).loss.item() for b in dl]
        
        metrics[f"platinum/{t}/nll"] = float(np.mean(losses))
    
    metrics['platinum/platinum_avg/nll'] = np.mean(list(metrics.values()))
    print(tabulate(metrics.items()))
    return metrics






def pick_metric(m):
    return next((m[k] for k in ['mcc,none', 'acc_norm,none', 'acc,none'] if k in m), 0.)


def add_bbh0(s, hflm, task_manager, limit=200):
    def set_fewshot(task_dict, n):
        for x in task_dict.values():
            set_fewshot(x, n) if isinstance(x, dict) else x.set_config(key="num_fewshot", value=n)

    bbh = get_task_dict(["leaderboard_bbh"], task_manager)
    set_fewshot(bbh, 0)
    r = evaluate(lm=hflm, task_dict=bbh, limit=limit)['results']
    s["leaderboard_bbh_0shot"] = pick_metric(r["leaderboard_bbh"])
    return s


def run_harness(model, tokenizer, limit=200):
    hflm = HFLM(pretrained=model, tokenizer=tokenizer, batch_size="auto")
    task_manager = TaskManager()
    s = {}

    for t in harness_tasks:
        try:
            r = evaluate(lm=hflm, task_dict=get_task_dict([t], task_manager), limit=limit)['results']
            s[f"{t}_3shot" if t == "leaderboard_bbh" else t] = pick_metric(r[t])
        except Exception as e:
            print(f"Skipping {t}: {e}")

    for t, task in custom_tasks.items():
        try:
            r = evaluate(lm=hflm, task_dict={t: task}, limit=limit)['results']
            s[t] = pick_metric(r[t])
        except Exception as e:
            print(f"Skipping {t}: {e}")

    try:
        return add_bbh0(s, hflm, task_manager, limit)
    except Exception as e:
        print(f"Skipping leaderboard_bbh_0shot: {e}")
        return s
