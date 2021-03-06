# Copyright 2020 Jérémie Donà, Jean-Yves Franceschi, Patrick Gallinari, Sylvain Lamprier

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse


DATASETS = ['mnist', 'chairs', 'taxibj', 'wave', 'wave_partial', 'sst']
ARCH_TYPES = ['dcgan', 'vgg', 'resnet', 'mlp', 'encoderSST']
DECODER_ARCH_TYPES = ['dcgan', 'vgg', 'mlp', 'decoderSST']
INITIALIZATIONS = ['orthogonal', 'kaiming', 'normal']
MIXING = ['concat', 'mul']


parser = argparse.ArgumentParser(prog="PDE-Driven Spatiotemporal Disentanglement (training)",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--xp_dir', type=str, metavar='DIR', required=True,
                    help='Directory where models will be saved.')
parser.add_argument('--chkpt_interval', type=int, metavar='STEPS', default=None,
                    help='If not None, save intermediate models every specified number of epochs.')

# Mixed-precision training
amp_p = parser.add_argument_group(title='Mixed-precision training',
                                  description='Choice of mixed-precision training library.')
amp_p = amp_p.add_mutually_exclusive_group()
amp_p.add_argument('--torch_amp', action='store_true',
                   help='Whether to use PyTorch\'s integrated mixed-precision training.')
amp_p.add_argument('--apex_amp', action='store_true',
                   help='Whether to use Nvidia\'s Apex mixed-precision training.')

distr_p = parser.add_argument_group(title='Distributed',
                                    description='Options for training on GPUs and distributed dataset loading.')
distr_p.add_argument('--device', type=int, metavar='DEVICE', default=None,
                     help='If not None, indicates the index of the GPU to use.')
distr_p.add_argument('--num_workers', type=int, metavar='NB', default=4,
                     help='Number of childs processes for data loading.')

model_p = parser.add_argument_group(title='Model Configuration',
                                    description='Model parameters.')
model_p.add_argument('--nt_cond', type=int, metavar='COND', default=5,
                     help='Number of conditioning observations')
model_p.add_argument('--nt_pred', type=int, metavar='PRED', default=10,
                     help='Number of observations to predict')
model_p.add_argument('--code_size_s', type=int, metavar='SIZE', default=128,
                     help='Number of dimensions in S (without skip connections).')
model_p.add_argument('--code_size_t', type=int, metavar='SIZE', default=20,
                     help='Number of dimensions in T.')
model_p.add_argument('--mixing', type=str, metavar='MIXING', default='concat', choices=MIXING,
                     help='Whether to concatenate or multiply S and T; in the latter case, their dimensions ' +
                          'be equal.')
model_p.add_argument('--architecture', type=str, metavar='ARCH', default='dcgan', choices=ARCH_TYPES,
                     help='Encoder and decoder architecture.')
model_p.add_argument('--decoder_architecture', type=str, metavar='ARCH', default=None, choices=DECODER_ARCH_TYPES,
                     help='If not None, overwrite the decoder architecture choice.')
model_p.add_argument('--skipco', action='store_true',
                     help='Whether to use skip connections from encoders to decoders.')
model_p.add_argument('--res_hidden_size', type=int, metavar='SIZE', default=512,
                     help='Hidden size of MLPs in the residual integrator.')
model_p.add_argument('--n_blocks', type=int, metavar='BLOCKS', default=1,
                     help='Number of resblocks in the residual integrator.')
model_p.add_argument('--enc_hidden_size', type=int, metavar='SIZE', default=64,
                     help='Hidden size of MLP encoders, or number of filters in convolutional encoders.')
model_p.add_argument('--dec_hidden_size', type=int, metavar='SIZE', default=64,
                     help='Hidden size of MLP decoders, or number of filters in convolutional decoders.')
model_p.add_argument('--enc_n_layers', type=int, metavar='LAYERS', default=3,
                     help='Number of layers in the MLP encoders and decoder.')
