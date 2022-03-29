'''
    Modified this to be a ring fault detection model in our framework
    All credit for this algorithm goes to:
    
    @author  Skully (https://github.com/ImSkully)
    @website https://skully.tech
    @email   contact@skully.tech
    
    @file utils.py
    @updated 13/12/21
'''

import cv2 as cv
import numpy as np
import math

'''
	getDistanceBetweenPoints2D(x1, y1, x2, y2)
	Gets the distance between the two coordinates provided on a 2D plane.
		@param (int) x1 		The x1 coordinate to for position 1.
		@param (int) y1 		The y1 coordinate to for position 1.
		@param (int) x2 		The x2 coordinate to for position 2.
		@param (int) y2 		The y2 coordinate to for position 2.
		@returns (int) distance The total distance between the two points.
'''
def getDistanceBetweenPoints2D(x1, y1, x2, y2):
	distanceX = x1 - x2; distanceY = y1 - y2
	return math.sqrt((distanceX * distanceX) + (distanceY * distanceY))

'''
	isPositionWithinCircle(x, y, radius, centerPoint)
	Takes the given x, y coordinate and checks to see if it is within the boundary of the radius provided.
		@param (int) x 		     The x position.
		@param (int) y 			 The y position.
		@param (int) radius 	 The radius of the circle.
		@param (int) centerPoint The center point of this circle.
		@returns (Bool) result 	 True if the position given is within the circle, false otherwise.
'''
def isPositionWithinCircle(x, y, radius, centerPoint):
	if (((x - centerPoint[0]) ** 2) + ((y - centerPoint[1]) ** 2)) < (radius ** 2): return True
	return False

'''
	getRingCenter(image)
	Gets the center point of the ring within the image provided.
		@param 	image 		  The image containing the o-ring.
		@returns (int) [x, y] The x, y position of the ring's center point.
'''
def getRingCenter(image):
	x, y, sumX, sumY, labelID = 0, 0, 0, 0, 0 # Initialize coordinate variables.

	for x in range(0, image.shape[0]):
		for y in range(0, image.shape[1]):
			if(image[x, y] == 1): # If the label at the current index is 1.
				sumX += x
				sumY += y
				labelID += 1 # Increase label ID.
			y += 1 # Move to next row.
		x += 1 # Move to next column.
	
	# Center point is located at the sum of total x values divided by label ID, for both x, y.
	return [round(sumX / labelID), round(sumY / labelID)]

'''
	getBoundaryRatio(image, centerPoint)
	Gets the total ratio of pixels within the boundary of the o-ring vs. the total number of pixels outside of the ring.
		@param image 		The image containing the ring.
		@param centerPoint  The center point of the ring within the image.
		@returns (int) ratio The ratio of total pixels within divided by total pixels outside the boundary.
'''
def getBoundaryRatio(image, centerPoint):
	radius = getRingRadius(image, centerPoint) # Get the radius of our ring.
	outOfBoundary, withinBoundary = 0, 0

	for i in range(0, image.shape[0]):
		for j in range(0, image.shape[1]):
			withinOuterCircle = isPositionWithinCircle(i, j, radius[0], centerPoint)
			withinInnerCircle = isPositionWithinCircle(i, j, radius[1], centerPoint)

			# If this position is within the outer radius and not inside the inner radius.
			if not isPositionWithinCircle(i, j, radius[1], centerPoint) and withinOuterCircle:
				if image[i, j] == 1: withinBoundary += 1 # If this is labelled as 1, increase within boundary.
				elif image[i, j] == 0: outOfBoundary += 1 # Otherwise increase outside boundary.
			elif withinInnerCircle or (not withinOuterCircle and not withinInnerCircle): # Otherwise if we aren't within the inner or outer circle, or not within either circle.
				if image[i, j] == 1: outOfBoundary += 1 # Increase the out of boundary counter.

	return outOfBoundary / withinBoundary # Return our ratio of total within/outside the boundaries of the ring.

'''
	getRingCircularity(image, centerPoint)
	Gets the circularity of the ring in the image provided.
		@param 	image 				The image containing the ring.
		@param  centerPoint 		The position of the center point of the ring in the image.
		@returns (int) circularity  The circularity of the ring that was found.
'''
def getRingCircularity(image, centerPoint):
	distanceToRing = []

	for x in range(0, image.shape[0]):
		for y in range(0, image.shape[1]):
			if (image[x,y] == 1): # If the label at this index is 1.
				# Get the distance between this point and our center point and add it to our distances table.
				distanceToRing.append(getDistanceBetweenPoints2D(x, y, centerPoint[0], centerPoint[1]))
	
	# Circularity of the image is the mean value of all distances to the center point divided by the standard deviation of all distances.
	return np.mean(distanceToRing) / np.std(distanceToRing)

'''
	getRingRadius(image, centerPoint)
	Gets the radius of the ring within the image provided.
		@param image 		The image containing the ring.
		@param centerPoint  The center point within the image, used to obtain the distance to the ring.
		@return table
		{
			(int) outerRadius The radius of the outer ring.
			(int) innerRadius The radius of the inner ring.
			(int) thickness   The thickness of the ring.
		}
'''
def getRingRadius(image, centerPoint):
	innerRingRadius, outerRingRadius, currentPosition = 0, 0, 0
	x, y = centerPoint[0], centerPoint[1] # Starting x, y positions are from the center of the ring.

	while currentPosition != 2: # While we aren't outside of the ring.
		if (currentPosition == 0) and (image[x, y] == 1): # If the current position is within the ring and this is labelled as the ring.
			currentPosition = 1 # This position is on the ring.
			innerRingRadius = getDistanceBetweenPoints2D(x, y, centerPoint[0], centerPoint[1])
		elif (currentPosition == 1) and (image[x, y] == 0): # If the current position is on the ring and its labelled as outside the ring.
			currentPosition = 2 # We are at the edge of the ring.
			outerRingRadius = getDistanceBetweenPoints2D(x, y, centerPoint[0], centerPoint[1])
		x += 1 # Increase x coordinate and continue moving right.
	
	return (outerRingRadius, innerRingRadius, (outerRingRadius - innerRingRadius)) # Thickness of the ring is distance between the outer ring and the inner ring.