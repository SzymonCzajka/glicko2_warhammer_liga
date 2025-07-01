import math

class Player:
    def __init__(self, rating=1500, rd=250, vol=0.06, tau=0.3, min_rd=130):
        self.rating = rating
        self.rd = rd
        self.vol = vol
        self.tau = tau
        self.min_rd = min_rd
        self._epsilon = 0.000001

    def getRating(self):
        return self.rating

    def getRd(self):
        return self.rd

    def _g(self, RD):
        return 1 / math.sqrt(1 + 3 * (RD ** 2) / (math.pi ** 2))

    def _E(self, rating, RD):
        return 1 / (1 + math.exp(-self._g(RD) * (self.rating - rating) / 400))

    def update_player(self, rating_list, RD_list, outcome_list):
        v_inv = 0
        for rating, RD in zip(rating_list, RD_list):
            E = self._E(rating, RD)
            g = self._g(RD)
            v_inv += (g ** 2) * E * (1 - E)
        v = 1 / v_inv

        delta_num = 0
        for rating, RD, outcome in zip(rating_list, RD_list, outcome_list):
            g = self._g(RD)
            E = self._E(rating, RD)
            delta_num += g * (outcome - E)
        delta = v * delta_num

        a = math.log(self.vol ** 2)
        A = a
        if delta ** 2 > self.rd ** 2 + v:
            B = math.log(delta ** 2 - self.rd ** 2 - v)
        else:
            k = 1
            while self._f(a - k * self.tau, delta, v, a) < 0:
                k += 1
            B = a - k * self.tau

        fA = self._f(A, delta, v, a)
        fB = self._f(B, delta, v, a)

        while abs(B - A) > self._epsilon:
            C = A + (A - B) * fA / (fB - fA)
            fC = self._f(C, delta, v, a)
            if fC * fB < 0:
                A = B
                fA = fB
            else:
                fA /= 2
            B = C
            fB = fC

        self.vol = math.exp(A / 2)

        pre_rd2 = self.rd ** 2 + self.vol ** 2
        rd_star = math.sqrt(pre_rd2)
        self.rd = 1 / math.sqrt((1 / rd_star ** 2) + (1 / v))
        self.rd = max(self.rd, self.min_rd)

        sum_term = 0
        for rating, RD, outcome in zip(rating_list, RD_list, outcome_list):
            g = self._g(RD)
            E = self._E(rating, RD)
            sum_term += g * (outcome - E)
        self.rating += (self.rd ** 2) * sum_term

    def _f(self, x, delta, v, a):
        exp_x = math.exp(x)
        num = exp_x * (delta ** 2 - self.rd ** 2 - v - exp_x)
        denom = 2 * (self.rd ** 2 + v + exp_x) ** 2
        return (num / denom) - ((x - a) / (self.tau ** 2))
