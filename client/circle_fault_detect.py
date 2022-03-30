'''
    Modified this to be a ring fault detection model in our framework
    All credit for this algorithm goes to:

    @author  Skully (https://github.com/ImSkully)
    @website https://skully.tech
    @email   contact@skully.tech
    
    @file detection.py
    @updated 13/12/21
    
    Boundary and fault detection algorithm that determines whether or not a fault
    exists within a ring using raw Computer Vision.
'''

import cv2 as cv
import numpy as np
import sys, time, queue, os, os.path
import math 



BOUNDARY_THRESHOLD_UPPER = 0.18 # The upper threshold in which a ring must not have a boundary greater than in order to be considered not defective.
CIRCULARITY_THRESHOLD 	 = 11.0 # The maximum circularity threshold to allow for rings before being considered defective.

'''
    findThreshold(image)
    Clustering algorithm to find the threshold of the image provided based on the average grey level in pixels.
        @param 	image 				The image to obtain a threshold value of.
        @return (int) threshold 	The threshold value obtained.
'''
def findThreshold(image):
    
    # First, find a grey level based on the sum of all pixels in our image.
    sumOfPixels = 0
    print(image) 
    for i in range(0, image.shape[0]):
        for j in range(0, image.shape[1]):
            sumOfPixels = sumOfPixels + image[i, j]

    # The initial estimate for our threshold is the average grey level, obtained by the total sum of pixels multiplied by total pixels.
    greyLevel = round(sumOfPixels / (image.shape[0] * image.shape[1]))
    outputDebug("Average grey level: " + str(greyLevel))

    # Usage this initial T value, we can then segment the image and find all pixels above and below this threshold using clustering.
    lastThreshold = 0
    above, below = [], [] # All pixels above and below our threshold.
    while True:
        for i in range(0, image.shape[0]):
            for j in range(0, image.shape[1]):
                if image[i, j] > greyLevel: above.append(image[i, j]) # If this pixel is above the grey level, add it to foreground.
                else: below.append(image[i, j]) # Otherwise, add it to the background.


        # Threshold is equal to half of the mean of total pixels above the threshold + total pixels below threshold.
        threshold = (round(np.mean(above)) + round(np.mean(below))) / 2
        
        above.clear; below.clear # Clear our arrays.
        if threshold - lastThreshold < 1: break # If this threshold - the last threshold is now 0 or less, stop searching.
        else: lastThreshold = threshold

    outputDebug("Using threshold value: " + str(threshold))
    return threshold

'''
    thresholdImage(image, threshold)
        @param		image 		The image to threshold.
        @param 		threshold 	The threshold value to apply to the image.
        @returns 	image 		The image itself with the threshold applied to it.
'''
def thresholdImage(image, threshold):
    for i in range(0, image.shape[0]):
        for j in range(0, image.shape[1]):
            if image[i, j] > threshold: image[i, j] = 255 # If the pixel at this position is above our threshold, make it a white pixel.
            else: image[i, j] = 0 # Otherwise, this pixel is a foreground pixel, make it black.

    return image

'''
    getPositionBackgroundRelative(image, x, y)
    Takes the given position and checks to see if it is a background or foreground pixel, relative to the neighbours in the position.
        @param 	 image 		 The image to check neighbours for.
        @param 	 (int) x 	 The x position within the table and on the image to look at.
        @param 	 (int) y 	 The y position within the table and on the image to look at.
        @returns (int) state The value of the pixel, 255 if it is a background, 0 if it is a foreground.
'''
def getPositionBackgroundRelative(image, x, y):
    foregroundPixels = 0

    # Fetch all the neighbours of this position.
    neighbours = [
        image[x - 1, y - 1], image[x, y - 1], image[x + 1, y - 1], # Top Row
        image[x - 1, y], image[x + 1, y], # Middle Row
        image[x - 1, y + 1], image[x, y + 1], image[x + 1, y + 1], # Bottom Row
    ]

    for neighbour in neighbours: # Iterate through every neighbour in our table.
        if neighbour == 0: foregroundPixels += 1 # Otherwise, increase foreground pixel counter.

        # If there are less than 4 foreground pixels next to this neighbour, consider it a background.
        if foregroundPixels < 4: return 255
        else: return 0

