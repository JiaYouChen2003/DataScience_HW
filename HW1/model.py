import cv2
import numpy as np
import os
import random
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.models import resnet50, ResNet50_Weights
import tqdm


class ResNet50_FC(nn.Module):
    def __init__(self, num_classes=1):
        super(ResNet50_FC, self).__init__()
        self.model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
        self.fc1 = nn.Linear(1000, 100)
        self.fc2 = nn.Linear(100, 10)
        self.fc3 = nn.Linear(10, num_classes)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = self.model(x)
        x = x.view(x.size(0), -1)
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)
        x = self.sigmoid(x)
        return x


def load_image_array(image_path):
    image = cv2.imread(image_path)
    try:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    except Exception:
        return None
    
    image = cv2.resize(image, (32, 32))
    
    return np.array(image)


def load_data(dataset_path):
    images = []
    labels = []
    classes = sorted(os.listdir(dataset_path))
    
    for class_name in classes:
        class_path = os.path.join(dataset_path, class_name)
        
        if not os.path.isdir(class_path):
            continue
        
        image_files = [f for f in os.listdir(class_path) if f.endswith(('.png'))]
        
        for i, image_file in enumerate(tqdm.tqdm(image_files)):
            image_path = os.path.join(class_path, image_file)
            
            image_array = load_image_array(image_path)
            if image_array is None:
                continue
            
            images.append(image_array)
            labels.append(classes.index(class_name))
    print(labels[-1])
    print(np.array(images).shape)
    print(np.array(labels).size)
    return np.array(images), np.array(labels)


def main():
    data_all, labels_all = load_data('./assets')
    
    model_plus_fc = ResNet50_FC()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model_plus_fc.parameters(), lr=0.001)
    
    num_epochs = 100
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)
    model_plus_fc.to(device)
    
    for epoch in range(num_epochs):
        inputs = None
        labels = []
        batch_count = 0
        for i, input in enumerate(tqdm.tqdm(data_all)):
            label = labels_all[i]
            if label == 0 and random.random() > 0.275:
                continue
            input = torch.from_numpy(input.astype(np.float32)).permute(2, 0, 1).unsqueeze(0).to(device)
            
            if inputs is None:
                inputs = input.to(device)
                labels.append(label)
            else:
                inputs = torch.cat((inputs, input), dim=0).to(device)
                labels.append(label)
            
            if batch_count % 32 == 31:
                labels = torch.tensor(labels).to(device)
                optimizer.zero_grad()
                outputs = model_plus_fc(inputs)
                loss = criterion(outputs, labels.float().view(-1, 1))
                loss.backward()
                optimizer.step()
                
                inputs = None
                labels = []
                with open('./loss/hw1_loss_random.txt', 'a') as file:
                    file.write(f'{epoch + 1} {i} Loss: {loss.item():.4f}' + '\n')
                batch_count = 0
            batch_count += 1
        
        print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')
        torch.save(model_plus_fc.state_dict(), './ckpt/ckpt_' + str(epoch) + '.pth')


if __name__ == "__main__":
    main()
