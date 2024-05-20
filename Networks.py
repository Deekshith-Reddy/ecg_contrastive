import torch
import torch.nn as nn

class BaselineConvNet(nn.Module):

    def __init__(self, classification=True, avg_embeddings=False):
        super(BaselineConvNet, self).__init__()
        self.classification = classification
        self.avg_embeddings = avg_embeddings
        self.conv1 = nn.Conv1d(in_channels=1, 
                               out_channels=16, 
                               kernel_size=7, 
                               stride=4)
        self.batch_norm1 = nn.BatchNorm1d(16)
        
        self.conv2 = nn.Conv1d(in_channels=16,
                               out_channels=32,
                               kernel_size=7,
                               stride=3)
        self.batch_norm2 = nn.BatchNorm1d(32)
        
        self.conv3 = nn.Conv1d(in_channels=32,
                               out_channels=64,
                               kernel_size=5,
                               stride=2)
        self.batch_norm3 = nn.BatchNorm1d(64)
        
        self.conv4 = nn.Conv1d(in_channels=64,
                               out_channels=64,
                               kernel_size=3,
                               stride=1)
        self.batch_norm4 = nn.BatchNorm1d(64)
        
        self.conv5 = nn.Conv1d(in_channels=64,
                               out_channels=128,
                               kernel_size=3,
                               stride=1)
        self.batch_norm5 = nn.BatchNorm1d(128)
        
        self.conv6 = nn.Conv1d(in_channels=128,
                               out_channels=256,
                               kernel_size=3,
                               stride=1)
        self.batch_norm6 = nn.BatchNorm1d(256)
        
        
        self.activation = nn.LeakyReLU(negative_slope=0.2)
        self.avg_pool = nn.AdaptiveAvgPool1d(1)
        self.finalLayer = nn.Sequential(
            nn.Linear(256, 1),
            nn.Sigmoid()
        ) if self.classification else nn.Sequential(
            nn.Linear(256, 256),
            nn.Linear(256, 128)

        )
    
    def forward(self, x):

        """ Forward Pass
        Args:
            x(torch.Tensor): Input tensor of shape (batch_size, 8, sequence_length)
        Returns:
            h(torch.Tensor): Output tensor of shape (batch_size, 1, 128) if avg_embeddings is True else (batch_size, 8, 128) and (batch_size, 1) if classification is True else (batch_size, 1) if classification
        """
        if self.classification:
            h = self.batch_norm1(self.activation(self.conv1(x)))
            h = self.batch_norm2(self.activation(self.conv2(h)))
            h = self.batch_norm3(self.activation(self.conv3(h)))
            h = self.batch_norm4(self.activation(self.conv4(h)))
            h = self.batch_norm5(self.activation(self.conv5(h)))
            h = self.batch_norm6(self.activation(self.conv6(h)))
            h = self.avg_pool(h)
            h = nn.Flatten()(h)
            h = self.finalLayer(h)
        else:
            batch_size = x.shape[0]
            nviews = x.shape[1]

            h = torch.empty(batch_size, nviews, 256, device=x.device)

            for i in range(nviews):
                x_i = x[:, i, :].unsqueeze(1)

                x_i = self.batch_norm1(self.activation(self.conv1(x_i)))
                x_i = self.batch_norm2(self.activation(self.conv2(x_i)))
                x_i = self.batch_norm3(self.activation(self.conv3(x_i)))
                x_i = self.batch_norm4(self.activation(self.conv4(x_i)))
                x_i = self.batch_norm5(self.activation(self.conv5(x_i)))
                x_i = self.batch_norm6(self.activation(self.conv6(x_i)))
                x_i = self.avg_pool(x_i)
                x_i = nn.Flatten()(x_i)

                h[:, i, :] = x_i


            if self.avg_embeddings:
                h = h.mean(dim=1, keepdim=True)

            h = self.finalLayer(h)

        return h
        
        