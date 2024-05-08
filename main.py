import secrets
import string
import sys
from pathlib import Path

from gtts import gTTS
from more_itertools import batched
from pydub import AudioSegment

ALPHABET = string.digits + string.ascii_letters + string.punctuation + " "
TEMP_FILE = "tmp.mp3"
GROUP_LEN = 5


def read_input() -> str:
    message = input("Your message:\n")

    if any(map(lambda c: c not in ALPHABET, message)):
        raise ValueError("Invalid symbols in message")
    return message


def synthesize_group(group: str) -> AudioSegment:
    if len(group) != GROUP_LEN:
        additional = GROUP_LEN - len(group)
        group += "0" * additional

    gap = AudioSegment.silent(duration=400)
    segment = gap

    for digit in group:
        tts = gTTS(digit)
        tts.save(TEMP_FILE)
        segment += AudioSegment.from_mp3(TEMP_FILE)

    return segment


def generate_message(groups: list[str]) -> AudioSegment:
    voice_message = AudioSegment.silent(duration=50)
    gap = AudioSegment.silent(duration=1000)

    for i, group in enumerate(groups):
        segment = synthesize_group(group)
        voice_message += segment
        if i != len(groups) - 1:
            voice_message += gap

    return voice_message


def main():
    try:
        message = read_input()

        key = [secrets.randbelow(len(ALPHABET)) for _ in range(len(message))]
        message_to_encrypt = [ALPHABET.index(c) for c in message]
        cypher = [(c + k) % len(ALPHABET) for c, k in zip(message_to_encrypt, key)]

        groups = list(
            map(
                lambda x: "".join(x),
                batched("".join(map(lambda x: ("" if x > 9 else "0") + str(x), cypher)), GROUP_LEN),
            )
        )

        with open("key.txt", "w") as key_file:
            key_file.write("".join(map(str, key)))

        voice_message = generate_message(groups)
        voice_message.export("message.mp3", format="mp3")
    except ValueError as e:
        print(e, file=sys.stderr)
    finally:
        p = Path(TEMP_FILE)
        p.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
