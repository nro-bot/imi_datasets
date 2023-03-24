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

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir",
        "-i",
        required=True,
        type=pathlib.Path,
        help="Directory containing input PDF files.",
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        required=True,
        type=pathlib.Path,
        help="Directory to output OCR'd text files to. The generated filenames will have the same structure as the input filenames.",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(exist_ok=True)
    for pdf_path in tqdm(list(args.input_dir.glob("*.pdf"))):
        text_path = output_dir / f"{pdf_path.stem}.txt"
        if text_path.exists():
            continue
        pdf_to_text(pdf_path, text_path)


if __name__ == "__main__":
    main()
