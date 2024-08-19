from asyncio import sleep
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# from langchain_community.document_loaders import WebBaseLoader
# from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.document_loaders import PyPDFDirectoryLoader
# from langchain_community.document_loaders import PyMuPDFLoader
from langchain_chroma import Chroma
from langchain import hub
import bs4
from langchain_google_vertexai import ChatVertexAI
import os


async def return_query(query: str, session_id: str):
    try:
        os.environ["GOOGLE_API_KEY"] = "AIzaSyCbwIgRs_eiiwOE5e0VOfv8tEOEcTtcMMM"
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get(
        #     "GOOGLE_APPLICATION_CREDENTIALS")
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = "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"

        llm = ChatVertexAI(project="forward-pad-429200-d1",
                           model="gemini-1.5-flash")

        # Load, chunk and index the contents of the blog.
        # loader = DirectoryLoader(
        #     f"uploads/{session_id}/", glob="**/*", silent_errors=True)

        loader = PyPDFLoader(f"uploads/{session_id}/mohd_shahbaz.pdf")

        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        vectorstore = Chroma.from_documents(
            documents=splits, embedding=VertexAIEmbeddings(model_name="textembedding-gecko@003"))

        # Retrieve and generate using the relevant snippets of the blog.
        retriever = vectorstore.as_retriever()
        prompt = hub.pull("rlm/rag-prompt")

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        async for chunk in rag_chain.astream(query):
            yield f"data: {chunk}\n\n"
    except:
        print("error!")


# return_query("What is Task Decomposition?", "err")


async def waypoints_generator():
    waypoints = open('waypoints.json')
    waypoints = json.load(waypoints)
    for waypoint in waypoints[0: 10]:
        data = json.dumps(waypoint)
        yield f"event: locationUpdate\ndata: {data}\n\n"
        await sleep(1)
