desired_file_size_num_bytes = 2 * 1024 * 1024 * 1024

with open("candy-database", "w") as fh:
    
    roughly_32_bytes_of_candy = "Mars-Aero-Snickers-Twix-Reeses \n"
    num_32_byte_chunks = int(desired_file_size_num_bytes / 32)
    
    for _ in range(num_32_byte_chunks):
        fh.write(roughly_32_bytes_of_candy)

