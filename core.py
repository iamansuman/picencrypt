import os
from shutil import rmtree
from math import isqrt
from PIL import Image
from tempfile import gettempdir
from datetime import datetime, timezone
import pyzipper
import time
# from random_word import RandomWords
# from json import load, dump

StatusMessages: list = ["OK", "Wrong Password", "Unexpected Error"]

def get_absolute_temp_path(fileName:str): return os.path.join(gettempdir(), 'picencrypt', fileName) 

def string_to_binary(string: str): return str().join(format(ord(c), '08b') for c in string)

def binary_to_string(binary_string: str) -> str:
    if len(binary_string) % 8 != 0: raise ValueError("Input binary string must be a multiple of 8 characters")
    chunks = [binary_string[i : i+8] for i in range(0, len(binary_string), 8)]
    char_codes = [int(chunk, 2) for chunk in chunks]
    return str().join(chr(code) for code in char_codes)

def byte_to_binary(byte_object):
    binary_list = []
    for byte in byte_object:
        ascii_code = ord(chr(byte))
        binary_string = format(ascii_code, 'b')
        binary_string = binary_string.zfill(8)
        binary_list.append(binary_string)
    return str().join(binary_list)

def binary_to_byte(binary_string):
  if len(binary_string) % 8 != 0: raise ValueError("Binary-like string length must be a multiple of 8")
  byte_list = []
  for i in range(0, len(binary_string), 8):
    byte_chunk = binary_string[i:i+8]
    decimal_value = int(byte_chunk, 2)
    character = chr(decimal_value)
    byte_list.append(bytes([ord(character)]))
  return b''.join(byte_list)

def largest_factors(number:int):
    sqrt_n: int = isqrt(number)
    for i in range(sqrt_n, 0, -1):
        if number % i == 0:
            fac1: int = number // i
            fac2: int = i
            return fac1, fac2

