import numpy as np
import torch
import os
from torchvision import transforms,datasets
import argparse
import random
import torch.optim as optim
from torch.optim.lr_scheduler import MultiStepLR
from torch import nn
from PIL import Image
from utils import supervisor, tools, default_args, imagenet
import config


parser = argparse.ArgumentParser()
parser.add_argument('-dataset', type=str, required=False,
                    default=default_args.parser_default['dataset'],
                    choices=default_args.parser_choices['dataset'])
parser.add_argument('-poison_type', type=str,  required=False,
                    choices=default_args.parser_choices['poison_type'],
                    default=default_args.parser_default['poison_type'])
parser.add_argument('-poison_rate', type=float,  required=False,
                    choices=default_args.parser_choices['poison_rate'],
                    default=default_args.parser_default['poison_rate'])
parser.add_argument('-cover_rate', type=float,  required=False,
                    choices=default_args.parser_choices['cover_rate'],
                    default=default_args.parser_default['cover_rate'])
parser.add_argument('-alpha', type=float,  required=False,
                    default=default_args.parser_default['alpha'])
parser.add_argument('-test_alpha', type=float,  required=False, default=None)
parser.add_argument('-trigger', type=str, required=False, default=None)
parser.add_argument('-model_path', required=False, default=None)
parser.add_argument('-cleanser', type=str, required=False, default=None,
                    choices=default_args.parser_choices['cleanser'])
parser.add_argument('-defense', type=str, required=False, default=None,
                    choices=default_args.parser_choices['defense'])
parser.add_argument('-no_normalize', default=False, action='store_true')
parser.add_argument('-no_aug', default=False, action='store_true')
parser.add_argument('-devices', type=str, default='0')
parser.add_argument('-seed', type=int, required=False, default=default_args.seed)
args = parser.parse_args()

os.environ["CUDA_VISIBLE_DEVICES"] = "%s" % args.devices
if args.trigger is None:
    args.trigger = config.trigger_default[args.dataset][args.poison_type]


if args.dataset == 'imagenet':
    kwargs = {'num_workers': 32, 'pin_memory': True}
else:
    kwargs = {'num_workers': 4, 'pin_memory': True}

# tools.setup_seed(args.seed)

data_transform_aug, data_transform, trigger_transform, normalizer, denormalizer = supervisor.get_transforms(args)


if args.dataset == 'cifar10':
    num_classes = 10
    momentum = 0.9
    weight_decay = 1e-4
    epochs = 200
    milestones = torch.tensor([100, 150])
    learning_rate = 0.1
    batch_size = 128

elif args.dataset == 'mnist':
    num_classes = 10
    momentum = 0.9
    weight_decay = 1e-4
    epochs = 200
    milestones = torch.tensor([100, 150])
    learning_rate = 0.1
    batch_size = 128

elif args.dataset == 'cifar100':
    num_classes = 100
    raise NotImplementedError('<To Be Implemented> Dataset = %s' % args.dataset)

elif args.dataset == 'gtsrb':
    num_classes = 43
    momentum = 0.9
    weight_decay = 1e-4
    epochs = 100
    milestones = torch.tensor([40, 80])
    learning_rate = 0.1
    batch_size = 128

elif args.dataset == 'imagenet50':

    num_classes = 50
    arch = supervisor.get_arch(args)
    momentum = 0.9
    weight_decay = 1e-4
    epochs = 100
    milestones = torch.tensor([40, 80])
    learning_rate = 0.01
    batch_size = 16

elif args.dataset == 'imagenet100':

    num_classes = 100
    arch = supervisor.get_arch(args)
    momentum = 0.9
    weight_decay = 1e-4
    epochs = 100
    milestones = torch.tensor([40, 80])
    learning_rate = 0.01
    batch_size = 16

elif args.dataset == 'imagenette':
    num_classes = 10
    momentum = 0.9
    weight_decay = 1e-4
    epochs = 100
    milestones = torch.tensor([40, 80])
    learning_rate = 0.1
    batch_size = 128

elif args.dataset == 'tinyimagenet200':
    num_classes = 200
    arch = supervisor.get_arch(args)
    momentum = 0.9
    weight_decay = 1e-4
    epochs = 1000
    milestones = torch.tensor([40, 70])
    learning_rate = 0.01
    batch_size = 32

elif args.dataset == 'imagenet':
    num_classes = 1000
    momentum = 0.9
    weight_decay = 1e-4
    epochs = 90
    milestones = torch.tensor([30, 60])
    learning_rate = 0.1
    batch_size = 256

else:
    print('<Undefined Dataset> Dataset = %s' % args.dataset)
    raise NotImplementedError('<To Be Implemented> Dataset = %s' % args.dataset)


poison_set_dir = supervisor.get_poison_set_dir(args)
model_path = supervisor.get_model_dir(args, cleanse=(args.cleanser is not None), defense=(args.defense is not None))


arch = supervisor.get_arch(args)

import torchvision
# model = torchvision.models.resnet18(weights='IMAGENET1K_V1')
model = arch(num_classes=num_classes)
model.load_state_dict(torch.load(model_path))
model = nn.DataParallel(model)
model = model.cuda()
print("Evaluating model '{}'...".format(model_path))

# Set Up Test Set for Debug & Evaluation
if args.dataset != 'imagenet':
    test_set_dir = os.path.join('clean_set', args.dataset, 'test_split')
    test_set_img_dir = os.path.join(test_set_dir, 'data')
    test_set_label_path = os.path.join(test_set_dir, 'labels')
    test_set = tools.IMG_Dataset(data_dir=test_set_img_dir,
                                label_path=test_set_label_path, transforms=data_transform)
    test_set_loader = torch.utils.data.DataLoader(
        test_set,
        batch_size=batch_size, shuffle=False, worker_init_fn=tools.worker_init, **kwargs)
    
    # Poison Transform for Testing
    poison_transform = supervisor.get_poison_transform(poison_type=args.poison_type, dataset_name=args.dataset,
                                                    target_class=config.target_class[args.dataset], trigger_transform=data_transform,
                                                    is_normalized_input=True,
                                                    alpha=args.alpha if args.test_alpha is None else args.test_alpha,
                                                    trigger_name=args.trigger, args=args)

elif args.dataset == 'imagenet':
    test_set_dir = os.path.join(config.imagenet_dir, 'val')
    test_set = imagenet.imagenet_dataset(directory=test_set_dir, shift=False, data_transform=data_transform,
                 label_file=imagenet.test_set_labels, num_classes=1000)
    test_split_meta_dir = os.path.join('clean_set', args.dataset, 'test_split')
    test_indices = torch.load(os.path.join(test_split_meta_dir, 'test_indices'))

    test_set = torch.utils.data.Subset(test_set, test_indices)
    test_set_loader = torch.utils.data.DataLoader(
        test_set,
        batch_size=batch_size, shuffle=False, worker_init_fn=tools.worker_init, **kwargs)

    # Poison Transform for Testing
    poison_transform = supervisor.get_poison_transform(poison_type=args.poison_type, dataset_name=args.dataset,
                                                    target_class=config.target_class[args.dataset], trigger_transform=data_transform,
                                                    is_normalized_input=True,
                                                    alpha=args.alpha if args.test_alpha is None else args.test_alpha,
                                                    trigger_name=args.trigger, args=args)


if args.poison_type == 'TaCT' or args.poison_type == 'SleeperAgent':
    source_classes = [config.source_class]
else:
    source_classes = None

tools.test(model=model, test_loader=test_set_loader, poison_test=True, poison_transform=poison_transform, num_classes=num_classes, source_classes=source_classes, all_to_all=('all_to_all' in args.poison_type))