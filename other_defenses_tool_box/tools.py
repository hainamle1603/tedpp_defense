import torch
from torch import nn
import  torch.nn.functional as F
from torch.utils.data import Dataset
import os
from PIL import Image
from torchvision import transforms, datasets
from torch.utils.data import DataLoader
import random
import numpy as np
from torchvision.utils import save_image
from utils import supervisor
from utils.tools import IMG_Dataset
import config
from torch.utils import data
import torchvision.transforms.functional as Ft

class AverageMeter:
    """Computes and stores the average and current value"""

    def __init__(self, name: str = None, fmt: str = ':f'):
        self.name: str = name
        self.fmt = fmt
        self.reset()

    def reset(self):
        self.val = 0.
        self.avg = 0.
        self.sum = 0.
        self.count = 0

    def update(self, val: float, n: int = 1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

    def __str__(self):
        fmtstr = '{name} {val' + self.fmt + '} ({avg' + self.fmt + '})'
        return fmtstr.format(**self.__dict__)

def to_numpy(x, **kwargs) -> np.ndarray:
    if isinstance(x, torch.Tensor):
        x = x.detach().cpu().numpy()
    return np.array(x, **kwargs)

# Project function
def tanh_func(x: torch.Tensor) -> torch.Tensor:
    return (x.tanh() + 1) * 0.5

def generate_dataloader(dataset='cifar10', dataset_path='./data/', batch_size=128, split='train', shuffle=True, drop_last=False, data_transform=None, noisy_test=False):
    if dataset == 'cifar10':
        if data_transform is None:
            data_transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize([0.4914, 0.4822, 0.4465], [0.247, 0.243, 0.261]),
            ])
        dataset_path = os.path.join(dataset_path, 'cifar10')
        
        if noisy_test:
            from torch.utils.data import ConcatDataset
            noisy_test_set_dir = os.path.join('clean_set', 'cifar10', 'noisy_test_split')
            noisy_test_set_img_dir = os.path.join(noisy_test_set_dir, 'data')
            noisy_test_set_label_path = os.path.join(noisy_test_set_dir, 'labels')
            noisy_test_set = IMG_Dataset(data_dir=noisy_test_set_img_dir, label_path=noisy_test_set_label_path, transforms=data_transform)
            noisy_test_loader = torch.utils.data.DataLoader(noisy_test_set, batch_size=batch_size, shuffle=True, drop_last=drop_last, num_workers=4, pin_memory=True)
            return noisy_test_loader
        if split == 'train':
            train_data = datasets.CIFAR10(root=dataset_path, train=True, download=False, transform=data_transform)
            train_data_loader = torch.utils.data.DataLoader(dataset=train_data, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last, num_workers=4, pin_memory=True)
            return train_data_loader
        elif split == 'std_test' or split == 'full_test':
            test_data = datasets.CIFAR10(root=dataset_path, train=False, download=False, transform=data_transform)
            test_data_loader = torch.utils.data.DataLoader(dataset=test_data, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last, num_workers=4, pin_memory=True)
            return test_data_loader
        elif split == 'valid' or split == 'val':
            val_set_dir = os.path.join('clean_set', 'cifar10', 'clean_split')
            val_set_img_dir = os.path.join(val_set_dir, 'data')
            val_set_label_path = os.path.join(val_set_dir, 'clean_labels')
            val_set = IMG_Dataset(data_dir=val_set_img_dir, label_path=val_set_label_path, transforms=data_transform)
            val_loader = torch.utils.data.DataLoader(val_set, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last, num_workers=4, pin_memory=True)
            return val_loader
        elif split == 'test':
            test_set_dir = os.path.join('clean_set', 'cifar10', 'test_split')
            test_set_img_dir = os.path.join(test_set_dir, 'data')
            test_set_label_path = os.path.join(test_set_dir, 'labels')
            test_set = IMG_Dataset(data_dir=test_set_img_dir, label_path=test_set_label_path, transforms=data_transform)
            test_loader = torch.utils.data.DataLoader(test_set, batch_size=batch_size, shuffle=True, drop_last=drop_last, num_workers=4, pin_memory=True)
            return test_loader
    elif dataset == 'gtsrb':
        if data_transform is None:
            data_transform = transforms.Compose([
                transforms.Resize((32, 32)),
                transforms.ToTensor(),
                transforms.Normalize([0.3337, 0.3064, 0.3171], [0.2672, 0.2564, 0.2629]),
            ])
        dataset_path = os.path.join(dataset_path, 'gtsrb')
        
        if noisy_test:
            from torch.utils.data import ConcatDataset
            noisy_test_set_dir = os.path.join('clean_set', 'gtsrb', 'noisy_test_split')
            noisy_test_set_img_dir = os.path.join(noisy_test_set_dir, 'data')
            noisy_test_set_label_path = os.path.join(noisy_test_set_dir, 'labels')
            noisy_test_set = IMG_Dataset(data_dir=noisy_test_set_img_dir, label_path=noisy_test_set_label_path, transforms=data_transform)
            noisy_test_loader = torch.utils.data.DataLoader(noisy_test_set, batch_size=batch_size, shuffle=True, drop_last=drop_last, num_workers=4, pin_memory=True)
            return noisy_test_loader
        if split == 'train':
            train_data = datasets.GTSRB(root=dataset_path, split='train', download=False, transform=data_transform)
            train_data_loader = torch.utils.data.DataLoader(dataset=train_data, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last, num_workers=4, pin_memory=True)
            return train_data_loader
        elif split == 'std_test' or split == 'full_test':
            test_data = datasets.GTSRB(root=dataset_path, split='test', download=False, transform=data_transform)
            test_data_loader = torch.utils.data.DataLoader(dataset=test_data, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last, num_workers=4, pin_memory=True)
            return test_data_loader
        elif split == 'valid' or split == 'val':
            val_set_dir = os.path.join('clean_set', 'gtsrb', 'clean_split')
            val_set_img_dir = os.path.join(val_set_dir, 'data')
            val_set_label_path = os.path.join(val_set_dir, 'clean_labels')
            val_set = IMG_Dataset(data_dir=val_set_img_dir, label_path=val_set_label_path, transforms=data_transform)
            val_loader = torch.utils.data.DataLoader(val_set, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last, num_workers=4, pin_memory=True)
            return val_loader
        elif split == 'test':
            test_set_dir = os.path.join('clean_set', 'gtsrb', 'test_split')
            test_set_img_dir = os.path.join(test_set_dir, 'data')
            test_set_label_path = os.path.join(test_set_dir, 'labels')
            test_set = IMG_Dataset(data_dir=test_set_img_dir, label_path=test_set_label_path, transforms=data_transform)
            test_loader = torch.utils.data.DataLoader(test_set, batch_size=batch_size, shuffle=True, drop_last=drop_last, num_workers=4, pin_memory=True)
            return test_loader
    elif dataset == 'mnist':
        if data_transform is None:
            data_transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,))
            ])
        dataset_path = os.path.join(dataset_path, 'MNIST')

        if noisy_test:
            from torch.utils.data import ConcatDataset
            noisy_test_set_dir = os.path.join('clean_set', 'mnist', 'noisy_test_split')
            noisy_test_set_img_dir = os.path.join(noisy_test_set_dir, 'data')
            noisy_test_set_label_path = os.path.join(noisy_test_set_dir, 'labels')
            noisy_test_set = IMG_Dataset(data_dir=noisy_test_set_img_dir, label_path=noisy_test_set_label_path,
                                         transforms=data_transform)
            noisy_test_loader = torch.utils.data.DataLoader(noisy_test_set, batch_size=batch_size, shuffle=True,
                                                            drop_last=drop_last, num_workers=4, pin_memory=True)
            return noisy_test_loader
        if split == 'train':
            train_data = datasets.MNIST(root=dataset_path, train=True, download=False, transform=data_transform)
            train_data_loader = torch.utils.data.DataLoader(dataset=train_data, batch_size=batch_size, shuffle=shuffle,
                                           drop_last=drop_last, num_workers=4, pin_memory=True)
            return train_data_loader
        elif split == 'std_test' or split == 'full_test':
            test_data = datasets.MNIST(root=dataset_path, train=False, download=False, transform=data_transform)
            test_data_loader = torch.utils.data.DataLoader(dataset=test_data, batch_size=batch_size, shuffle=shuffle,
                                          drop_last=drop_last, num_workers=4, pin_memory=True)
            return test_data_loader
        elif split == 'valid' or split == 'val':
            val_set_dir = os.path.join('clean_set', 'mnist', 'clean_split')
            val_set_img_dir = os.path.join(val_set_dir, 'data')
            val_set_label_path = os.path.join(val_set_dir, 'clean_labels')
            val_set = IMG_Dataset(data_dir=val_set_img_dir, label_path=val_set_label_path, transforms=data_transform)
            val_loader = torch.utils.data.DataLoader(val_set, batch_size=batch_size, shuffle=shuffle,
                                                     drop_last=drop_last, num_workers=4, pin_memory=True)
            return val_loader
        elif split == 'test':
            test_set_dir = os.path.join('clean_set', 'mnist', 'test_split')
            test_set_img_dir = os.path.join(test_set_dir, 'data')
            test_set_label_path = os.path.join(test_set_dir, 'labels')
            test_set = IMG_Dataset(data_dir=test_set_img_dir, label_path=test_set_label_path, transforms=data_transform)
            test_loader = torch.utils.data.DataLoader(test_set, batch_size=batch_size, shuffle=True,
                                                      drop_last=drop_last, num_workers=4, pin_memory=True)
            return test_loader
    elif dataset == 'imagenette':
        if data_transform is None:
            data_transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])

        dataset_path = os.path.join(dataset_path, 'imagenette2')

        if split == 'train':
            train_data = datasets.ImageFolder(os.path.join(dataset_path, 'train'), data_transform)
            train_data_loader = torch.utils.data.DataLoader(dataset=train_data, batch_size=batch_size, shuffle=shuffle,
                                           drop_last=drop_last, num_workers=32, pin_memory=True)
            return train_data_loader
        elif split == 'std_test' or split == 'full_test':
            test_data = datasets.ImageFolder(os.path.join(dataset_path, 'val'), data_transform)
            test_data_loader = torch.utils.data.DataLoader(dataset=test_data, batch_size=batch_size, shuffle=shuffle,
                                          drop_last=drop_last, num_workers=32, pin_memory=True)
            return test_data_loader
        elif split == 'valid' or split == 'val':
            val_set_dir = os.path.join('clean_set', 'imagenette', 'clean_split')
            val_set_img_dir = os.path.join(val_set_dir, 'data')
            val_set_label_path = os.path.join(val_set_dir, 'clean_labels')
            val_set = IMG_Dataset(data_dir=val_set_img_dir, label_path=val_set_label_path, transforms=data_transform)
            val_loader = torch.utils.data.DataLoader(val_set, batch_size=batch_size, shuffle=shuffle,
                                                     drop_last=drop_last, num_workers=32, pin_memory=True)
            return val_loader
        elif split == 'test':
            test_set_dir = os.path.join('clean_set', 'imagenette', 'test_split')
            test_set_img_dir = os.path.join(test_set_dir, 'data')
            test_set_label_path = os.path.join(test_set_dir, 'labels')
            test_set = IMG_Dataset(data_dir=test_set_img_dir, label_path=test_set_label_path, transforms=data_transform)
            test_loader = torch.utils.data.DataLoader(test_set, batch_size=batch_size, shuffle=True,
                                                      drop_last=drop_last, num_workers=32, pin_memory=True)
            return test_loader

    elif dataset == 'imagenet50':
        if data_transform is None:
            data_transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])

        dataset_path = os.path.join(dataset_path, 'imagenet50')

        if split == 'train':
            train_data = datasets.ImageFolder(os.path.join(dataset_path, 'train'), data_transform)
            train_data_loader = torch.utils.data.DataLoader(dataset=train_data, batch_size=batch_size, shuffle=shuffle,
                                           drop_last=drop_last, num_workers=32, pin_memory=True)
            return train_data_loader
        elif split == 'std_test' or split == 'full_test':
            test_data = datasets.ImageFolder(os.path.join(dataset_path, 'val'), data_transform)
            test_data_loader = torch.utils.data.DataLoader(dataset=test_data, batch_size=batch_size, shuffle=shuffle,
                                          drop_last=drop_last, num_workers=32, pin_memory=True)
            return test_data_loader
        elif split == 'valid' or split == 'val':
            val_set_dir = os.path.join('clean_set', 'imagenet50', 'clean_split')
            val_set_img_dir = os.path.join(val_set_dir, 'data')
            val_set_label_path = os.path.join(val_set_dir, 'clean_labels')
            val_set = IMG_Dataset(data_dir=val_set_img_dir, label_path=val_set_label_path, transforms=data_transform)
            val_loader = torch.utils.data.DataLoader(val_set, batch_size=batch_size, shuffle=shuffle,
                                                     drop_last=drop_last, num_workers=32, pin_memory=True)
            return val_loader
        elif split == 'test':
            test_set_dir = os.path.join('clean_set', 'imagenet50', 'test_split')
            test_set_img_dir = os.path.join(test_set_dir, 'data')
            test_set_label_path = os.path.join(test_set_dir, 'labels')
            test_set = IMG_Dataset(data_dir=test_set_img_dir, label_path=test_set_label_path, transforms=data_transform)
            test_loader = torch.utils.data.DataLoader(test_set, batch_size=batch_size, shuffle=True,
                                                      drop_last=drop_last, num_workers=32, pin_memory=True)
            return test_loader

    elif dataset == 'imagenet100':
        if data_transform is None:
            data_transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])

        dataset_path = os.path.join(dataset_path, 'imagenet100')

        if split == 'train':
            train_data = datasets.ImageFolder(os.path.join(dataset_path, 'train'), data_transform)
            train_data_loader = torch.utils.data.DataLoader(dataset=train_data, batch_size=batch_size, shuffle=shuffle,
                                           drop_last=drop_last, num_workers=32, pin_memory=True)
            return train_data_loader
        elif split == 'std_test' or split == 'full_test':
            test_data = datasets.ImageFolder(os.path.join(dataset_path, 'val'), data_transform)
            test_data_loader = torch.utils.data.DataLoader(dataset=test_data, batch_size=batch_size, shuffle=shuffle,
                                          drop_last=drop_last, num_workers=32, pin_memory=True)
            return test_data_loader
        elif split == 'valid' or split == 'val':
            val_set_dir = os.path.join('clean_set', 'imagenet100', 'clean_split')
            val_set_img_dir = os.path.join(val_set_dir, 'data')
            val_set_label_path = os.path.join(val_set_dir, 'clean_labels')
            val_set = IMG_Dataset(data_dir=val_set_img_dir, label_path=val_set_label_path, transforms=data_transform)
            val_loader = torch.utils.data.DataLoader(val_set, batch_size=batch_size, shuffle=shuffle,
                                                     drop_last=drop_last, num_workers=32, pin_memory=True)
            return val_loader
        elif split == 'test':
            test_set_dir = os.path.join('clean_set', 'imagenet100', 'test_split')
            test_set_img_dir = os.path.join(test_set_dir, 'data')
            test_set_label_path = os.path.join(test_set_dir, 'labels')
            test_set = IMG_Dataset(data_dir=test_set_img_dir, label_path=test_set_label_path, transforms=data_transform)
            test_loader = torch.utils.data.DataLoader(test_set, batch_size=batch_size, shuffle=True,
                                                      drop_last=drop_last, num_workers=32, pin_memory=True)
            return test_loader

    elif dataset == 'imagenet200':
        if data_transform is None:
            data_transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])

        dataset_path = os.path.join(dataset_path, 'imagenet200')

        if split == 'train':
            train_data = datasets.ImageFolder(os.path.join(dataset_path, 'train'), data_transform)
            train_data_loader = torch.utils.data.DataLoader(dataset=train_data, batch_size=batch_size, shuffle=shuffle,
                                           drop_last=drop_last, num_workers=32, pin_memory=True)
            return train_data_loader
        elif split == 'std_test' or split == 'full_test':
            test_data = datasets.ImageFolder(os.path.join(dataset_path, 'val'), data_transform)
            test_data_loader = torch.utils.data.DataLoader(dataset=test_data, batch_size=batch_size, shuffle=shuffle,
                                          drop_last=drop_last, num_workers=32, pin_memory=True)
            return test_data_loader
        elif split == 'valid' or split == 'val':
            val_set_dir = os.path.join('clean_set', 'imagenet200', 'clean_split')
            val_set_img_dir = os.path.join(val_set_dir, 'data')
            val_set_label_path = os.path.join(val_set_dir, 'clean_labels')
            val_set = IMG_Dataset(data_dir=val_set_img_dir, label_path=val_set_label_path, transforms=data_transform)
            val_loader = torch.utils.data.DataLoader(val_set, batch_size=batch_size, shuffle=shuffle,
                                                     drop_last=drop_last, num_workers=32, pin_memory=True)
            return val_loader
        elif split == 'test':
            # test_set_dir = os.path.join('clean_set', 'imagenet200', 'test_split')
            # test_set_img_dir = os.path.join(test_set_dir, 'data')
            # test_set_label_path = os.path.join(test_set_dir, 'labels')
            # test_set = IMG_Dataset(data_dir=test_set_img_dir, label_path=test_set_label_path, transforms=data_transform)
            # test_loader = torch.utils.data.DataLoader(test_set, batch_size=batch_size, shuffle=True,
            #                                           drop_last=drop_last, num_workers=32, pin_memory=True)

            from torch.utils.data import ConcatDataset, DataLoader

            test_data = datasets.ImageFolder(os.path.join(dataset_path, 'test'), data_transform)
            val_data = datasets.ImageFolder(os.path.join(dataset_path, 'val'), data_transform)

            merged_data = ConcatDataset([test_data, val_data])
            test_loader = DataLoader(dataset=merged_data, batch_size=batch_size, shuffle=shuffle,
                                       drop_last=drop_last, num_workers=32, pin_memory=True)

            # test_data = datasets.ImageFolder(os.path.join(dataset_path, 'test'), data_transform)
            # test_loader = DataLoader(dataset=test_data, batch_size=batch_size, shuffle=shuffle,
            #                               drop_last=drop_last, num_workers=32, pin_memory=True)

            return test_loader

    elif dataset == 'tinyimagenet200':
        if data_transform is None:
            data_transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
            ])

        dataset_path = os.path.join(dataset_path, 'tinyimagenet200')

        if split == 'train':
            train_data = datasets.ImageFolder(os.path.join(dataset_path, 'train'), data_transform)
            train_data_loader = torch.utils.data.DataLoader(dataset=train_data, batch_size=batch_size, shuffle=shuffle,
                                           drop_last=drop_last, num_workers=32, pin_memory=True)
            return train_data_loader
        elif split == 'std_test' or split == 'full_test':
            test_data = datasets.ImageFolder(os.path.join(dataset_path, 'val'), data_transform)
            test_data_loader = torch.utils.data.DataLoader(dataset=test_data, batch_size=batch_size, shuffle=shuffle,
                                          drop_last=drop_last, num_workers=32, pin_memory=True)
            return test_data_loader
        elif split == 'valid' or split == 'val':
            val_set_dir = os.path.join('clean_set', 'tinyimagenet200', 'clean_split')
            val_set_img_dir = os.path.join(val_set_dir, 'data')
            val_set_label_path = os.path.join(val_set_dir, 'clean_labels')
            val_set = IMG_Dataset(data_dir=val_set_img_dir, label_path=val_set_label_path, transforms=data_transform)
            val_loader = torch.utils.data.DataLoader(val_set, batch_size=batch_size, shuffle=shuffle,
                                                     drop_last=drop_last, num_workers=32, pin_memory=True)
            return val_loader
        elif split == 'test':
            # test_set_dir = os.path.join('clean_set', 'tinyimagenet200', 'test_split')
            # test_set_img_dir = os.path.join(test_set_dir, 'data')
            # test_set_label_path = os.path.join(test_set_dir, 'labels')
            # test_set = IMG_Dataset(data_dir=test_set_img_dir, label_path=test_set_label_path, transforms=data_transform)
            # test_loader = torch.utils.data.DataLoader(test_set, batch_size=batch_size, shuffle=True,
            #                                           drop_last=drop_last, num_workers=32, pin_memory=True)

            from torch.utils.data import ConcatDataset, DataLoader

            test_data = datasets.ImageFolder(os.path.join(dataset_path, 'test'), data_transform)
            val_data = datasets.ImageFolder(os.path.join(dataset_path, 'val'), data_transform)

            merged_data = ConcatDataset([test_data, val_data])
            test_loader = DataLoader(dataset=merged_data, batch_size=batch_size, shuffle=shuffle,
                                       drop_last=drop_last, num_workers=32, pin_memory=True)

            # test_data = datasets.ImageFolder(os.path.join(dataset_path, 'test'), data_transform)
            # test_loader = DataLoader(dataset=test_data, batch_size=batch_size, shuffle=shuffle,
            #                               drop_last=drop_last, num_workers=32, pin_memory=True)

            return test_loader

    elif dataset == 'imagenet':
        from utils import imagenet
        if data_transform is None:
            data_transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
                transforms.CenterCrop(224),
            ])
        dataset_path = config.imagenet_dir
        train_set_dir = os.path.join(config.imagenet_dir, 'train')
        test_set_dir = os.path.join(config.imagenet_dir, 'val')
        if split == 'train':
            train_data = imagenet.imagenet_dataset(directory=train_set_dir, data_transform=data_transform, poison_directory=None,
                                             poison_indices=None, target_class=config.target_class['imagenet'], num_classes=1000)
            train_data_loader = torch.utils.data.DataLoader(dataset=train_data, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last, num_workers=32, pin_memory=True)
            return train_data_loader
        elif split == 'std_test' or split == 'full_test':
            test_data = imagenet.imagenet_dataset(directory=test_set_dir, shift=False, data_transform=data_transform,
                                                label_file=imagenet.test_set_labels, num_classes=1000)
            test_data_loader = torch.utils.data.DataLoader(dataset=test_data, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last, num_workers=32, pin_memory=True)
            return test_data_loader
        elif split == 'valid' or split == 'val':
            test_data = imagenet.imagenet_dataset(directory=test_set_dir, shift=False, data_transform=data_transform,
                                                label_file=imagenet.test_set_labels, num_classes=1000)
            val_split_meta_dir = os.path.join('clean_set', 'imagenet', 'clean_split')
            val_split_indices = torch.load(os.path.join(val_split_meta_dir, 'clean_split_indices'))
            val_set = torch.utils.data.Subset(test_data, val_split_indices)
            
            val_loader = torch.utils.data.DataLoader(val_set, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last, num_workers=32, pin_memory=True)
            return val_loader
        elif split == 'test':
            test_data = imagenet.imagenet_dataset(directory=test_set_dir, shift=False, data_transform=data_transform,
                                                label_file=imagenet.test_set_labels, num_classes=1000)
            test_split_meta_dir = os.path.join('clean_set', 'imagenet', 'test_split')
            test_indices = torch.load(os.path.join(test_split_meta_dir, 'test_indices'))
            test_data = torch.utils.data.Subset(test_data, test_indices)
            
            test_loader = torch.utils.data.DataLoader(test_data, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last, num_workers=32, pin_memory=True)
            return test_loader
    else:
        print('<To Be Implemented> Dataset = %s' % dataset)
        exit(0)

