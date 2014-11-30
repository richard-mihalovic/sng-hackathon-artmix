import cv2
from PIL import Image, ImageFilter

def calc_hist(image):
	hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
	return cv2.normalize(hist).flatten()

def compare_hist(h1, h2, method=cv2.cv.CV_COMP_CHISQR):
	return cv2.compareHist(h1, h2, method)

def find_min_hist(hist, values):
	min_val = 1000
	min_idx = None
	min_img = None

	for i in range(len(values)):
		hist_d = compare_hist(hist, values[i]['hist'])
		if min_val > hist_d:
			min_val = hist_d
			min_idx = i
			min_img = values[i]['img']

	return min_idx, min_val, min_img

path_images_a = [];
path_images_b = [];

W = 53
H = 40
BS = 15

for j in range(1, H + 1):
	for i in range(1, W + 1):
		path_images_a.append(str(j) + 'x' + str(i) + '.jpg')
		path_images_b.append(str(j) + 'x' + str(i) + '.jpg')

images_a = []
images_b = []

for img in path_images_a:
	file_name = './a/' + img

	image = cv2.imread(file_name)
	images_a.append(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
	print 'Load: ' + file_name

for img in path_images_b:
	file_name = './b/' + img

	image = cv2.imread(file_name)
	images_b.append(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
	print 'Load: ' + file_name

hist_a = {}
hist_b = {}
available_values = []

for i in range(len(images_a)):
	img = images_a[i];
	hist = calc_hist(img)
	hist_a[i] = hist

for i in range(len(images_b)):
	img = images_b[i]
	hist = calc_hist(img)
	hist_b[i] = hist
	available_values.append({'idx': i, 'hist': hist, 'img': img})

i = 0	
offset_x = 0
offset_y = 0

original_image = Image.new("RGB", (800, 600))
new_image = Image.new("RGB", (800, 600))

while len(available_values):
	hist = hist_a[i]
	idx, val, img = find_min_hist(hist, available_values)
	del available_values[idx]

	original_image.paste(
		Image.fromarray(images_a[W * offset_y + offset_x]), 
		(offset_x * BS, offset_y * BS)
	)

	new_image.paste(
		Image.fromarray(img), 
		(offset_x * BS, offset_y * BS)
	)

	offset_x += 1

	if offset_x >= W:
		offset_x = 0
		offset_y += 1

	i += 1

	print i, ' / ', W*H

original_image.save('result_org.jpg')
new_image.save('result.jpg')

# blurred_image = new_image.filter(ImageFilter.BLUR)
# blurred_image.save('result_b.jpg')