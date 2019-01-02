# Code

Traditionally, caricature artists are people but how would a robot draw caricatures? We embarked on a journey to find out. Enter CaricaTron, an opensource robotic caricature artist. Made possible by computer vision, below is a brief description of how CaricaTron works broken into two parts - software and hardware.

### Software

CaricaTron detects human faces and their key facial structures using OpenCV, Python, and the dlib library’s pre-trained facial landmark detector. Once a face is recognised the image is cropped and scaled to fit on a fixed canvas. This landmark detector returns 68 points, grouped into regions that represent the jaw, eyes, nose and mouth, which is then drawn to an SVG file and saved. This file is then used to draw the physical portrait. The software has to work in practically real time, with a fixed webcam, which presents non-trivial issues.

### Mechanical

The mechanical heart of CaricaTron is the AxiDraw- a CNC pen plotter. It is traditionally used to draw SVG images on a letter size paper. We were lucky enough to be given access to the alpha version of a Python library to control AxiDraw programmatically. But we wanted to go big, much bigger than letter size. So, we devised a light pantograph mechanism that extends the reach of the AxiDraw 2.5x. As for the canvas, we had many choices - a pen and paper, drywall markers, heat erasable inks… we opted to use a large touchscreen display that would allow us to draw and, more importantly, erase more reliably than the other methods.

CaricaTron was originally built to be a window display. We use a capacitive touch button for users to take a photo and have a caricature drawn. The button glows to invite users to press it. It is placed just in front of a hidden webcam which takes the photo. This setup, however, did not work as reliably as we expected. The capacitive sensor acted unreliably from behind a pane of glass resulting in false positives. However, while testing we realized that we didn’t need the button at all!

In the forthcoming iterations of the project we plan to streamline the design by removing the button and using computer vision to detect when a user is initiating an interaction. The display can then engage the user via text and, for example, ask the user to step forward if the face is too small. Recognising the tilt and size of the face gives us the ability to engage the user in a manner a real artist would, asking the user to strike a pose, or commenting on their features… We’re excited to continue developing CaricaTron.
