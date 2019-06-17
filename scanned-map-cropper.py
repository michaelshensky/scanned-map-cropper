from __future__ import division
from PIL import Image as imm
from PIL import ImageDraw as immd
from PIL import ImageTk as immtk
import os
import shutil
import statistics
import tkinter



#the directory containing the collared maps that will be cropped
inputdirectory = "sample_collared_maps"

#the directory where cropped maps will be saved - make sure you set this correctly
outputdirectory = "cropped_maps"

#delete the cropped map export directory if it exists and replace it with a new, empty directory
if os.path.isdir(outputdirectory):
    shutil.rmtree(outputdirectory, ignore_errors=True)

os.mkdir(outputdirectory)

#parameters here set a limit on how many maps will be processed  before script stops
#lower the limit value to test script on a small sample of maps
mapprocessinglimit = 100
mapsprocessed = 0

removerows = []
removecolumns = []
columntest = []
spantest = []
rowtest = []

#walk through all directories and files in the input directory
for root, dirs, files in os.walk(inputdirectory):

    #for each file in the input directory (keep in mind that this will also include files in subdirectories)
    for f in files:

        #if map processing limit not exceed and map is a tif or jpg file
        if mapsprocessed < mapprocessinglimit and (f[-3:] == "tif" or f[-3:] == "jpg"):
            img = imm.open(root + "/" + f)
            img.load()
            h = img.height
            w = img.width
            draw = immd.Draw(img)
            print(f)

            rgbimg = img.convert('RGB')
            pixels = rgbimg.load()


            threshold = 6000
            spanresolution = 10

            verticalscanlines = []
            horizontalscanlines = []

            for div in [2,3]:
                verticalscanlines.append(w/div)
                verticalscanlines.append((w/div) + 50)
                horizontalscanlines.append(h-(h/div))
                horizontalscanlines.append(h-((h/div) + 50))


            for yscan in verticalscanlines:
                draw.line((0,yscan, w,yscan), fill=(0,111,200,255), width=3)


            for xscan in horizontalscanlines:
                draw.line((xscan,0, xscan,h), fill=(0,111,200,255), width=3)


            allxspans = []
            allyspans = []
            listofallxspanslists = []
            listofallyspanslists = []

            for y in verticalscanlines:
                for x in range(w):
                    if x % spanresolution == 0 and x !=0:
                        xspan = []
                        for z in range(x-spanresolution,x):
                            currentpixel = pixels[z,y]
                            panc = currentpixel[0] + currentpixel[1] + currentpixel[2]
                            xspan.append(panc)
                        spantest = round(statistics.pvariance(xspan))
                        allxspans.append(spantest)
                        # print("pixel column [" + str(x) + "]   =   " + str(spantest))
                listofallxspanslists.append(allxspans)


            avgxspanvalues = [sum(e)/len(e) for e in zip(*listofallxspanslists)]

            for index, span in enumerate(avgxspanvalues):
                if span > threshold and index > 2:
                    mapxmin = index * spanresolution
                    print("MAPXMIN = " + str(mapxmin))
                    break

            for index, span in enumerate(reversed(avgxspanvalues)):
                if span > threshold and index > 2:
                    mapxmax = w - (index * spanresolution)
                    print("MAPXMAX = " + str(mapxmax))
                    break




            for x in horizontalscanlines:
                for y in range(h):
                    if y % spanresolution == 0 and y != 0:
                        yspan = []
                        for z in range(y - spanresolution, y):
                            currentpixel = pixels[x,z]
                            panc = currentpixel[0] + currentpixel[1] + currentpixel[2]
                            yspan.append(panc)
                        spantest = round(statistics.pvariance(yspan))
                        allyspans.append(spantest)
                        # print("pixel row [" + str(y) + "]   =   " + str(spantest))
                listofallyspanslists.append(allyspans)

            avgyspanvalues = [sum(e)/len(e) for e in zip(*listofallyspanslists)]

            for index, span in enumerate(avgyspanvalues):
                if span > threshold and index > 2:
                    mapymin = index * spanresolution
                    print("MAPYMIN = " + str(mapymin))
                    break

            for index, span in enumerate(reversed(avgyspanvalues)):
                if span > threshold and index > 2:
                    mapymax = h - (index * spanresolution)
                    print("MAPYMAX = " + str(mapymax))
                    break


            draw.line((0,mapymax, w,mapymax), fill=128, width=4)
            draw.line((0,mapymin, w,mapymin), fill=128, width=4)
            draw.line((mapxmax,0, mapxmax,h), fill=128, width=4)
            draw.line((mapxmin,0, mapxmin,h), fill=128, width=4)

            #show a popup window of the collared map with blue lines indicating which pixel columns/rows were scanned and red lines indicating where the map will be cropped
            img.show()

            #crop the map and save the new image to the cropped map output directory
            img.crop((mapxmin, mapymin, mapxmax, mapymax)).save(outputdirectory + "/" + f[:-4] + "_cropped" + f[-4:])

        mapsprocessed += 1
