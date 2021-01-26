# Quick & dirty preparation of a string containing the font.

s = "".join(chr(i) for i in range(32, 127))
font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf", size=24)
img = font.getmask(s, mode="1")
numpy.array(img).reshape(1330, 23)
fnt = numpy.array(img).reshape(1330, 23) // 255
fnt = numpy.array(img).reshape(23, -1) // 255
fnt2 = numpy.zeros((24, fnt.shape[1]), dtype=bool)
fnt2[0:-1] = fnt
fnt2[:14]
imshow(fnt2)
compact = numpy.zeros((3, fnt.shape[1]), dtype="uint8")
for i in range(8):
    compact = numpy.bitwise_or(compact, fnt2[i::8].astype("uint8") << i)
sfont = numpy.bitwise_not(compact[:, ].T).tobytes()
