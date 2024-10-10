
#Function for generating embedding
def get_embedding(input, model='text-embedding-3-small'):
    response = client.embeddings.create(
        input=input,
        model=model
    )
    return [x.embedding for x in response.data]

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# an embeddings model is initialized using the OpenAIEmbeddings class.
# The specified model is 'text-embedding-3-small'.
embeddings_model = OpenAIEmbeddings(model='text-embedding-3-small')

# This function is for calculating the tokens given the "message"
# ⚠️ This is simplified implementation that is good enough for a rough estimation

import tiktoken

def count_tokens(text):
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
    return len(encoding.encode(text))

def count_tokens_from_message_rough(messages):
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
    value = ' '.join([x.get('content') for x in messages])
    return len(encoding.encode(value))

from langchain_community.document_loaders import PyPDFLoader

filepath = './data/Kellog_Evaluation.pdf'
loader = PyPDFLoader(filepath)
pages = loader.load()
print(pages[0])


from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=500,
    chunk_overlap=50,
    length_function=count_tokens
)


splitted_documents = text_splitter.split_documents(pages)

print(len(splitted_documents))

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Load the document, split it into chunks, embed each chunk and load it into the vector store.
db = Chroma.from_documents(splitted_documents, embeddings_model, persist_directory="./chroma_db")
print(db._collection.count())

from langchain.prompts import PromptTemplate

# Build prompt
template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Always say "thanks for asking!" at the end of the answer.
{context}
Question: {question}
Helpful Answer:"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# Run chain
qa_chain = RetrievalQA.from_chain_type(
    ChatOpenAI(model='gpt-3.5-turbo'),
    retriever=db.as_retriever(),
    return_source_documents=True, # Make inspection of document possible
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
)

#qa_chain.invoke("What is a logic model?")

#from langchain.chains import SimpleQAWithContext

# Define the chain passing the context
#qa_chain = SimpleQAWithContext(
    #ChatOpenAI(model='gpt-3.5-turbo'),
    #retriever=db.as_retriever(),
    #prompt_template=QA_CHAIN_PROMPT
#)
