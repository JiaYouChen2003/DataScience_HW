import json
import numpy as np
import sys
import torch

import model


def test_model(testImageJsonFilePath):
    model_acc = model.ResNet50_FC()
    checkpoint = torch.load('./ckpt/ckpt_99.pth')
    model_acc.load_state_dict(checkpoint)
    model_acc.eval()
    
    testImageJsonFile = open(testImageJsonFilePath, 'r', encoding='utf8')
    predictionList = []
    predictionImageJsonFile = open('image_predictions.json', 'w', encoding='utf8')
    data = json.load(testImageJsonFile)
    image_paths = data.get('image_paths', [])
    
    for image_path in image_paths:
        print(image_path)
        image_array = model.load_image_array(image_path)
        if image_array is None:
            print(image_path)
            predictionList.append(0)
            continue
        
        input = torch.from_numpy(image_array.astype(np.float32)).permute(2, 0, 1).unsqueeze(0)
        label_pred = round(model_acc(input).item())
        predictionList.append(label_pred)
        
    predictions = {
        "image_predictions": predictionList
    }
    json.dump(predictions, predictionImageJsonFile, indent=2)


if __name__ == '__main__':
    test_model(sys.argv[1])
