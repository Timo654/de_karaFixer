#thanks to ryanbevins and SutandoTsukai181 for research
import sys
import os

global MODIFIED_COUNT
input_files = sys.argv[1:]
ENDIANNESS = 'little'
MODIFIED_COUNT = 0

# checks if there are any files
if input_files == []:
    input("No files detected. You need to drag and drop the file(s).\nPress any key to continue.")
    quit()

# gets max possible score
def get_score(binary_data, n_notes, header_size):
    i = 1
    score = 0
    offset = header_size + 20
    regular_count = 0
    hold_count = 0
    rapid_count = 0
    while i <= n_notes:
        note_type = int.from_bytes(binary_data[offset:offset + 4], ENDIANNESS)
        if note_type == 0:  # regular
            score += 10  # regular note is 10pt (Great)
            regular_count += 1
        elif note_type == 1:  # hold
            score += 30  # hold note is 30pt (Great)
            hold_count += 1
        elif note_type == 2:  # rapid
            score += 30  # rapid note is 30pt (Great)
            rapid_count += 1
        if i > 20:  # if heat mode is available (triggers at 20x combo)
            score += 5  # +5 points per note during heat mode

        offset += 32
        i += 1
    print(f'{regular_count} regular notes\n{hold_count} hold notes\n{rapid_count} rapid notes')
    return score


def save_file(input_file, binary_data):
    with open(f'{input_file[:-4]}-new.kbd', 'wb') as f:
        f.write(binary_data)
        print(f'{os.path.basename(input_file)[:-4]}-new.kbd saved.')

# loads the file
def magic_check(binary_data, input_file):
    try:
        magic = binary_data[0x0:0x4].decode()
    except(UnicodeDecodeError):
        print(f"Can't load magic for {os.path.basename(input_file)}, skipping file.")
        return False
    if magic == "NTBK":
        ver = int.from_bytes(binary_data[0x8:0xC], ENDIANNESS)
        if ver in [1, 2]:
            return True
        else:
            print(f'Unknown version {ver} found.\nSkipping {os.path.basename(input_file)}')
            return False
    else:
        print(f'Magic does not match, most likely not a valid karaoke file.\nSkipping {os.path.basename(input_file)}.')
        return False

def load_file(input_file):
    with open(input_file, 'rb') as binary_file:
        binary_data = bytearray(binary_file.read())
        num_bytes = binary_file.tell()
    if magic_check(binary_data, input_file):
        update_values(binary_data, num_bytes, input_file)


def update_values(binary_data, num_bytes, input_file):
    global MODIFIED_COUNT
    # load values from header
    print('Loading data from header...')
    ver = int.from_bytes(binary_data[0x8:0xC], ENDIANNESS)
    size = int.from_bytes(binary_data[0xC:0x10], ENDIANNESS)
    n_notes = int.from_bytes(binary_data[0x10:0x14], ENDIANNESS)
    max_score = int.from_bytes(binary_data[0x14:0x18], ENDIANNESS)
        

    print(f'Version: {ver}')
    print(f'Size w/o header: {size}')
    print(f'Number of notes: {n_notes}')
    print(f'Max score: {max_score}')

    if ver == 1:
        header_size = 24
    elif ver == 2:
        header_size = 28

    # calculates header size
    actual_size = num_bytes - header_size
    
    # calculates number of notes
    # 32 bytes is the size of 1 note info
    actual_n_notes = int(actual_size / 32)
    # calculates max score
    actual_max_score = get_score(binary_data, actual_n_notes, header_size)

    # update values
    file_modified = False
    if size != actual_size:
        binary_data[0xC:0x10] = actual_size.to_bytes(4, byteorder=ENDIANNESS)
        file_modified = True
        print(f'Updated size value. Old: {size} New: {actual_size}')
    if n_notes != actual_n_notes:
        binary_data[0x10:0x14] = actual_n_notes.to_bytes(
            4, byteorder=ENDIANNESS)
        file_modified = True
        print(
            f'Updated note count. Old: {n_notes} New: {actual_n_notes}')
    if max_score != actual_max_score:
        binary_data[0x14:0x18] = actual_max_score.to_bytes(
            4, byteorder=ENDIANNESS)
        file_modified = True
        print(f'Updated max score. Old: {max_score} New: {actual_max_score}')

    # save file
    if file_modified:
        save_file(input_file, binary_data)
        MODIFIED_COUNT += 1
    else:
        print(f'No values were updated in {os.path.basename(input_file)}.')


# loads each file
for file in input_files:
    load_file(file)

input(f"{MODIFIED_COUNT} file(s) were updated.\nPress enter to continue...")
