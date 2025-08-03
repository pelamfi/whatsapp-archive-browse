import argparse

def main():
    parser = argparse.ArgumentParser(description="Whatsapp Archive Browseability Generator")
    parser.add_argument("input_folder", help="Input folder containing WhatsApp archives")
    parser.add_argument("output_folder", help="Output folder for generated HTML")
    parser.add_argument("--locale", default="FI", help="Locale specification (default: FI)")

    args = parser.parse_args()

    print("Input folder:", args.input_folder)
    print("Output folder:", args.output_folder)
    print("Locale:", args.locale)

if __name__ == "__main__":
    main()
