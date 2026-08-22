import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from app.llm.providers.huggingface import HuggingFaceProvider, CLASSIFY_PROMPT


async def main():
    provider = HuggingFaceProvider()
    for desc in [
        "PSP gateway responded with an unexpected error code",
        "3DS authentication step could not be completed",
        "Txn declined by issuer bank, code 05",
    ]:
        prompt = CLASSIFY_PROMPT.format(error_code="GATEWAY_ERROR", error_description=desc)
        raw = await provider._generate(prompt, temperature=0.0)
        print(f"--- {desc} ---")
        print(raw)
        print()


if __name__ == "__main__":
    asyncio.run(main())