import cv2
from PIL import Image
from sys import argv


def load_image_as_blocks(path, block_size):
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img_height, img_width, img_depth = img.shape

    n_width = img_width // block_size
    n_height = img_height // block_size

    print('image: {0} {1}x{1}, {2}, {3}'.format(path, block_size, n_width, n_height))

    blocks = []
    for j in range(n_height):
        for i in range(n_width):
            blocks.append(
                img[
                    j * block_size:j * block_size + block_size,
                    i * block_size:i * block_size + block_size
                ]
            )

    return {
        'blocks': blocks,
        'horizontal_size': n_width,
        'vertical_size': n_height
    }


def calc_hist(image):
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    return cv2.normalize(hist).flatten()


def compare_hist(h1, h2, method):
    return cv2.compareHist(h1, h2, method)


def find_min_hist(hist, values, compare_method, sort_direction=1):
    min_val = 1000
    min_idx = None
    min_img = None

    if sort_direction < 0:
        min_val = - 1000

    for i in range(len(values)):
        hist_d = compare_hist(hist, values[i]['hist'], compare_method)
        if sort_direction > 0:
            if min_val > hist_d:
                min_val = hist_d
                min_idx = i
                min_img = values[i]['img']
        else:
            if min_val < hist_d:
                min_val = hist_d
                min_idx = i
                min_img = values[i]['img']

    return min_idx, min_val, min_img


def process_images(
    images_a, images_b,
    W, H,
    compare_method=cv2.cv.CV_COMP_CHISQR,
    sort_direction=1
):
    hist_a = {}
    hist_b = {}
    available_values = []

    for i in range(W * H):
        hist_a[i] = calc_hist(images_a[i])
        hist_b[i] = calc_hist(images_b[i])
        available_values.append({'idx': i, 'hist': hist_b[i], 'img': images_b[i]})

    i = 0
    offset_x = 0
    offset_y = 0

    new_image = Image.new('RGB', (800, 600))

    while len(available_values):
        hist = hist_a[i]
        idx, val, img = find_min_hist(hist, available_values, compare_method, sort_direction)
        del available_values[idx]

        new_image.paste(
            Image.fromarray(img),
            (offset_x * block_size, offset_y * block_size)
        )

        offset_x += 1

        if offset_x >= W:
            offset_x = 0
            offset_y += 1

        i += 1
        print i, ' / ', W * H

    return new_image


def parse_command_line():
    if len(argv) == 4:
        return argv[1], argv[2], argv[3]  # path1 path2 block_size
    else:
        print 'Usage: image1 image2 block_size'
        import sys
        sys.exit()

image_a_path, image_b_path, block_size = parse_command_line()

block_size = int(block_size)

image_a = load_image_as_blocks(image_a_path, block_size)
image_b = load_image_as_blocks(image_b_path, block_size)

images_a = image_a['blocks']
images_b = image_b['blocks']

W = min([image_a['horizontal_size'], image_b['horizontal_size']])
H = min([image_a['vertical_size'], image_b['vertical_size']])

image1 = process_images(
    images_a,
    images_b,
    W, H,
    compare_method=cv2.cv.CV_COMP_CORREL,
    sort_direction=-1
)
image1.save('result1.jpg')

image2 = process_images(
    images_a,
    images_b,
    W, H,
    compare_method=cv2.cv.CV_COMP_INTERSECT,
    sort_direction=-1
)
image2.save('result2.jpg')

image3 = process_images(
    images_a,
    images_b,
    W, H,
    compare_method=cv2.cv.CV_COMP_CHISQR
)
image3.save('result3.jpg')

image4 = process_images(
    images_a,
    images_b,
    W, H,
    compare_method=cv2.cv.CV_COMP_BHATTACHARYYA
)
image4.save('result4.jpg')
