"""CLI entry point for running without Streamlit."""
import argparse
from core.pipeline import process

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    parser.add_argument("--language", choices=["Hindi","Kannada","Tamil"], default="Hindi")
    parser.add_argument("--engine", choices=["demo","indicxlit"], default="demo")
    args = parser.parse_args()
    result = process(args.text, args.language,
                     engine="AI4Bharat IndicXlit" if args.engine == "indicxlit" else "Offline demo lexicon")
    print("Native:", result.native)
    print("Polished:", result.polished)
    print("Provider:", result.provider)
    for warning in result.warnings:
        print("Warning:", warning)
