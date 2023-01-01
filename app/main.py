import sys
import os
import zlib
import hashlib


GIT_ROOT = ".git/"
GIT_OBJECTS = ".git/objects/"
GIT_REFS = ".git/refs/"
GIT_HEAD = ".git/HEAD"

def initialize():
    os.mkdir(GIT_ROOT)
    os.mkdir(GIT_OBJECTS)
    os.mkdir(GIT_REFS)
    with open(GIT_HEAD, "w") as f:
            f.write("ref: refs/heads/master\n")


def catCommand(hash):
    dir = hash[:2]
    fileName = hash[2:]
    with open(f"{GIT_OBJECTS}/{dir}/{fileName}","rb") as f:
        data = f.read()
        data = zlib.decompress(data)
        data = data.split(b"\x00",maxsplit=1)[1]
        print(data.decode(), end="")

def hashCommand(filepath):
    with open(filepath,"rb") as f:
        content = f.read()
        content = f"blob {len(content)}".encode() + b"\0" + content

        sha = hashlib.sha1(content).hexdigest()
        sha_prefix = sha[:2]
        sha_suffix = sha[2:]
        
        compressed_content = zlib.compress(content)

        os.mkdir(f"{GIT_OBJECTS}/{sha_prefix}")
        with open(f"{GIT_OBJECTS}/{sha_prefix}/{sha_suffix}","wb") as f:
            f.write(compressed_content)
        print(sha,end = "")


def main():
    command = sys.argv[1]
    if command == "init":
        initialize()
        print("Initialized git directory")
    elif command == "cat-file" and len(sys.argv) == 4:
        catCommand(sys.argv[3])
    elif command == "hash-object" and len(sys.argv) == 4:
        hashCommand(sys.argv[3])

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
