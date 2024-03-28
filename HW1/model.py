import cv2
import numpy as np
import os
import random
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.models import resnet50, ResNet50_Weights
import tqdm


class ResNet50_FC(nn.Module):
    def __init__(self, num_classes=1):
        super(ResNet50_FC, self).__init__()
        self.fc = nn.Linear(1000, num_classes)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        x = self.sigmoid(x)
        return x


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
            image = cv2.imread(image_path)
            try:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            except Exception:
                continue
            
            image = cv2.resize(image, (32, 32))
            
            image_array = np.array(image)
            
            images.append(image_array)
            labels.append(classes.index(class_name))
    print(np.array(images).shape)
    print(np.array(labels).size)
    return np.array(images), np.array(labels)


if __name__ == "__main__":
    data, label = load_data('./assets')
    data_train, data_test, label_train, label_test = train_test_split(data, label, test_size=0.2, random_state=42)
    
    model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
    model_fc = ResNet50_FC()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    num_epochs = 100
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)
    model.to(device)
    
    for epoch in range(num_epochs):
        inputs = None
        labels = []
        batch_count = 0
        for i, input in enumerate(tqdm.tqdm(data_train)):
            label = label_train[i]
            if label == 0 and random.random() > 0.25:
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
                outputs = model(inputs)
                outputs = model_fc(outputs)
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
        torch.save(model.state_dict(), './ckpt/ckpt_' + str(epoch) + '.pth')
