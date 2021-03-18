import wave
import os
import subprocess
import time
from PIL import Image


def encode_image(file_path, data, count): # file_path is the image that we want to encode and data is the message to be encoded !!
    img = Image.open(file_path)
    new_img = img.copy()
    new_img_data = list(new_img.getdata())

    new_img_data = [new_img_data[i][j] for i in range(len(new_img_data)) for j in range(len(new_img_data[i]))]
    data += (1000-len(data))*"#"
    data_bits = list(map(int, "".join([format(ord(i), "08b") for i in data])))

    for i in range(1000):
        new_img_data[i] = (new_img_data[i] & 254) | data_bits[i]

    new_img_datas = [tuple(new_img_data[i:i+3]) for i in range(0, len(new_img_data), 3)]

    w = new_img.size[0]
    (x, y) = (0, 0)

    for pixel in new_img_datas:
        new_img.putpixel((x, y), pixel)
        if(x == w - 1):
            x = 0
            y += 1
        else:
            x += 1

    new_path = f"static/download/clone_img{count}.png"
    new_img.save(new_path, 'PNG')
    return  new_path[7:]


def decode_image(file_path):
    img = Image.open(file_path)

    new_img_data = list(img.getdata())
    new_img_data = [new_img_data[i][j] for i in range(len(new_img_data)) for j in range(len(new_img_data[i]))]

    extracted = [new_img_data[i] & 1 for i in range(1000)]

    message = "".join(chr(int( "".join(map(str, extracted[i:i+8])), 2)) for i in range(0, len(extracted), 8))
    message = message.split("###")[0]

    return message


def convert_to_wav(path, count):
    cache = f'cache/temp{count}.wav'
    cmd = f"ffmpeg -i {path} -acodec pcm_u8 -ar 22050 {cache} -y"
    subprocess.run(cmd.split())
    return cache

def encode_audio(file_path, message, count):
    if file_path.endswith('mp3'):
        filepath = convert_to_wav(file_path, count)
        audio = wave.open(filepath, mode='rb')
    else:
        audio = wave.open(file_path, mode='rb')

    frame_bytes = bytearray(list(audio.readframes((audio.getnframes()))))

    message = message + int((len(frame_bytes)-(len(message)*8*8))/8) *'#'
    bits = list(map(int, "".join([bin(ord(i)).lstrip("0b").rjust(8, "0") for i in message])))
    for i, bit in enumerate(bits):
        frame_bytes[i] = (frame_bytes[i] & 254) | bit
    frame_modified = bytes(frame_bytes)

    path = f'static/download/decoded_audio{count}.wav'

    with wave.open(path, 'wb') as f:
        f.setparams(audio.getparams())
        f.writeframes(frame_modified)
        f.close()
    audio.close()
    return path[7:]


def decode_audio(file_path):
    if file_path.endswith('mp3'):
        filepath = convert_to_wav(file_path)
        audio = wave.open(filepath, mode='rb')
    else:
        audio = wave.open(file_path, mode='rb')

    frame_bytes = bytearray(list(audio.readframes(audio.getnframes())))

    extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]

    string = "".join(chr(int("".join(map(str, extracted[i:i+8])),2)) for i in range(0, len(extracted), 8))
    decoded = string.split('###')[0]
    audio.close()
    return decoded

if __name__ == "__main__":
    image_process()
