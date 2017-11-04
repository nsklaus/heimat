
def pos_in_newmap(self, door):
    """ -> list """
    newpos = ['','']
    tempx = 0
    tempy = 0
    # door on left side
    if door.x == 0:
        tempx = (door.x + 128)
        tempy = (door.y + 64)
        newpos[1] = 'left'
    # door on top side
    elif door.x > 0 and door.y == 0:
        tempx = (door.x + 64)
        tempy = (door.y + 128)
        newpos[1] = 'top'
    # door on bottom side
    elif door.x > 0 and door.y == self.map.height - 64:
        tempx = (door.x + 64)
        tempy = (door.y - 64)
        newpos[1] = 'bottom'
    # door on right side
    elif door.x == self.map.width - 64 and door.y > 0:
        tempx = (door.x - 64)
        tempy = (door.y + 64)
        newpos[1] = 'right'
    newpos[0] = (tempx, tempy)
    return newpos
