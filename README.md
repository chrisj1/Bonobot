# Bonobot
Discord bot that when you type "!bonobo " and @ someone, it posts an image of their profile picture on-to one of several bonobos
# How to help Bonobos
Bonobos are an endangered species and according to [this link](https://www.awf.org/blog/endangered-bonobo-africas-forgotten-ape) there are only about 15,000-20,000 of them left in the world.
To learn more and help these magnificient animals: https://www.bonobos.org/
# How to add a new bonobo template

0. Make sure your image is a bonobo. People trying to merge chips will be dealt with.
1. Fork and clone this repo
2. Save your new bonobo images to the autotemplates folder.
3. run `python template_generator/generate.py autotemplates/YOUR_TEMPLATE_FILE
`
4. Drag out rectangles over the faces of the bonobos
5. If you make mistake, the 'r' key resets the image and the 'esc' key will exit the program
6. When you are happy with your results, press enter to save your image. This will generate the mask file as well as convert your template image to a png if it is not one already.
7. Commit your changes and make a PR
