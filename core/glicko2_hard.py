import math

class Player:
    def __init__(self, rating=1500, rd=275, vol=0.06, min_rd=130):
        self.rating = rating
        self.rd = rd
        self.vol = vol
        self.min_rd = min_rd
        self._tau = 0.3
        self._epsilon = 0.000001

    def getRating(self):
        return self.rating

    def getRd(self):
        return max(self.rd, self.min_rd)

    def _g(self, RD):
        return 1 / math.sqrt(1 + (3 * RD ** 2) / (math.pi ** 2))

    def _E(self, rating, RD):
        return 1 / (1 + math.exp(-self._g(RD) * (self.rating - rating) / 400))

    def update_player(self, rating_list, RD_list, outcome_list):
        v_inv = sum(
            (self._g(RD) ** 2) * self._E(rating, RD) * (1 - self._E(rating, RD))
            for rating, RD in zip(rating_list, RD_list)
        )
        v = 1 / v_inv

        delta = v * sum(
            self._g(RD) * (outcome - self._E(rating, RD))
            for rating, RD, outcome in zip(rating_list, RD_list, outcome_list)
        )

        a = math.log(self.vol ** 2)
        A = a

        if delta ** 2 > self.rd ** 2 + v:
            B = math.log(delta ** 2 - self.rd ** 2 - v)
        else:
            k = 1
            while self._f(a - k * self._tau, delta, v, a) < 0:
                k += 1
            B = a - k * self._tau

        fA, fB = self._f(A, delta, v, a), self._f(B, delta, v, a)

        while abs(B - A) > self._epsilon:
            C = A + (A - B) * fA / (fB - fA)
            fC = self._f(C, delta, v, a)
            if fC * fB < 0:
                A, fA = B, fB
            else:
                fA /= 2
            B, fB = C, fC

        self.vol = math.exp(A / 2)

        rd_star = math.sqrt(self.rd ** 2 + self.vol ** 2)
        new_rd = 1 / math.sqrt((1 / rd_star ** 2) + (1 / v))
        self.rd = max(new_rd, self.min_rd)

        sum_term = sum(
            self._g(RD) * (outcome - self._E(rating, RD))
            for rating, RD, outcome in zip(rating_list, RD_list, outcome_list)
        )
        self.rating += (self.rd ** 2) * sum_term

    def _f(self, x, delta, v, a):
        ex = math.exp(x)
        num = ex * (delta ** 2 - self.rd ** 2 - v - ex)
        denom = 2 * (self.rd ** 2 + v + ex) ** 2
        return (num / denom) - ((x - a) / (self._tau ** 2))