'''
    applyBinaryMorph(image)
        @param 	image 	The image to apply binary morphing to.
        @return image 	The same image with morphing applied.
'''
def applyBinaryMorph(image):
    morphedImage = image.copy()

    for i in range(0, image.shape[0]):
        for j in range(0, image.shape[1]):
            if (i == 0 or i == image.shape[0] - 1) or (j == 0 or j == image.shape[1] - 1): #PATCH: can optimize this?
                pass # If we are at the end of an image, skip it.
            elif image[i, j] == 255: # If the pixel at this index is white.
                morphedImage[i, j] = getPositionBackgroundRelative(morphedImage, i, j)

    return morphedImage

'''
    imageHistogram(image)
        @param image 	The image to obtain a histogram of.
        @return image 	The generated histogram of the image provided.
'''
def imageHistogram(image):
    histogram = np.zeros(256) # Generate empty array of zeros with size of 256.
    for i in range(0, image.shape[0]): # Loop through the width of the image. (rows)
        for j in range(0, image.shape[1]): # Loop through the height of the image. (columns)
            histogram[image[i, j]] += 1 # Increase counter at this position in our table.
    return histogram

'''
    applyImageCCL(image)
    Takes the given image and applies connected component labelling to each pixel within the image by giving it a set label value.
        @param 	 image 		The image to apply CCL on.
        @returns image 		A image with labels applied based on the image provided.
'''
def applyImageCCL(image):
    labelledImage = image.copy()
    labelID = 1 # Start labelling with ID 1.
    labelQueue = queue.Queue() # Create a queue for our pixels.
    
    # Set all our labels initially to 0, background.
    for i in range(0, image.shape[0]):
        for j in range(0, image.shape[1]):
            labelledImage[i, j] = 0
    
    for i in range(0, image.shape[0]):
        for j in range(0, image.shape[1]):
            if (labelledImage[i, j] == 0) and (image[i, j] == 0): # If this index is not labelled, and its a foreground pixel.
                labelledImage[i, j] = labelID # Update the value to the current label ID.
                labelQueue.put([i, j]) # Add this index to our queue.

                # While the queue still has values in it, continue iterating.
                while labelQueue.qsize() > 0:
                    queuedPixel = labelQueue.get()

                    # Fetch direct neighbours of this pixel.
                    neighbours = [
                        [queuedPixel[0], queuedPixel[1] - 1],  # Neighbour above.
                        [queuedPixel[0], queuedPixel[1] + 1], # Neighbour below.
                        [queuedPixel[0] - 1, queuedPixel[1]], # Neighbour to the left.
                        [queuedPixel[0] + 1, queuedPixel[1]], # Neighbour to the right.
                    ]

                    for neighbour in neighbours: # Iterate through each neighbour.
                        # If this neighbour has not been visited before and doesn't have a label.
                        if (labelledImage[neighbour[0], neighbour[1]] == 0) and (image[neighbour[0], neighbour[1]] == 0):
                            labelledImage[neighbour[0], [neighbour[1]]] = labelID # Set current label ID to this neighbour.
                            labelQueue.put(neighbour) # Now add this neighbour into our queue.

                # Our label queue was cleared, increase label ID and process again.
                labelID += 1
    return labelledImage

