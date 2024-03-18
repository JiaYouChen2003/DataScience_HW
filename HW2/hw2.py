import pandas as pd
import promptbench as pb
import tqdm


file_path = './mmlu_sample.csv'
data = pd.read_csv(file_path)
data_list = data.to_dict(orient='records')

model = pb.LLMModel(model='google/flan-t5-large', max_new_tokens=10, temperature=0.0001)

prompts = pb.Prompt(["Answer the following multiple choices question related to {task}, think step by step, but only provide answer with A, B, C, D: {input}\n\
                     A: {A}\n\
                     B: {B}\n\
                     C: {C}\n\
                     D: {D}"
                     ])


def extractSubstringForResponse(string, start_index=4):
    print(string)
    string = string.replace(" ", "")
    return string[start_index + 1:start_index + 2]


def projFunc(pred):
    mapping = {
        'A': 0,
        'B': 1,
        'C': 2,
        'D': 3
    }
    return mapping.get(pred, -1)


for prompt in prompts:
    preds = []
    labels = []
    for data in tqdm.tqdm(data_list):
        input_text = pb.InputProcess.basic_format(prompt, data)
        label = data['target']
        
        raw_pred = extractSubstringForResponse(model(input_text))
        pred = projFunc(raw_pred)
        label = projFunc(label)
        print(pred, label)
        
        preds.append(pred)
        labels.append(label)
    
    # evaluate
    score = pb.Eval.compute_cls_accuracy(preds, labels)
    print(f"{score:.3f}, {prompt}")
