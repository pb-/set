# quick and dirty script to generate the peanut-shape icon
from math import sin, cos, tan, pi

def fmt(num):
    if abs(num - int(num)) < 1e-6:
        return int(num)
    return round(num, 2)


def make_path(length, girth, alpha):
    width = 100
    height = 60
    quarter = length / 4
    c1_x = (width - length) / 2
    c2_x = c1_x + length
    y = height / 2
    beta = pi - alpha

    dx = cos(alpha) * girth
    dy = -sin(alpha) * girth
    r = quarter / cos(beta)

    inner = 2 * -cos(alpha) * (r - girth)

    quarter = fmt(quarter)
    c1_x = fmt(c1_x)
    c2_x = fmt(c2_x)
    y = fmt(y)
    dx = fmt(dx)
    dy = fmt(dy)
    r = fmt(r)
    inner = fmt(inner)

    print(f'<path fill="none" stroke="black" stroke-width="2" d="M{c1_x} {y} m{dx} {dy} a{girth} {girth} 0 0 0 {-2*dx} {-2*dy} a{r-girth} {r-girth} 0 0 1 {inner} 0 a{r+girth} {r+girth} 0 0 0 {length-inner} 0 a{girth} {girth} 0 0 0 {2*dx} {2*dy} a{r-girth} {r-girth} 0 0 1 -{inner} 0 a{r+girth} {r+girth} 0 0 0 -{length-inner} 0" />')


print('<?xml version="1.0" encoding="UTF-8" ?><svg xmlns="http://www.w3.org/2000/svg" version="1.1">')
make_path(60, 13, 3 * pi / 4)
print('</svg>')
