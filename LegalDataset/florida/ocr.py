import pathlib

import PIL
import pytesseract
import wand.image
import numpy as np
from tqdm import tqdm


def pdf_to_text(pdf_path, text_path):
    # Parsing of the PDF to even determine the page count takes a while, so we
    # generate the progress bar before we start opening the PDF in order to show
    # the current filename being processed even before we know the page count.
    # We then update the progress bar with the page count once the PDF is
    # parsed.
    with (
        tqdm(desc=pdf_path.name, leave=False) as progress,
        wand.image.Image(filename=pdf_path, resolution=300) as pdf,
    ):
        pages = list(pdf.sequence)
        progress.reset(len(pages))
        text_per_page = []
        for page in pages:
            raw = np.array(wand.image.Image(image=page))
            text_per_page.append(pytesseract.image_to_string(raw))
            progress.update()

        with text_path.open("w") as text_file:
            for text in text_per_page:
                text_file.write(text)
                text_file.write("\n\n")


def main():
    import argparse
    from concurrent.futures import ThreadPoolExecutor

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir",
        "-i",
        type=pathlib.Path,
        required=True,
        help="Directory containing input PDF files.",
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        type=pathlib.Path,
        required=True,
        help="Directory to output OCR'd text files to. The generated filenames will have the same structure as the input filenames.",
    )
    parser.add_argument(
        "--threads",
        "-t",
        type=int,
        default=8,
        help="Number of PDFs to process in parallel.",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(exist_ok=True)

    pdf_paths = list(args.input_dir.glob("*.pdf"))

    def process(pdf_path):
        text_path = output_dir / f"{pdf_path.stem}.txt"
        if text_path.exists():
            return
        pdf_to_text(pdf_path, text_path)

    with (
        ThreadPoolExecutor(max_workers=args.threads) as executor,
        tqdm(total=len(pdf_paths)) as progress,
    ):
        for _ in executor.map(process, pdf_paths):
            progress.update()


if __name__ == "__main__":
    main()
