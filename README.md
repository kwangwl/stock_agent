![Github_Logo](.//static/Picture1.png)  
Building a Stock Analysis Application Using Amazon Bedrock Agent

###
### Architecture

![Picture2](.//static/Picture2.png)

1. Streamlit: Provides a user interface to visually display stock analysis results.
2. Amazon Bedrock Agent: Integrates with various AI models to analyze stock data, processing data through Knowledge Base and Action Group.
3. Amazon OpenSearch: A vector database responsible for Amazon Bedrock's RAG (Retrieval-Augmented Generation) functionality, providing fast and efficient search capabilities in conjunction with the Knowledge Base.
4. AWS Lambda: Executes functions necessary for processing and analyzing stock data.
5. Yahoo Finance: Retrieves stock data from Yahoo Finance for analysis.