model_p.add_argument('--dec_n_layers', type=int, metavar='LAYERS', default=3,
                     help='Number of layers in the MLP encoders and decoder.')
model_p.add_argument('--init_encoder', type=str, metavar='INIT', default='normal', choices=INITIALIZATIONS,
                     help='Initialization type of the encoder and the decoder.')
model_p.add_argument('--gain_encoder', type=float, metavar='GAIN', default=0.02,
                     help='Initialization gain of the encoder and the decoder.')
model_p.add_argument('--init_resnet', type=str, metavar='INIT', default='orthogonal', choices=INITIALIZATIONS,
                     help='Initialization type of the linear layers of the MLP blocks in the integrator.')
model_p.add_argument('--gain_resnet', type=float, metavar='GAIN', default=1.41,
                     help='Initialization gain of the linear layers of the MLP blocks in the integrator.')
model_p.add_argument('--no_s', action='store_true',
                     help='If activated, desactivates the static component.')
model_p.add_argument('--offset', type=int, metavar='SIZE', default=5,
                     help='When non-zero and equal to the number of conditioning frames, reconstructs ' +
                          'conditioning observations, besides forecasting future observations.')

opt_p = parser.add_argument_group(title='Optimization Configuration',
                                  description='Loss and optimization parameters.')
opt_p.add_argument('--lamb_ae', type=float, metavar='LAMBDA', default=10,
                   help='Multiplier of the autoencoding loss.')
opt_p.add_argument('--lamb_s', type=float, metavar='LAMBDA', default=45,
                   help='Multiplier of the S invariance loss.')
opt_p.add_argument('--lamb_t', type=float, metavar='LAMBDA', default=0.001,
                   help='Multiplier of the T regularization loss.')
opt_p.add_argument('--lamb_pred', type=float, metavar='LAMBDA', default=45,
                   help='Multiplier of the prediction loss.')
opt_p.add_argument('--batch_size', type=int, metavar='SIZE', default=128,
                   help='Training batch size.')
opt_p.add_argument('--lr', type=float, metavar='LR', default=4e-4,
                   help='Learning rate of Adam optimizer.')
opt_p.add_argument('--beta1', type=float, metavar='BETA', default=0.9,
                   help='First-order decay parameter of the Adam optimizer.')
opt_p.add_argument('--beta2', type=float, metavar='BETA', default=0.99,
                   help='Second-order decay parameter of the Adam optimizer.')
opt_p.add_argument('--epochs', type=int, metavar='EPOCH', default=200,
                   help='Number of epochs to train on.')
opt_p.add_argument('--scheduler', action='store_true',
                   help='If activated, uses a scheluder dividing the learning rate at given epoch milestones.')
opt_p.add_argument('--scheduler_decay', type=float, metavar='DECAY', default=0.5,
                   help='Multiplier to learning rate applied at each scheduler milestone.')
opt_p.add_argument('--scheduler_milestones', type=int, nargs='+', metavar='EPOCHS', default=[300, 400, 500, 600, 700],
                   help='Scheduler epoch milestones where the learning rate is multiplied by the decay parameter.')

data_p = parser.add_argument_group(title='Dataset',
                                   description='Chosen dataset and dataset parameters.')
data_p.add_argument('--data', type=str, metavar='DATASET', default='mnist', choices=DATASETS,
                    help='Dataset choice.')
data_p.add_argument('--data_dir', type=str, metavar='DIR', required=True,
                    help='Data directory.')
parser.add_argument('--downsample', type=int, metavar='DOWNSAMPLE', default=2,
                    help='Set the sampling rate for the WaveEq dataset.')
parser.add_argument('--n_wave_points', type=int, metavar='NUMBER', default=100,
                    help='Number of random pixels to select for partial WaveEq (WaveEq-100).')
parser.add_argument('--zones', type=int, metavar='ZONES', default=list(range(1, 30)), nargs='+',
                    help='SST zones to train on.')
parser.add_argument('--n_object', type=int, metavar='NUMBER', default=2,
                    help='Number of digits in the Moving MNIST data.')
