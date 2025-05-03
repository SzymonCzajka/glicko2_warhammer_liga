import math

class Player:
    def __init__(self, rating=1500, rd=200, vol=0.06):
        self.rating = rating
        self.rd = rd
        self.vol = vol
        self._tau = 0.5
        self._epsilon = 0.000001

    def getRating(self):
        return self.rating

    def getRd(self):
        return self.rd

    def _g(self, RD):
        return 1 / math.sqrt(1 + (3 * RD ** 2) / (math.pi ** 2))

    def _E(self, rating, RD):
        return 1 / (1 + math.exp(-self._g(RD) * (self.rating - rating) / 400))

    def update_player(self, rating_list, RD_list, outcome_list):
        v_inv = 0
        for rating, RD in zip(rating_list, RD_list):
            E = self._E(rating, RD)
            g_RD = self._g(RD)
            v_inv += (g_RD ** 2) * E * (1 - E)
        v = 1 / v_inv

        delta_num = 0
        for rating, RD, outcome in zip(rating_list, RD_list, outcome_list):
            g_RD = self._g(RD)
            E = self._E(rating, RD)
            delta_num += g_RD * (outcome - E)
        delta = v * delta_num

        a = math.log(self.vol ** 2)
        A = a
        B = None
        if delta ** 2 > self.rd ** 2 + v:
            B = math.log(delta ** 2 - self.rd ** 2 - v)
        else:
            k = 1
            while self._f(a - k * self._tau, delta, v, a) < 0:
                k += 1
            B = a - k * self._tau

        fA = self._f(A, delta, v, a)
        fB = self._f(B, delta, v, a)

        while abs(B - A) > self._epsilon:
            C = A + (A - B) * fA / (fB - fA)
            fC = self._f(C, delta, v, a)
            if fC * fB < 0:
                A = B
                fA = fB
            else:
                fA = fA / 2
            B = C
            fB = fC

        new_vol = math.exp(A / 2)
        self.vol = new_vol

        pre_rd_squared_inv = 1 / (self.rd ** 2 + new_vol ** 2)
        rd_star = 1 / math.sqrt(pre_rd_squared_inv)
        self.rd = 1 / math.sqrt((1 / rd_star ** 2) + (1 / v))

        sum_term = 0
        for rating, RD, outcome in zip(rating_list, RD_list, outcome_list):
            g_RD = self._g(RD)
            E = self._E(rating, RD)
            sum_term += g_RD * (outcome - E)

        self.rating += (self.rd ** 2) * sum_term

    def _f(self, x, delta, v, a):
        ex = math.exp(x)
        num = ex * (delta ** 2 - self.rd ** 2 - v - ex)
        denom = 2 * (self.rd ** 2 + v + ex) ** 2
        return (num / denom) - ((x - a) / (self._tau ** 2))