def unpack_poisoned_train_set(args, batch_size=128, shuffle=False, data_transform=None):
    """
    Return with `poison_set_dir`, `poisoned_set_loader`, `poison_indices`, and `cover_indices` if available
    """
    if data_transform is None:
        data_transform_aug, data_transform, trigger_transform, normalizer, denormalizer = supervisor.get_transforms(args)

    poison_set_dir = supervisor.get_poison_set_dir(args)

    if os.path.exists(os.path.join(poison_set_dir, 'data')): # if old version
        poisoned_set_img_dir = os.path.join(poison_set_dir, 'data')
    if os.path.exists(os.path.join(poison_set_dir, 'imgs')): # if new version
        poisoned_set_img_dir = os.path.join(poison_set_dir, 'imgs')
    poisoned_set_label_path = os.path.join(poison_set_dir, 'labels')
    poison_indices_path = os.path.join(poison_set_dir, 'poison_indices')
    cover_indices_path = os.path.join(poison_set_dir, 'cover_indices') # for adaptive attacks

    poisoned_set = IMG_Dataset(data_dir=poisoned_set_img_dir,
                                label_path=poisoned_set_label_path, transforms=data_transform)

    poisoned_set_loader = torch.utils.data.DataLoader(poisoned_set, batch_size=batch_size, shuffle=shuffle, num_workers=32, pin_memory=True)

    poison_indices = torch.load(poison_indices_path)
    
    if ('adaptive' in args.poison_type) or args.poison_type == 'TaCT':
        cover_indices = torch.load(cover_indices_path)
        return poison_set_dir, poisoned_set_loader, poison_indices, cover_indices
    
    return poison_set_dir, poisoned_set_loader, poison_indices, []

