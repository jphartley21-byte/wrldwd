"""Where the original's lines live (rule 4: OUTSIDE the project, never copied in). One resolver for every toolkit
module, matching ww/config.PRIVATE_ORIGINAL. The toolkit used to hard-code ~/Documents/Worldwide_private while ww used
~/Documents/WORLDWIDE_PRIVATE: the same folder on Windows, two different folders on Linux/macOS (found 14 Oct 2026)."""
import os


def original_path():
    env = os.environ.get("WW_PRIVATE_ORIGINAL")
    if env:
        return env
    docs = os.path.join(os.path.expanduser("~"), "Documents")
    for folder in ("Worldwide_private", "WORLDWIDE_PRIVATE"):
        p = os.path.join(docs, folder, "original_lines.txt")
        if os.path.exists(p):
            return p
    return os.path.join(docs, "Worldwide_private", "original_lines.txt")
