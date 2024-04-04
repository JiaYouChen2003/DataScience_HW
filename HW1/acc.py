from sklearn.metrics import accuracy_score
import numpy as np
import sys
import torch
import tqdm

import model


def main(checkpoint_num):
    model_acc = model.ResNet50_FC()
    checkpoint = torch.load('./ckpt/ckpt_' + checkpoint_num + '.pth')
    print(checkpoint.keys())
    model_acc.load_state_dict(checkpoint)
    model_acc.eval()
    print(model_acc)
    data_all, labels_all = model.load_data('./assets')
    labels_pred = []
    for i, input in enumerate(tqdm.tqdm(data_all)):
        input = torch.from_numpy(input.astype(np.float32)).permute(2, 0, 1).unsqueeze(0)
        label_pred = round(model_acc(input).item())
        labels_pred.append(label_pred)
    
    print(accuracy_score(labels_all, labels_pred))


if __name__ == "__main__":
    main(sys.argv[1])