def jaccard_idx(mask: torch.Tensor, real_mask: torch.Tensor, select_num: int = 9) -> float:
    if select_num <= 0: return 0
    mask = mask.to(dtype=torch.float)
    real_mask = real_mask.to(dtype=torch.float)
    detect_mask = mask > mask.flatten().topk(select_num)[0][-1]
    sum_temp = detect_mask.int() + real_mask.int()
    overlap = (sum_temp == 2).sum().float() / (sum_temp >= 1).sum().float()
    return float(overlap)

def normalize_mad(values: torch.Tensor, side: str = None) -> torch.Tensor:
    if not isinstance(values, torch.Tensor):
        values = torch.tensor(values, dtype=torch.float)
    median = values.median()
    abs_dev = (values - median).abs()
    mad = abs_dev.median()
    measures = abs_dev / mad / 1.4826
    if side == 'double':    # TODO: use a loop to optimie code
        dev_list = []
        for i in range(len(values)):
            if values[i] <= median:
                dev_list.append(float(median - values[i]))
        mad = torch.tensor(dev_list).median()
        for i in range(len(values)):
            if values[i] <= median:
                measures[i] = abs_dev[i] / mad / 1.4826

        dev_list = []
        for i in range(len(values)):
            if values[i] >= median:
                dev_list.append(float(values[i] - median))
        mad = torch.tensor(dev_list).median()
        for i in range(len(values)):
            if values[i] >= median:
                measures[i] = abs_dev[i] / mad / 1.4826
    return measures

