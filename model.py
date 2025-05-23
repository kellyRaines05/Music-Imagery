import torch
import torch.nn as nn
import torch.nn.functional as F

class SoundToImage(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(4, 128),
            nn.ReLU(),
            nn.Linear(128, 8*8*64),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(32, 3, 4, stride=2, padding=1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        x = self.fc(x)
        x = x.view(-1, 64, 8, 8)
        x = self.decoder(x)
        return x

class UNet(nn.Module):
    def __init__(self):
        super(UNet, self).__init__()
        self.input_conv = nn.Conv2d(3, 64, kernel_size=9, padding=4)
        
        self.res_block = nn.Sequential(
            *[self._residual_block() for _ in range(5)]
        )
        
        self.mid_conv = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        
        # Multiple upsampling stages
        self.upsample1 = nn.Sequential(
            nn.Conv2d(64, 256, kernel_size=3, padding=1),
            nn.PixelShuffle(2),
            nn.ReLU()
        )
        
        self.upsample2 = nn.Sequential(
            nn.Conv2d(64, 256, kernel_size=3, padding=1),
            nn.PixelShuffle(2),
            nn.ReLU()
        )
        
        self.upsample3 = nn.Sequential(
            nn.Conv2d(64, 256, kernel_size=3, padding=1),
            nn.PixelShuffle(2),
            nn.ReLU()
        )
        
        self.output_conv = nn.Conv2d(64, 3, kernel_size=9, padding=4)

    def _residual_block(self):
        block = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.PReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64)
        )
        return block

    def forward(self, x):
        out1 = self.input_conv(x)
        out = self.res_block(out1)
        out = self.mid_conv(out)
        out = out + out1

        out = self.upsample1(out)
        out = self.upsample2(out)
        out = self.upsample3(out)

        out = F.interpolate(out, size=(128, 128), mode='bilinear', align_corners=False)

        out = self.output_conv(out)

        return out