from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_all_code_files(code_files, max_chunks=100):
    """Reads code files and splits them into chunks using LangChain, up to a max chunk limit."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,      # Larger chunk for richer context
        chunk_overlap=150     # Slight overlap for continuity
    )

    chunked_code = {}
    total_chunks = 0

    for file_path in code_files:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        chunks = text_splitter.split_text(code)
        valid_chunks = []

        for chunk in chunks:
            if total_chunks >= max_chunks:
                break
            valid_chunks.append(chunk)
            total_chunks += 1

        if valid_chunks:
            chunked_code[file_path] = valid_chunks

        if total_chunks >= max_chunks:
            break

    return chunked_code
