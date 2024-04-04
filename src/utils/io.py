from yaml.loader import SafeLoader
import yaml
import torch
import random
import numpy as np
import argparse
import os
import hydra


def save_model(model, model_name):
    outputs_dir = hydra.core.hydra_config.HydraConfig.get().runtime.output_dir
    ckpts_dir = os.path.join(outputs_dir, 'ckpts')
    os.makedirs(ckpts_dir, exist_ok=True)
    model_path = os.path.join(ckpts_dir, model_name)
    torch.save(model.state_dict(), model_path)


def load_yaml_config(path):
    with open(path) as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data


def load_batch_to_device(batch, device):
    for key, value in batch.items():
        if isinstance(value, torch.Tensor):
            batch[key] = value.to(device)
    return batch


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_name", default="config_classification")
    parser.add_argument("--wandb_name", default=None)
    parser.add_argument("--sweep", default="sweep_classification.yaml")
    parser.add_argument("--n_runs", default=5, type=int)

    args = parser.parse_args()

    return args


def set_random_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.use_deterministic_algorithms(True)  # Needed for reproducible results
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
