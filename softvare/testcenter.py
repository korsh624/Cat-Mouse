import cv2
import numpy as np

# Create a black image (or load an existing one)
# Dimensions: 512x512, 3 channels (BGR), 8-bit unsigned integer
img = np.zeros((512, 512, 3), np.uint8) 

# 1. Draw an outlined green circle
center_outline = (100, 200)
radius_outline = 50
color_outline = (0, 255, 0) # Green in BGR
thickness_outline = 2
cv2.circle(img, center_outline, radius_outline, color_outline, thickness_outline)

# 2. Draw a filled red circle
center_filled = (400, 400)
radius_filled = 40
color_filled = (0, 0, 255) # Red in BGR
thickness_filled = -1 # Fills the circle
cv2.circle(img, center_filled, radius_filled, color_filled, thickness_filled)

# Display the image
cv2.imshow("Image with Circles", img)
cv2.waitKey(0) # Wait for a key press
cv2.destroyAllWindows()
