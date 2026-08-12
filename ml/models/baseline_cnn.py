import torch
import torch.nn as nn
import torchvision.models as models

class BaselineResNet(nn.Module):
    """
    Baseline ResNet-50 for multi-label classification of intracranial hemorrhage.
    Expects a 3-channel input (Brain, Subdural, Bone windows).
    Outputs 6 logits.
    """
    def __init__(self, num_classes: int = 6, pretrained: bool = True):
        super(BaselineResNet, self).__init__()
        
        # Load the base ResNet-50 model
        weights = models.ResNet50_Weights.DEFAULT if pretrained else None
        self.base_model = models.resnet50(weights=weights)
        
        # We don't need to change the first conv layer because our input is 3-channel.
        # But we do need to replace the final fully connected layer.
        in_features = self.base_model.fc.in_features
        self.base_model.fc = nn.Linear(in_features, num_classes)
        
    def forward(self, x):
        # x shape: (Batch, 3, H, W)
        return self.base_model(x)

if __name__ == "__main__":
    # Quick shape check
    model = BaselineResNet()
    dummy_input = torch.randn(2, 3, 256, 256)
    out = model(dummy_input)
    print(f"Output shape: {out.shape}") # Expected: (2, 6)
