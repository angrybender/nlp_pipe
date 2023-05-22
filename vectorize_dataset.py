import tqdm
import argparse

from pipe_load_dataset.helper import get_dataset_files
from pipe_load_dataset.ADatasetFile import ADatasetFile
from pipe_text_processing.text_processing import create_items_from_text
from pipe_text_processing.text2vec import TextsVectorizer
from pipe_vengine.DatasetIndexer import DatasetIndexer

import logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('app')
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Put dataset into the vector engine')

# source params:
parser.add_argument('--dataset_path', type=str, required=True, help='Path to the raw dataset dir of file')
parser.add_argument('--dataset_type', choices=['ljson', 'csv'], required=True, help='Dataset format')
parser.add_argument('--dataset_text_field', type=str, help='Field in the JSON/CSV dataset, containing text')

# pre-processing params:
parser.add_argument('--split_by_paragraphs', choices=['Y'], default='', help='Split each items by LR')
parser.add_argument('--merge_short_paragraphs', choices=['Y'], default='', help='Recursive merge paragraphs less than AVG words')
parser.add_argument('--min_words_paragraphs', type=int, default=0, help='Filter paragraphs less than')
parser.add_argument('--overlap_paragraphs', type=int, default=0, help='Create "shingles" from paragraphs')

# vectorization params:
parser.add_argument('--vectorizer_model_path', type=str, required=True, help='Path to the vectorizer model')
parser.add_argument('--use_gpu', choices=['Y'], default='')

# vector engine params:
parser.add_argument('--vengine_host', type=str, required=True)
parser.add_argument('--vengine_port', type=str, default='6333')
parser.add_argument('--vengine_db_name', type=str, required=True)
parser.add_argument('--vengine_from_id', type=int, default=1, help='Start PK ID for upsert data')

args = parser.parse_args()
if args.dataset_type in ['ljson', 'csv'] and not args.dataset_text_field:
    raise Exception("Set value for --dataset_text_field")

logger.info("Collect dataset files and statistic...")
dataset_files = get_dataset_files(args.dataset_path)
if not dataset_files:
    raise Exception(f"Empty path: {args.dataset_path}")


assert args.overlap_paragraphs == 0 or args.overlap_paragraphs >= 2

total_items_count = 0
dataset_preloaded_files = []
for file_path in tqdm.tqdm(dataset_files):
    dataset_file = ADatasetFile.farbic(args.dataset_type)

    dataset_file.load(file_path, {
        'field': args.dataset_text_field,
    })
    total_items_count += dataset_file.get_count()
    dataset_preloaded_files.append(dataset_file)


logger.info("Load data...")
indexer = DatasetIndexer(args.vengine_host, args.vengine_port, args.vengine_db_name)
vectorization_model = TextsVectorizer(args.vectorizer_model_path, args.use_gpu)
progress_bar = tqdm.tqdm(total=total_items_count)
processed_cnt = 0
indexer_start_pk_id = args.vengine_from_id
for dataset_file in dataset_preloaded_files:
    for text in dataset_file.get_items():
        items = create_items_from_text(
            text, args.min_words_paragraphs,  args.split_by_paragraphs == 'Y', args.merge_short_paragraphs == 'Y'
        )

        if args.overlap_paragraphs > 0:
            shingles = []
            for i in range(args.overlap_paragraphs, len(items)+1):
                shingles.append(' '.join(items[i-args.overlap_paragraphs:i]))
            items = shingles

        if items:
            vectors = vectorization_model.fit_transform(items, False)
            indexer.index_data([{'text': item} for item in items], [v.tolist() for v in vectors], indexer_start_pk_id)
            indexer_start_pk_id += len(items)

        progress_bar.update()
        processed_cnt += 1

progress_bar.update(total_items_count - processed_cnt)
logger.info("Successful completed.")