def to_list(x) -> list:
    if isinstance(x, (torch.Tensor, np.ndarray)):
        return x.tolist()
    return list(x)

def val_atk(args, model, split='test', batch_size=100):
    """
    Validate the attack (described in `args`) on `model`
    """
    model.eval()
    data_transform_aug, data_transform, trigger_transform, normalizer, denormalizer = supervisor.get_transforms(args)

    poison_transform = supervisor.get_poison_transform(poison_type=args.poison_type, dataset_name=args.dataset,
                                                       target_class=config.target_class[args.dataset],
                                                       trigger_transform=trigger_transform,
                                                       is_normalized_input=(not args.no_normalize),
                                                       alpha=args.alpha if args.test_alpha is None else args.test_alpha,
                                                       trigger_name=args.trigger, args=args)
    test_loader = generate_dataloader(dataset=args.dataset, dataset_path=config.data_dir, batch_size=batch_size, split=split, shuffle=False, drop_last=False, data_transform=data_transform)

    if args.dataset == 'cifar10': num_classes = 10
    elif args.dataset == 'mnist': num_classes = 10
    elif args.dataset == 'gtsrb': num_classes = 43
    elif args.dataset == 'imagenet': num_classes = 1000
    elif args.dataset == 'imagenette': num_classes = 10
    elif args.dataset == 'imagenet50': num_classes = 50
    elif args.dataset == 'imagenet100': num_classes = 100
    elif args.dataset == 'imagenet200': num_classes = 200
    elif args.dataset == 'tinyimagenet200': num_classes = 200
    else: num_classes = 10
    
    if args.poison_type == 'TaCT' or args.poison_type == 'SleeperAgent':
        source_classes = [config.source_class]
    else:
        source_classes = None

    from utils.tools import test
    ca, asr = test(model=model, test_loader=test_loader, poison_test=True, poison_transform=poison_transform, num_classes=num_classes, source_classes=source_classes, all_to_all=('all_to_all' in args.poison_type))
    return ca, asr, 0

