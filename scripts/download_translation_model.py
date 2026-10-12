from transformers import MarianMTModel, MarianTokenizer


MODEL_NAME = "Helsinki-NLP/opus-mt-tc-big-en-pt"


def main() -> None:
    MarianTokenizer.from_pretrained(MODEL_NAME)
    MarianMTModel.from_pretrained(MODEL_NAME)
    print(f"Cached translation model: {MODEL_NAME}")


if __name__ == "__main__":
    main()