'''
    isRingDefective(image, centerPoint)
    Determines whether the o-ring in the image provided is defective or not.
        @param 	 image  		The image to check.
        @param   centerPoint  	The center point of the ring within the image.
        @returns (Bool) state 	True if the ring is defective, false otherwise.
'''
def isRingDefective(image, centerPoint):
    circularity = round(getRingCircularity(image, centerPoint), 2)
    boundaryRatio = round(getBoundaryRatio(image, centerPoint), 2)
    outputDebug("Found circularity of: " + str(circularity))
    outputDebug("Found boundary ratio of: " + str(boundaryRatio))

    if (boundaryRatio > BOUNDARY_THRESHOLD_UPPER): return True
    elif (circularity > CIRCULARITY_THRESHOLD) or (boundaryRatio < 0.1): return False
    else: return True

'''
    renderLabeledRing(labeledImage, cliOnly)
    Renders an image of the labelled image provided with the defective status.
        @param (image) labeledImage 	The image to render, must be labelled through CCL.
        @param (Bool)  cliOnly 			Whether or not to run in CLI only mode, if this is true then only console outputs display, image is still rendered to output directory.
'''
def renderLabeledRing(labeledImage):
    # Finally, display the resulting image.
    labelFrequency = [0] * 4
    labeledImageCopy = labeledImage.copy()

    # Get the total number of labels attached to each pixel.
    for i in range(0, labeledImage.shape[0]):
        for j in range(0, labeledImage.shape[1]):
            if labeledImage[i, j] > 0: # If this pixel has a label on it.
                labelFrequency[labeledImage[i,j]] += 1 # Increase counter.
    # Set the most frequent label so we can identify the O-ring over broken pieces
    mostFrequent = np.argmax(labelFrequency)
    
    for i in range(0, labeledImage.shape[0]):
        for j in range(0, labeledImage.shape[1]):
            if labeledImage[i, j] > 0 and labeledImage[i, j] != mostFrequent:
                labeledImage[i, j] = 100
            elif labeledImage[i, j] == mostFrequent:
                labeledImage[i, j] = 255

    labeledImage = cv.cvtColor(labeledImage,cv.COLOR_GRAY2RGB)

    # Determine labels whether the ring is defective or not.
    centerPoint = getRingCenter(labeledImageCopy)
    outputDebug("Found center point at: " + str(centerPoint))
    defectiveState = isRingDefective(labeledImageCopy, centerPoint) # Whether this ring is defective or not.
    outputDebug("[FINISHED INSPECTION OF RING: "  + str(processingTime) + " seconds]")

    r, g, b, defectiveString = 0, 255, 0, "PASS" # Color value of the pass state/ring.
    if defectiveState: r, g, b = 0, 0, 255; defectiveString = "FAIL"

    # Render the ring around the center point of the o-ring.
    radius = getRingRadius(labeledImageCopy, centerPoint)
    cv.circle(labeledImage, (centerPoint[1], centerPoint[0]), round(radius[0]), (r, g, b), 2)
    
    # Add labels to the image relative to the image's width/height.
    imageWidth = labeledImageCopy.shape[0]
    imageHeight = labeledImageCopy.shape[1]

    cv.putText(labeledImage, defectiveString, (6, imageHeight - 10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (r, g, b), 1, cv.LINE_AA) # Pass/Fail Text
    if defectiveState:
        return True, labeledImage
    else:
        return False, labeledImage
        

'''
    outputDebug(message)
    Outputs debug information to the command line if debug mode is enabled.
        @param 	(string) message 	The message to output.
'''
def outputDebug(message, prefix = ''):
    #if DEBUG_OUTPUTS and message:
        #print(prefix + "  [" + str(CURRENT_RING_ID) + "]: " + str(message))
    pass

'''
    Modified this to be a ring fault detection model in our framework
    All credit for this algorithm goes to:
    
    @author  Skully (https://github.com/ImSkully)
    @website https://skully.tech
    @email   contact@skully.tech
    
    @file utils.py
    @updated 13/12/21
'''


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
    
    return (outerRingRadius, innerRingRadius, (outerRingRadius - innerRingRadius)) # Thickness of the ring is dista