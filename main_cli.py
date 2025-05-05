from gui import PokerGUI
import math

def get_ellipse_positions(cx, cy, a, b, n):
    positions = []
    for i in range(n):
        theta = 2 * math.pi * i / n
        x = cx + a * math.cos(theta)
        y = cy + b * math.sin(theta)
        positions.append((x, y))
    return positions

if __name__ == "__main__":
    app = PokerGUI()
    SEAT_COORDS = get_ellipse_positions(400, 250, 300, 180, 9)
    app.mainloop()