def pack_to_zip(keys:list, fileName:str, dirOfFiles:str, endFilePath:str):
    pk, sk = keys
    binaryKey = int(string_to_binary(pk)) & int(string_to_binary(sk))

    with pyzipper.AESZipFile(os.path.join(endFilePath, f"Encrypted-{fileName.rsplit('.', 1)[0]}.zip"), 'w', compression=pyzipper.ZIP_DEFLATED, compresslevel=9, encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(str(binaryKey).encode('utf-8'))
        for entry in os.scandir(dirOfFiles):
            if entry.is_file():
                zf.write(get_absolute_temp_path(entry.name), entry.name)
    
    rmtree(get_absolute_temp_path(''), onerror=None, ignore_errors=True)

def unpack_from_zip(keys:list, filePath:str, tempFolderPath:str):
    pk, sk = keys
    binaryKey = int(string_to_binary(pk)) & int(string_to_binary(sk))
    zf = pyzipper.AESZipFile(filePath, 'r')
    zf.setpassword(str(binaryKey).encode('utf-8'))
    try:
        zf.extractall(tempFolderPath)
        return True
    except RuntimeError: return False

def pack_to_mp4(keys: list, fileName: str, endFilePath: str): pass

def unpack_from_mp4(): pass

def Encrypt(payload):
    fileName: str = payload[0]
    filePath: str = payload[1]
    endFilePath = payload[2]
    endFileType: str = payload[3]
    pk, sk = payload[4]

    temp_file_dir = get_absolute_temp_path('')
    if os.path.isdir(temp_file_dir): rmtree(temp_file_dir, onerror=None, ignore_errors=True)
    os.mkdir(temp_file_dir)

    file = open(filePath, 'rb')
    dataList: list = file.readlines()
    file.close()

    dataListBin = []

    for i in range(len(dataList)):
        data = dataList[i]
        binary_data = byte_to_binary(data)
        dataListBin.append(binary_data)

    #Image size -> 1920 x 1080 (WxH)

    totalBinDataLen = sum(len(i) for i in dataListBin)
    
    noOfFrames = totalBinDataLen // 2073600 #1920x1080
    pixelsInLastFrame = totalBinDataLen % 2073600

    fileIndex = 0
    img = Image.new('1', (1920, 1080), 0)
    x, y = 0, 0

    for data in dataListBin:
        #Do encryption here on `data`
        for val in data:
            if y >= 1080:
                img.save(get_absolute_temp_path(f'{fileIndex}.png'), 'png')
                img.close()
                fileIndex += 1
                img = Image.new('1', (1920, 1080), 0)
                x, y = 0, 0
            
            if val == '1': img.putpixel((x, y), 1)
            x += 1
            
            if x >= 1920:
                x = 0
                y += 1
    

    img.save(get_absolute_temp_path(f'{fileIndex}.png'), 'png')
    
    if pixelsInLastFrame != (y*1920)+x:
        raise Exception("Mismatch in pixels while constructing last main data frame")
        exit()

    # metadata: dict = {
    #     totalFragments: len(dataList),
    #     fileName: fileName,
    #     timeOfEncryptionInUTC: datetime.now(tz=timezone.utc),
    #     encryptionTestPhrase: RandomWords().get_random_word() + RandomWords().get_random_word()
    # }

    metadata: str = f"fileName:{fileName};totalFragments:{noOfFrames+1};totalBits:{totalBinDataLen};pixelsInLastFrame:{pixelsInLastFrame};timeOfEncryptionInUTC:{datetime.now(tz=timezone.utc)}"
    metadataBin = str().join(format(ord(c), '08b') for c in metadata)
    
    with Image.new('1', largest_factors(len(metadataBin)), 0) as img:
        width, height = img.size
        x, y = 0, 0
        for bi in metadataBin:
            if bi == '1': img.putpixel((x, y), 1)
            x += 1
            if x >= width:
                x = 0
                y += 1
        
        img.save(get_absolute_temp_path('data.png'), 'png')
    
    if endFileType == 'mp4': pack_to_mp4(payload[4], fileName, endFilePath)
    else: pack_to_zip(payload[4], fileName, temp_file_dir, endFilePath)

    return StatusMessages[0]

def Decrypt(payload):
    fileName: str = payload[0]
    fileType: str = fileName.rsplit('.', 1)[1]
    filePath: str = payload[1]
    endFilePath = payload[2]
    pk, sk = payload[3]

    temp_file_dir = get_absolute_temp_path('')
    if os.path.isdir(temp_file_dir): rmtree(temp_file_dir, onerror=None, ignore_errors=True)
    os.mkdir(temp_file_dir)

    UnpackStatus = False
    if fileType == 'mp4': UnpackStatus = unpack_from_mp4()
    else: UnpackStatus = unpack_from_zip(payload[3], filePath, temp_file_dir)
    UnpackStatus = unpack_from_zip(payload[3], filePath, temp_file_dir)
    if not UnpackStatus: return StatusMessages[1]

    #Get metadata from data frame
    img = Image.open(r"C:\Users\ansum\AppData\Local\Temp\picencrypt\data.png")
    width, height = img.size
    bin_metadata = str()
    for y in range(height):
        for x in range(width):
            bin_metadata += '1' if img.getpixel((x, y)) > 128 else '0'

    l1 = binary_to_string(bin_metadata).split(';')
    keys, vals = [], []
    for l2 in l1:
        keys.append(l2.split(':')[0])
        vals.append(l2.split(':')[1])

    if 'fileName' not in keys or 'totalFragments' not in keys or 'totalBits' not in keys or 'pixelsInLastFrame' not in keys: return StatusMessages[1]

    metadata = dict(zip(keys, vals))
    
    #deserialising image
    dataList = []

    for i in range(int(metadata['totalFragments'])-1):
        img = Image.open(get_absolute_temp_path(f'{i}.png'))        
        bin_data = str()
        for y in range(1080):
            for x in range(1920):
                bin_data += '1' if img.getpixel((x, y)) > 128 else '0'

        dataList.append(binary_to_byte(bin_data))

    img = Image.open(get_absolute_temp_path(f'{int(metadata['totalFragments'])-1}.png'))
    x, y = 0, 0
    bin_data = str()
    for _ in range(int(metadata['pixelsInLastFrame'])):
        bin_data += '1' if img.getpixel((x, y)) > 128 else '0'
        x += 1
        if x >= 1920:
            y += 1
            x = 0
    img.close()
    dataList.append(binary_to_byte(bin_data))
    
    #Writing bytes to file
    with open(os.path.join(endFilePath, metadata['fileName']), 'wb') as f: f.writelines(dataList)

    return StatusMessages[0]


# if __name__ == "__main__":      #For Testing only; Remove in builds
#     t1 = time.perf_counter()
#     # Encrypt(['Sugar.mp3', r"C:\Users\ansum\Music\My Music\Sugar.mp3", r"C:\Users\ansum\Desktop", 'zip', ['1qaz0plm', '152634']])
#     Decrypt(['Encrypted-Sugar.zip', r"C:\Users\ansum\Desktop\Encrypted-Sugar.zip", r"C:\Users\ansum\Desktop", ['1qaz0plm', '152634']])
#     t2 = time.perf_counter()
#     print(t2-t1)