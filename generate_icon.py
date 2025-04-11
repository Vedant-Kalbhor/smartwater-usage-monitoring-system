import numpy as np
from PIL import Image, ImageDraw

# Create a blank image with transparent background
width, height = 512, 512
img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Draw a water drop shape
center_x, center_y = width // 2, height // 2
drop_width, drop_height = width * 0.7, height * 0.8
drop_top = center_y - drop_height // 2
drop_bottom = drop_top + drop_height

# Water drop coordinates
drop_shape = [
    (center_x, drop_top),  # Top point
    (center_x + drop_width // 2, center_y),  # Right bulge
    (center_x, drop_bottom),  # Bottom point
    (center_x - drop_width // 2, center_y),  # Left bulge
]

# Draw the water drop with a blue gradient
gradient_blue = (41, 128, 185)  # Blue color
draw.polygon(drop_shape, fill=gradient_blue)

# Add some highlights
highlight_shape = [
    (center_x - drop_width // 4, center_y - drop_height // 6),
    (center_x, center_y - drop_height // 4),
    (center_x + drop_width // 5, center_y - drop_height // 8),
]
draw.polygon(highlight_shape, fill=(255, 255, 255, 100))

# Add a simple water wave pattern inside
wave_y = center_y + drop_height // 6
wave_width = drop_width // 2
wave_points = []

# Create a simple wave pattern
for x in range(int(center_x - wave_width // 2), int(center_x + wave_width // 2), 5):
    y_offset = 10 * np.sin((x - (center_x - wave_width // 2)) / 20)
    wave_points.append((x, wave_y + y_offset))

# Connect the wave points to create a flowing pattern
if wave_points:
    previous_point = wave_points[0]
    for point in wave_points[1:]:
        draw.line([previous_point, point], fill=(255, 255, 255, 150), width=2)
        previous_point = point

# Save the image
img.save('generated-icon.png')
print("Icon successfully generated as 'generated-icon.png'")