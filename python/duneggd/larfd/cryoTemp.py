for z_i in range(self.nAPAs[2]):
    for y_i in range(self.nAPAs[1]):
        cpalist = {}
        for x_i in range(self.nAPAs[0]):

            isFirst = x_i == 0
            isLast  = x_i == self.nAPAs[0]-1

            # Rotating the volumes depending on whether they're top or bottom
            if y_i == self.nAPAs[1] - 1:
                rot0 = 'identity'
                rot1 = 'r180aboutY'
            else:
                rot0 = 'r180aboutX'
                rot1 = 'r180aboutX_180aboutY'

            if isFirst==False and isLast==False:
                
