import hydra
import torch
import torch.nn as nn
from hydra.core.config_store import ConfigStore
import albumentations as A
from albumentations.pytorch import ToTensorV2

from src.config import Configuration
from src.datasets import UCFDataset
from src.models import CNNLSTM
from src.trainers import ClassificationTrainer

cs = ConfigStore.instance()
# Registering the Config class with the name 'config'.
cs.store(name="config", node=Configuration)


@hydra.main(version_base=None, config_path=".", config_name="config.yaml")
def main(config: Configuration) -> None:
    # transforms
    transforms_train = A.Compose([
        A.Resize(width=224, height=224),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2(),
    ])
    transforms_val = A.Compose([
        A.Resize(width=224, height=224),
        A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ToTensorV2(),
    ])

    # create the dataset
    train_dataset = UCFDataset(train=True, data_path=config.data_path, transforms=transforms_train)
    valid_dataset = UCFDataset(train=False, data_path=config.data_path, transforms=transforms_val)

    # create the dataloaders
    train_dl = torch.utils.data.DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    val_dl = torch.utils.data.DataLoader(valid_dataset, batch_size=config.batch_size, shuffle=True)

    # create the model
    model = CNNLSTM(n_classes=train_dataset.n_classes)

    # create the loss function
    criterion = nn.CrossEntropyLoss()

    # instantiate the optimizer and scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr)
    # scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=config.max_lr,
    #                                                 total_steps=config.n_epochs * len(train_dl))

    # initialize trainer
    trainer = ClassificationTrainer(
        config=config,
        train_dl=train_dl,
        val_dl=val_dl,
        criterion=criterion,
        model=model,
        optimizer=optimizer,
        # scheduler=scheduler,
    )

    # start training
    best_metric = trainer.fit()
    trainer.evaluate()

    return best_metric


if __name__ == "__main__":
    main()
