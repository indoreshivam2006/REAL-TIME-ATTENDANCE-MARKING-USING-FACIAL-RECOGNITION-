"""
FaceNet model implementation using PyTorch
Based on InceptionResnetV1 architecture for face recognition
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
import numpy as np
from PIL import Image
import os
import requests
from typing import Optional, Tuple


class InceptionResnetV1(nn.Module):
    """
    InceptionResnetV1 model for face recognition
    Pre-trained on VGGFace2 dataset
    Outputs 512-dimensional embeddings
    """
    
    def __init__(self, pretrained='vggface2', classify=False, num_classes=None):
        super(InceptionResnetV1, self).__init__()
        
        # Basic conv layers
        self.conv2d_1a = BasicConv2d(3, 32, kernel_size=3, stride=2)
        self.conv2d_2a = BasicConv2d(32, 32, kernel_size=3, stride=1)
        self.conv2d_2b = BasicConv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.maxpool_3a = nn.MaxPool2d(3, stride=2)
        self.conv2d_3b = BasicConv2d(64, 80, kernel_size=1, stride=1)
        self.conv2d_4a = BasicConv2d(80, 192, kernel_size=3, stride=1)
        self.conv2d_4b = BasicConv2d(192, 256, kernel_size=3, stride=2)
        
        # Inception-Resnet blocks
        self.repeat_1 = nn.Sequential(
            *[Block35(scale=0.17) for _ in range(5)]
        )
        self.mixed_6a = Mixed_6a()
        self.repeat_2 = nn.Sequential(
            *[Block17(scale=0.10) for _ in range(10)]
        )
        self.mixed_7a = Mixed_7a()
        self.repeat_3 = nn.Sequential(
            *[Block8(scale=0.20) for _ in range(5)]
        )
        self.block8 = Block8(noReLU=True)
        
        self.avgpool_1a = nn.AdaptiveAvgPool2d(1)
        self.dropout = nn.Dropout(0.6)
        self.last_linear = nn.Linear(1792, 512, bias=False)
        self.last_bn = nn.BatchNorm1d(512, eps=0.001, momentum=0.1, affine=True)
        
        if classify:
            self.logits = nn.Linear(512, num_classes)
        else:
            self.logits = None
            
        self.pretrained = pretrained
        
    def forward(self, x):
        """Forward pass"""
        x = self.conv2d_1a(x)
        x = self.conv2d_2a(x)
        x = self.conv2d_2b(x)
        x = self.maxpool_3a(x)
        x = self.conv2d_3b(x)
        x = self.conv2d_4a(x)
        x = self.conv2d_4b(x)
        x = self.repeat_1(x)
        x = self.mixed_6a(x)
        x = self.repeat_2(x)
        x = self.mixed_7a(x)
        x = self.repeat_3(x)
        x = self.block8(x)
        x = self.avgpool_1a(x)
        x = self.dropout(x)
        x = self.last_linear(x.view(x.shape[0], -1))
        x = self.last_bn(x)
        
        if self.logits is not None:
            x = self.logits(x)
        else:
            x = F.normalize(x, p=2, dim=1)
            
        return x


class BasicConv2d(nn.Module):
    def __init__(self, in_planes, out_planes, kernel_size, stride, padding=0):
        super().__init__()
        self.conv = nn.Conv2d(
            in_planes, out_planes,
            kernel_size=kernel_size, stride=stride,
            padding=padding, bias=False
        )
        self.bn = nn.BatchNorm2d(out_planes, eps=0.001, momentum=0.1, affine=True)
        self.relu = nn.ReLU(inplace=False)

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        return x


class Block35(nn.Module):
    def __init__(self, scale=1.0):
        super().__init__()
        self.scale = scale
        self.branch0 = BasicConv2d(256, 32, kernel_size=1, stride=1)
        self.branch1 = nn.Sequential(
            BasicConv2d(256, 32, kernel_size=1, stride=1),
            BasicConv2d(32, 32, kernel_size=3, stride=1, padding=1)
        )
        self.branch2 = nn.Sequential(
            BasicConv2d(256, 32, kernel_size=1, stride=1),
            BasicConv2d(32, 32, kernel_size=3, stride=1, padding=1),
            BasicConv2d(32, 32, kernel_size=3, stride=1, padding=1)
        )
        self.conv2d = nn.Conv2d(96, 256, kernel_size=1, stride=1)
        self.relu = nn.ReLU(inplace=False)

    def forward(self, x):
        x0 = self.branch0(x)
        x1 = self.branch1(x)
        x2 = self.branch2(x)
        out = torch.cat((x0, x1, x2), 1)
        out = self.conv2d(out)
        out = out * self.scale + x
        out = self.relu(out)
        return out


class Block17(nn.Module):
    def __init__(self, scale=1.0):
        super().__init__()
        self.scale = scale
        self.branch0 = BasicConv2d(896, 128, kernel_size=1, stride=1)
        self.branch1 = nn.Sequential(
            BasicConv2d(896, 128, kernel_size=1, stride=1),
            BasicConv2d(128, 128, kernel_size=(1,7), stride=1, padding=(0,3)),
            BasicConv2d(128, 128, kernel_size=(7,1), stride=1, padding=(3,0))
        )
        self.conv2d = nn.Conv2d(256, 896, kernel_size=1, stride=1)
        self.relu = nn.ReLU(inplace=False)

    def forward(self, x):
        x0 = self.branch0(x)
        x1 = self.branch1(x)
        out = torch.cat((x0, x1), 1)
        out = self.conv2d(out)
        out = out * self.scale + x
        out = self.relu(out)
        return out


class Block8(nn.Module):
    def __init__(self, scale=1.0, noReLU=False):
        super().__init__()
        self.scale = scale
        self.noReLU = noReLU
        self.branch0 = BasicConv2d(1792, 192, kernel_size=1, stride=1)
        self.branch1 = nn.Sequential(
            BasicConv2d(1792, 192, kernel_size=1, stride=1),
            BasicConv2d(192, 192, kernel_size=(1,3), stride=1, padding=(0,1)),
            BasicConv2d(192, 192, kernel_size=(3,1), stride=1, padding=(1,0))
        )
        self.conv2d = nn.Conv2d(384, 1792, kernel_size=1, stride=1)
        if not self.noReLU:
            self.relu = nn.ReLU(inplace=False)

    def forward(self, x):
        x0 = self.branch0(x)
        x1 = self.branch1(x)
        out = torch.cat((x0, x1), 1)
        out = self.conv2d(out)
        out = out * self.scale + x
        if not self.noReLU:
            out = self.relu(out)
        return out


class Mixed_6a(nn.Module):
    def __init__(self):
        super().__init__()
        self.branch0 = BasicConv2d(256, 384, kernel_size=3, stride=2)
        self.branch1 = nn.Sequential(
            BasicConv2d(256, 192, kernel_size=1, stride=1),
            BasicConv2d(192, 192, kernel_size=3, stride=1, padding=1),
            BasicConv2d(192, 256, kernel_size=3, stride=2)
        )
        self.branch2 = nn.MaxPool2d(3, stride=2)

    def forward(self, x):
        x0 = self.branch0(x)
        x1 = self.branch1(x)
        x2 = self.branch2(x)
        out = torch.cat((x0, x1, x2), 1)
        return out


class Mixed_7a(nn.Module):
    def __init__(self):
        super().__init__()
        self.branch0 = nn.Sequential(
            BasicConv2d(896, 256, kernel_size=1, stride=1),
            BasicConv2d(256, 384, kernel_size=3, stride=2)
        )
        self.branch1 = nn.Sequential(
            BasicConv2d(896, 256, kernel_size=1, stride=1),
            BasicConv2d(256, 256, kernel_size=3, stride=2)
        )
        self.branch2 = nn.Sequential(
            BasicConv2d(896, 256, kernel_size=1, stride=1),
            BasicConv2d(256, 256, kernel_size=3, stride=1, padding=1),
            BasicConv2d(256, 256, kernel_size=3, stride=2)
        )
        self.branch3 = nn.MaxPool2d(3, stride=2)

    def forward(self, x):
        x0 = self.branch0(x)
        x1 = self.branch1(x)
        x2 = self.branch2(x)
        x3 = self.branch3(x)
        out = torch.cat((x0, x1, x2, x3), 1)
        return out


def load_pretrained_weights(model, pretrained='vggface2'):
    """
    Load pre-trained weights for the model
    Downloads from GitHub if not present locally
    """
    weights_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'weights')
    os.makedirs(weights_dir, exist_ok=True)
    
    if pretrained == 'vggface2':
        weights_file = os.path.join(weights_dir, 'inception_resnet_v1_vggface2.pt')
        url = 'https://github.com/timesler/facenet-pytorch/releases/download/v2.2.9/20180402-114759-vggface2.pt'
    elif pretrained == 'casia-webface':
        weights_file = os.path.join(weights_dir, 'inception_resnet_v1_casia.pt')
        url = 'https://github.com/timesler/facenet-pytorch/releases/download/v2.2.9/20180408-102900-casia-webface.pt'
    else:
        return model
    
    # Download if not exists
    if not os.path.exists(weights_file):
        print(f"Downloading pre-trained weights from {url}...")
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            with open(weights_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Downloaded weights to {weights_file}")
        except Exception as e:
            print(f"⚠️ Failed to download weights: {e}")
            print("Model will use random initialization")
            return model
    
    # Load weights
    try:
        state_dict = torch.load(weights_file, map_location='cpu')
        
        # Remove logits layer if present (we don't need it for embeddings)
        if 'logits.weight' in state_dict:
            del state_dict['logits.weight']
        if 'logits.bias' in state_dict:
            del state_dict['logits.bias']
        
        model.load_state_dict(state_dict)
        print(f"✅ Loaded pre-trained weights from {weights_file}")
    except Exception as e:
        print(f"⚠️ Failed to load weights: {e}")
        print("Model will use random initialization")
    
    return model


def get_facenet_model(pretrained='vggface2', device='cpu'):
    """
    Get FaceNet model with pre-trained weights
    
    Args:
        pretrained: 'vggface2' or 'casia-webface' or None
        device: 'cpu' or 'cuda'
    
    Returns:
        model: InceptionResnetV1 model
    """
    model = InceptionResnetV1(pretrained=pretrained, classify=False)
    
    if pretrained:
        model = load_pretrained_weights(model, pretrained)
    
    model.eval()
    model.to(device)
    
    return model
