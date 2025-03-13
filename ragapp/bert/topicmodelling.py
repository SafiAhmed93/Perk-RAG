import os
import PyPDF2
import pandas as pd
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from typing import List, Dict, Any
import matplotlib.pyplot as plt
from tqdm import tqdm


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file using PyPDF2.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text content as a string
    """
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()

            return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""


def process_pdf_directory(directory_path: str) -> List[Dict[str, Any]]:
    """
    Process all PDF files in a directory with better error handling.
    """
    documents = []

    # Get all PDF files
    pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith(".pdf")]

    print(f"Processing {len(pdf_files)} PDF files...")

    # Process each PDF
    for pdf_file in tqdm(pdf_files):
        pdf_path = os.path.join(directory_path, pdf_file)
        text = extract_text_from_pdf(pdf_path)

        # Only add documents with meaningful content
        if text and len(text.strip()) > 20:  # Ensure there's at least some content
            documents.append({"filename": pdf_file, "content": text})
        else:
            print(f"Warning: Skipping {pdf_file} due to insufficient content")

    return documents


def run_topic_modeling(documents: List[Dict[str, Any]], num_topics: int = None):
    """
    Run BERTopic modeling with better error handling.
    """
    # Extract just the text content for modeling
    docs = [doc["content"] for doc in documents]

    # Ensure we have enough documents
    if len(docs) < 2:
        raise ValueError("Need at least 2 documents for topic modeling")

    # Basic preprocessing to ensure quality
    docs = [doc.strip() for doc in docs]

    # Print some diagnostics
    print(f"Number of documents: {len(docs)}")
    print(
        f"Avg document length (chars): {sum(len(doc) for doc in docs) / max(1, len(docs)):.1f}"
    )

    # Use more robust settings for small document collections
    topic_model = BERTopic(
        language="english",
        calculate_probabilities=True,
        verbose=True,
        min_topic_size=1,  # Allow singleton topics if needed
        nr_topics=num_topics,
        umap_model=None,  # Try using default UMAP settings
    )

    try:
        topics, probs = topic_model.fit_transform(docs)
        return topic_model, topics, documents
    except Exception as e:
        print(f"Error during topic modeling: {e}")

        # Try fallback approach with basic settings
        print("Attempting with fallback settings...")
        backup_model = BERTopic(verbose=True)
        topics, probs = backup_model.fit_transform(docs)
        return backup_model, topics, documents


def save_results(
    topic_model: BERTopic,
    topics: List[int],
    documents: List[Dict[str, Any]],
    output_dir: str,
):
    """
    Save the topic modeling results.

    Args:
        topic_model: Trained BERTopic model
        topics: Assigned topics for each document
        documents: List of document dictionaries
        output_dir: Directory to save results
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create a DataFrame with results
    results_df = pd.DataFrame(
        {
            "filename": [doc["filename"] for doc in documents],
            "topic": topics,
            "topic_name": [
                (
                    topic_model.get_topic_info().iloc[i]["Name"]
                    if i < len(topic_model.get_topic_info())
                    else "Unknown"
                )
                for i in range(len(topics))
            ],
        }
    )

    # Save results to CSV
    results_df.to_csv(os.path.join(output_dir, "topic_assignments.csv"), index=False)

    # Save topic information
    topic_info = topic_model.get_topic_info()
    topic_info.to_csv(os.path.join(output_dir, "topic_info.csv"), index=False)

    # Save visualizations
    topic_model.visualize_topics().write_html(
        os.path.join(output_dir, "topic_visualization.html")
    )
    topic_model.visualize_barchart(top_n_topics=10).write_html(
        os.path.join(output_dir, "top_topics_barchart.html")
    )

    # Generate and save document-topic map
    fig, ax = plt.subplots(figsize=(12, 10))
    topic_model.visualize_documents(
        docs=[doc["content"] for doc in documents], topics=topics, ax=ax
    )
    plt.savefig(os.path.join(output_dir, "document_topic_map.png"), bbox_inches="tight")

    print(f"Results saved to {output_dir}")


def main():
    # Configuration
    pdf_directory = "GIM-docs"  # Replace with your PDF directory
    output_directory = "berttopic_results"  # Output directory for results
    num_topics = None  # Set to a number or None for automatic

    # Process PDFs
    documents = process_pdf_directory(pdf_directory)
    print(f"Successfully processed {len(documents)} documents")

    if not documents:
        print("No documents to process. Exiting.")
        return

    # Run topic modeling
    topic_model, topics, documents = run_topic_modeling(documents, num_topics)

    # Print topic information
    topic_info = topic_model.get_topic_info()
    print("\nTopic Information:")
    print(topic_info.head(10))

    # Get top topics
    print("\nTop Topics:")
    for topic_id in topic_info.head(5)["Topic"]:
        if topic_id != -1:  # Skip outlier topic
            words = topic_model.get_topic(topic_id)
            print(f"Topic {topic_id}: {', '.join([word for word, _ in words[:5]])}")

    # Save results
    save_results(topic_model, topics, documents, output_directory)

    # Print document-topic mapping for first few documents
    print("\nSample Document-Topic Assignments:")
    for i, (doc, topic) in enumerate(zip(documents[:5], topics[:5])):
        print(f"Document: {doc['filename']}")
        print(f"Assigned Topic: {topic}")
        if topic != -1:
            words = topic_model.get_topic(topic)
            print(f"Topic words: {', '.join([word for word, _ in words[:5]])}")
        print("")
