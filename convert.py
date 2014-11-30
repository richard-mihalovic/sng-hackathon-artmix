from PIL import Image

import json
import sys

if len(sys.argv) == 4:
    file_name = sys.argv[1]
    output_path = sys.argv[2]
    block_size = int(sys.argv[3])

    img = Image.open(file_name)

    n_width = img.size[0] // block_size
    n_height = img.size[1] // block_size

    print('block: {0}x{0}, {1}, {2}'.format(block_size, n_width, n_height))

    for j in range(n_height):
        for i in range(n_width):
            box = (
                i * block_size,
                j * block_size,
                i * block_size + block_size,
                j * block_size + block_size
            )
            region = img.crop(box)

            region.save(output_path + '/{0}x{1}.jpg'.format(j+1, i+1))

    with open(output_path + '/size.json','wt') as f:
        f.write(
            json.dumps({
                'width': n_width,
                'height': n_height
            })
        )