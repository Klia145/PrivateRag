from pathlib import Path
import hashlib
import faiss
from unstructured.chunking.title import chunk_by_title
from unstructured.partition.auto import partition
from sentence_transformers import SentenceTransformer

def process_documents(
    input_folder: str = "DateBase",
    output_folder: str = "ThemessageDatebase",
    index_name: str = "knowledge.index",
    chunks_file: str = "chunks.txt"
):
    """改进后的文档处理函数
    
    Args:
        input_folder: 输入文件夹 (默认: DateBase)
        output_folder: 输出文件夹 (默认: ThemessageDatebase)
        index_name: 索引文件名 (默认: knowledge.index)
        chunks_file: 分块文本文件名 (默认: chunks.txt)
    """
    # 创建输出目录
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 记录已处理文件的哈希值
    processed_log = output_dir / "processed.log"
    processed = set()
    if processed_log.exists():
        processed = set(processed_log.read_text().splitlines())

    all_chunks = []
    for file in Path(input_folder).iterdir():
        # 计算文件哈希值
        file_hash = hashlib.md5(file.read_bytes()).hexdigest()
        if file_hash in processed:
            print(f"跳过已处理文件: {file.name}")
            continue
            
        try:
            elements = partition(filename=str(file))
            chunks = chunk_by_title(
                elements=elements,
                max_characters=1000,
                new_after_n_chars=800,
                overlap=200
            )
            all_chunks += [f"【{file.name}】{str(chunk)}" for chunk in chunks]
            processed.add(file_hash)
        except Exception as e:
            print(f"文件处理失败 {file.name}: {str(e)}")
            continue

    # 保存处理记录
    processed_log.write_text("\n".join(processed))

    # 生成编码和索引
    encoder = SentenceTransformer('./local_encoder')
    embeddings = encoder.encode(all_chunks)
    
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings.astype('float32'))
    
    # 保存到指定路径
    faiss.write_index(index, str(output_dir / index_name))
    (output_dir / chunks_file).write_text("\n".join(all_chunks), encoding='utf-8')

if __name__ == "__main__":
    # 示例调用 (参数均可选)
    process_documents()   # 自定义分块文件名
    