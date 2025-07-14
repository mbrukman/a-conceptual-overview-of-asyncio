import socket
import random


def gaussian_sum(n_samples: int) -> float:
    total = 0.0
    for _ in range(n_samples):
        total += random.gauss()
    
    return total

SERVER_ADDRESS = ("127.0.0.1", 8197)

if __name__ == "__main__":
    server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server.bind(SERVER_ADDRESS)

    max_queue_length = 1024
    server.listen(max_queue_length)
    print(f"Server is running and listening on: {SERVER_ADDRESS}.")

    while True:
        conn, _ = server.accept()
        print(f"Processing new connection: {conn}.")
        
        total = gaussian_sum(n_samples=int(1e7))
        conn.send(f"{total}".encode())
        print(f"Done. Closing connection: {conn}.\n")
        conn.close()