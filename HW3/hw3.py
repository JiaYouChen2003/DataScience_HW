from datasets import load_dataset
import evaluate
import nltk
import numpy as np
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
# from transformers import DataCollatorForSeq2Seq
# from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer
from tqdm import tqdm
import json

MODEL_NAME = "google/flan-t5-base"
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
prefix = "Please give headline for the following passage: "


def preprocess_func(examples, padding="max_length"):
    inputs = [prefix + doc for doc in examples["body"]]
    model_inputs = tokenizer(inputs, padding=padding, truncation=True)
    
    labels = tokenizer(text_target=examples["headline"], padding=padding, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def preprocess_test(examples, padding="max_length"):
    inputs = [prefix + doc for doc in examples["body"]]
    model_inputs = tokenizer(inputs, padding=padding, truncation=True)
    return model_inputs


def compute_metrics(eval_preds):
    nltk.download("punkt", quiet=True)
    metric = evaluate.load("rouge")
    
    preds, labels = eval_preds
    
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    
    decoded_preds = ["\n".join(nltk.sent_tokenize(pred.strip())) for pred in decoded_preds]
    decoded_labels = ["\n".join(nltk.sent_tokenize(label.strip())) for label in decoded_labels]
    
    result = metric.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
    
    return result


# dataset = load_dataset("json", data_files="content/drive/MyDrive/train.json")

# train_dataset = dataset["train"].train_test_split(test_size=0.2)['train']
# eval_dataset = dataset["train"].train_test_split(test_size=0.2)['test']

# train_tokenized_dataset = train_dataset.map(preprocess_func, batched=True)
# eval_tokenized_dataset = eval_dataset.map(preprocess_func, batched=True)
# print(train_tokenized_dataset)
# print(eval_tokenized_dataset)

# model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
# model.train()
# L_RATE = 3e-4
# BATCH_SIZE = 4
# PER_DEVICE_EVAL_BATCH = 1
# WEIGHT_DECAY = 0.01
# SAVE_TOTAL_LIM = 3
# NUM_EPOCHS = 2

# data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

# training_args = Seq2SeqTrainingArguments(
#     output_dir="content/drive/MyDrive",
#     evaluation_strategy="no",
#     learning_rate=L_RATE,
#     per_device_train_batch_size=BATCH_SIZE,
#     per_device_eval_batch_size=PER_DEVICE_EVAL_BATCH,
#     weight_decay=WEIGHT_DECAY,
#     save_total_limit=SAVE_TOTAL_LIM,
#     save_steps=2000,
#     num_train_epochs=NUM_EPOCHS,
#     predict_with_generate=True,
#     push_to_hub=False
# )

# trainer = Seq2SeqTrainer(
#     model=model,
#     args=training_args,
#     train_dataset=train_tokenized_dataset,
#     # eval_dataset=eval_tokenized_dataset,
#     tokenizer=tokenizer,
#     data_collator=data_collator,
#     compute_metrics=compute_metrics
# )


# def main():
#     trainer.train(resume_from_checkpoint=True)


model_name = "checkpoint-40000"
model_dir = f"./{model_name}"

tokenizer = T5Tokenizer.from_pretrained(model_dir)
model = T5ForConditionalGeneration.from_pretrained(model_dir)
model.eval()

test_dataset = load_dataset("json", data_files="./test.json", split="train")
test_tokenized_dataset = test_dataset.map(preprocess_test, batched=True)

test_tokenized_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask'])
dataloader = torch.utils.data.DataLoader(test_tokenized_dataset, batch_size=32)

all_predictions_decode = []

model.to('cuda')
for i, batch in enumerate(tqdm(dataloader)):
    input_ids = batch['input_ids'].to('cuda')
    attention_mask = batch['attention_mask'].to('cuda')
    
    outputs = model.generate(input_ids=input_ids, attention_mask=attention_mask, max_length=50)
    predictions = [tokenizer.decode(output, skip_special_tokens=True, clean_up_tokenization_spaces=True) for output in outputs]
    all_predictions_decode.append(predictions)

all_predictions_decode_flattened = [pred for preds in all_predictions_decode for pred in preds]

file_path = "./110511055.json"

with open(file_path, "w") as json_file:
    for prediction_decode in all_predictions_decode_flattened:
        json.dump({'headline': str(prediction_decode)}, json_file)
        json_file.write('\n')

print("Data saved to", file_path)
