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

def lsTreeCommand(hash):

    file_path = f"{GIT_OBJECTS}/{hash[:2]}/{hash[2:]}"
    with open(file_path, "rb") as f:
        data = f.read()
        data = zlib.decompress(data)
        data = data.split(b"\x00")
        files = []
        for i in range(1,len(data)-1):
            filename = data[i].split(b" ")[-1]
            files.append(filename)
        for file in files:
            print(file.decode())

def writeTree():
    blob_code = b"10064"
    dir_code = b"40000"
    content = []
    files = os.listdir()
    files.sort()

    for obj in files:
        if str(obj) == ".git":
            continue
        h = hashlib.sha1()
        code = dir_code if os.path.isdir(obj) else blob_code
        h.update(str(obj).encode())
        hash = h.digest()
        content.append(code + b" " + str(obj).encode() + b"\0" + hash)

    content = b"".join(content)
    content = b"tree " + str(len(content)).encode() + b"\0" + content
    h = hashlib.sha1()
    h.update(content)
    content_hash = h.hexdigest()

    os.makedirs(f"{GIT_OBJECTS}/{content_hash[:2]}", exist_ok=True)
    with open(f"{GIT_OBJECTS}/{content_hash[:2]}/{content_hash[2:]}","wb") as out:
        out.write(zlib.compress(content))
    print(content_hash)



def main():
    command = sys.argv[1]
    # print(sys.argv)
    if command == "init":
        initialize()
        print("Initialized git directory")
    elif command == "cat-file" and len(sys.argv) == 4:
        catCommand(sys.argv[3])
    elif command == "hash-object" and len(sys.argv) == 4:
        hashCommand(sys.argv[3])
    elif command == "ls-tree" and len(sys.argv)==4:
        lsTreeCommand(sys.argv[3])
    elif command == "write-tree":
        writeTree()
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