def accuracy(output, target, topk=(1,)):
    """Computes the precision@k for the specified values of k"""
    maxk = max(topk)
    batch_size = target.size(0)

    _, pred = output.topk(maxk, 1, True, True)
    pred = pred.t()
    correct = pred.eq(target.view(1, -1).expand_as(pred))

    res = []
    for k in topk:
        correct_k = correct[:k].reshape(-1).float().sum(0)
        res.append(correct_k.mul_(100.0 / batch_size))
    return res

class Cutout(object):
    """Randomly mask out one or more patches from an image.
    Args:
        n_holes (int): Number of patches to cut out of each image.
        length (int): The length (in pixels) of each square patch.
    """
    def __init__(self, n_holes, length):
        self.n_holes = n_holes
        self.length = length

    def __call__(self, img):
        """
        Args:
            img (Tensor): Tensor image of size (C, H, W).
        Returns:
            Tensor: Image with n_holes of dimension length x length cut out of it.
        """
        h = img.size(1)
        w = img.size(2)

        mask = torch.ones((h, w))

        for n in range(self.n_holes):
            y = torch.randint(high=h, size=(1, 1))
            x = torch.randint(high=w, size=(1, 1))

            y1 = torch.clip(y - self.length // 2, 0, h)
            y2 = torch.clip(y + self.length // 2, 0, h)
            x1 = torch.clip(x - self.length // 2, 0, w)
            x2 = torch.clip(x + self.length // 2, 0, w)

            mask[y1: y2, x1: x2] = 0.

        mask = mask.expand_as(img)
        img = img * mask

        return img

class CelebA_attr(data.Dataset):
    def __init__(self, data_dir, split, transforms, download):
        self.dataset = datasets.CelebA(root=data_dir, split=split, target_type="attr", download=download)
        self.list_attributes = [18, 31, 21]
        self.transforms = transforms
        self.split = split

    def _convert_attributes(self, bool_attributes):
        return (bool_attributes[0] << 2) + (bool_attributes[1] << 1) + (bool_attributes[2])

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, index):
        input, target = self.dataset[index]
        input = self.transforms(input)
        target = self._convert_attributes(target[self.list_attributes])
        return (input, target)