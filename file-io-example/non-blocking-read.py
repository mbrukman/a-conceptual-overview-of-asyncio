import os

fd = os.open(
    path="candy-database",
    flags=(
        os.O_RDWR |
        os.O_NONBLOCK
    )
)

# https://stackoverflow.com/questions/39948588/non-blocking-file-read

is_blocking = os.get_blocking(fd)

# n is the maximum number of bytes to read.
res = os.read(fd, 2**30)

print(f"is_blocking: {is_blocking}.")
print(f"fd: {fd}")
# print(f"read_val: {res}")

os.close(fd)