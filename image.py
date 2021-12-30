from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import json
import requests

with open("EBGaramond-Regular.ttf", 'rb') as reg:
    garamond_regular = ImageFont.truetype(reg, size=94)
with open("EBGaramond-Medium.ttf", 'rb') as reg:
    garamond_medium = ImageFont.truetype(reg, size=94)
with open("EBGaramond-Medium.ttf", 'rb') as reg:
    garamond_medium_small = ImageFont.truetype(reg, size=50)


def create_img(sentence: str, quoted_from: str = None, use_unsplash: bool = False) -> Image:
    W, H = (1920, 1080)
    sentence = f"\"{sentence}\""
    
    response = requests.get("https://picsum.photos/1920/1080")
    im = Image.open(BytesIO(response.content))
    im.thumbnail((1920, 1080), Image.ANTIALIAS)
    im = ImageEnhance.Brightness(im).enhance(.3)
    print("background ready :)")
    
    draw = ImageDraw.Draw(im)


    #find the average size of the letter
    sum = 0
    for letter in sentence:
        sum += draw.textsize(letter, font=garamond_medium)[0]

    average_length_of_letter = sum/len(sentence)

    #find the number of letters to be put on each line
    number_of_letters_for_each_line = (W/1.618)/average_length_of_letter
    incrementer = 0
    fresh_sentence = ''

    #add some line breaks
    for letter in sentence:
        if(letter == '-'):
            fresh_sentence += '\n\n' + letter
        elif(incrementer < number_of_letters_for_each_line):
            fresh_sentence += letter
        else:
            if(letter == ' '):
                fresh_sentence += '\n'
                incrementer = 0
            else:
                fresh_sentence += letter
        incrementer += 1

    print(fresh_sentence)

    #render the text in the center of the box
    dim = draw.textsize(fresh_sentence, font=garamond_medium)
    if quoted_from:
        dim_quoted_from = draw.textsize(quoted_from, font=garamond_medium_small)

    x2 = dim[0]
    y2 = dim[1]

    qx = (W/2 - x2/2)
    qy = (H/2 - y2/2)


    draw.text((qx, qy - (40 if quoted_from else 0)), fresh_sentence, fill="white", font=garamond_medium, align="center")
    if quoted_from:
        x = W/2 + x2/2 - dim_quoted_from[0]
        y = H/2 + y2/2 + 40
        draw.text((x if x > W/2 else W/2, y), quoted_from, fill="white", font=garamond_medium_small, align="left")

    # draw.rectangle((qx, qy, dim[0], dim[1]), fill="black")
    return im


if __name__ == '__main__':
    # create_img("this\nis\na\ntestadasdfasfd", True).show()
    # create_img("you\nare\na\ndumbass", True).save("test.png", "PNG")
    create_img(("test "*1)[:-1], "Luca"*5).save("test.png", "PNG")
