from flask import Flask, flash, redirect, send_file, render_template, request
from debug import request_dump
import os
import string
import random
import config
import PIL
from PIL import Image

app = Flask(__name__)


url = config.url
loc = config.loc
locname = config.locname
debug = config.debug
secret = config.secret_key
local = config.local
limit = config.imglimit
climit = config.consolelimit
port = config.port


global latestimg

latestimg = "../static/default.jpg"


def foldercheck():

    if locname not in os.listdir('./'):
        os.mkdir(loc)


def genfilename(console, filename, length):

    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    result = ''.join(random.choice(letters) for i in range(length))

    split_tup = os.path.splitext(filename)
    file_extension = split_tup[1]
    file_extension = str(file_extension).lower()

    finalname = console + "_" + result + file_extension

    if finalname in os.listdir(loc):
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        result = ''.join(random.choice(letters) for i in range(length))

        split_tup = os.path.splitext(filename)
        file_extension = split_tup[1]

        finalname = console + "_" + result + file_extension

    return finalname


def consolecheck(useragent):

    if "New Nintendo 3DS like iPhone" in useragent:
        console = "n3ds"
    elif "Nintendo WiiU" in useragent:
        console = "wiiu"
    elif "Nintendo 3DS" in useragent:
        console = "o3ds"
    elif "Nintendo DSi" in useragent:
        console = "ndsi"
    else:
        console = "unk"

    return console


@app.route('/')
def main():
    global latestimg

    if debug == True:
        request_dump(request)

    useragent = request.headers.get('User-Agent')

    consoleraw = consolecheck(useragent)

    match consoleraw:
        case "n3ds":
            console = "a New Nintendo 3DS"
        case "wiiu":
            console = "a Nintendo Wii U"
        case "o3ds":
            console = "an Old Nintendo 3DS"
        case "ndsi":
            console = "a Nintendo DSi"
        case "unk":
            console = "an unknown device"
        case _:
            console = "_"

    return render_template('index.html', console=console, latestimg=latestimg)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global latestimg

    if debug == True:
        request_dump(request)
    useragent = request.headers.get('User-Agent')
    console = consolecheck(useragent)

    if request.method == 'POST':
        file = request.files['file']

        filename = genfilename(console, file.filename, 8)

        img = Image.open(file)
        wid, hgt = img.size
        if wid not in [400, 320, 854, 1920, 1360, 1366, 1280]:
            return render_template('error.html', error="Image width is incorrect.")
        if hgt not in [240, 480, 720, 1080]:
            return render_template('error.html', error="Image height is incorrect.")
        if console == "unk":
            return  render_template('error.html', error="You are not uploading from a 3DS/Wii U console.")

        img.save(os.path.join(loc, filename))

        latestimg = filename

        return render_template('complete.html', uploadname=filename, url=url)

    return render_template('upload.html', uploadname="image.jpg", url=url)


@app.route('/list')
def list():
    if debug == True:
        request_dump(request)

    n3dsimages = []
    wiiuimages = []
    o3dsimages = []

    for image in os.listdir(loc):
        if "n3ds_" in image:
            n3dsimages.append(image)
        if "wiiu_" in image:
            wiiuimages.append(image)
        if "o3ds_" in image:
            o3dsimages.append(image)

    useragent = request.headers.get('User-Agent')
    consoleraw = consolecheck(useragent)

    if consoleraw == "unk" and limit is not None:
        while len(n3dsimages) > limit:
            n3dsimages.pop()
        while len(wiiuimages) > limit:
            wiiuimages.pop()
        while len(o3dsimages) > limit:
            o3dsimages.pop()
    
    if consoleraw != "unk" and climit is not None:
        while len(n3dsimages) > climit:
            n3dsimages.pop(-1)
        while len(wiiuimages) > climit:
            wiiuimages.pop()
        while len(o3dsimages) > climit:
            o3dsimages.pop()


    return render_template("list.html", n3dsimages=n3dsimages, wiiuimages=wiiuimages, o3dsimages=o3dsimages, limit=limit if consoleraw == "unk" else climit)


@app.route('/css/<sheet>.css')
def css(sheet):

    return send_file(f"./static/{sheet}.css")


@app.route('/uploads/<image>')
def view(image):

    return send_file(f"{loc}/{image}")


if __name__ == '__main__':
    foldercheck()
    app.secret_key = secret
    app.run(url, port, debug)
