# -*- coding: utf-8 -*-
"""Ashish0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16rXoCWRohZNdEq068cvgm5Yy5Pl_kLHP
"""

!pip install pypdf

!pip install -q transformers einops accelerate langchain bitsandbytes

!pip install install sentence_transformers

!pip install llama_index

# Commented out IPython magic to ensure Python compatibility.
# %pip install llama-index-llms-huggingface

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import Settings

mkdir data

documents=SimpleDirectoryReader("/content/data").load_data()
documents

# setup prompts - specific to StableLM
from llama_index.core import PromptTemplate

system_prompt = """<|SYSTEM|># StableLM Tuned (Alpha version)
- StableLM is a helpful and harmless open-source AI language model developed by StabilityAI.
- StableLM is excited to be able to help the user, but will refuse to do anything that could be considered harmful to the user.
- StableLM is more than just an information source, StableLM is also able to write poetry, short stories, and make jokes.
- StableLM will refuse to participate in anything that could harm a human.
"""

# This will wrap the default prompts that are internal to llama-index
query_wrapper_prompt = PromptTemplate("<|USER|>{query_str}<|ASSISTANT|>")

!huggingface-cli login

import torch

llm = HuggingFaceLLM(
    context_window=4096,
    max_new_tokens=256,
    generate_kwargs={"temperature": 0.7, "do_sample": False},
    system_prompt=system_prompt,
    query_wrapper_prompt=query_wrapper_prompt,
    tokenizer_name="StabilityAI/stablelm-tuned-alpha-3b",
    model_name="StabilityAI/stablelm-tuned-alpha-3b",
    device_map="auto",
    # stopping_ids=[50278, 50279, 50277, 1, 0],
    # tokenizer_kwargs={"max_length": 4096},
    # uncomment this if using CUDA to reduce memory usage
    model_kwargs={"torch_dtype": torch.float16}
)

Settings.llm = llm
Settings.chunk_size = 1024

# Commented out IPython magic to ensure Python compatibility.
# %pip install llama-index-embeddings-langchain

from langchain.embeddings import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding

lc_embed_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

embed_model = LangchainEmbedding(lc_embed_model)

from llama_index.core import Settings

Settings.llm = llm
Settings.embed_model = embed_model
Settings.chunk_size = 512

index = VectorStoreIndex.from_documents(documents)

index

query_engine=index.as_query_engine()

!pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/rocm5.1.1

!python3 launch.py --precision full --no-half

query_engine = index.as_query_engine(streaming=True)

response_stream = query_engine.query("What are the lesson plane for Broadcast")

print(response_stream)