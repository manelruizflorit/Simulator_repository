#First we will introduce de different airplanes data, organised in classes for each airplane;

class Airplane:

    def __init__(self, name, max_landing_weight, max_weight, max_payload,
                 S, CD0_app, CD2_app, CD0_clean, CD2_clean,
                 hp_desc, CT_desc_high, CT_desc_low, CT_desc_app,
                 CT1, CT2, CT3, CF1, CF2):

        self.name = name
        self.max_landing_weight = max_landing_weight
        self.max_weight = max_weight
        self.max_payload = max_payload
        self.S = S
        self.CD0_app = CD0_app
        self.CD2_app = CD2_app
        self.CD0_clean = CD0_clean
        self.CD2_clean = CD2_clean
        self.hp_desc = hp_desc
        self.CT_desc_high = CT_desc_high
        self.CT_desc_low = CT_desc_low
        self.CT_desc_app = CT_desc_app
        self.CT1 = CT1
        self.CT2 = CT2
        self.CT3 = CT3
        self.CF1 = CF1
        self.CF2 = CF2

#B767-300ER
B767 = Airplane(
    "B767",
    0.145150 * 10**6,
    0.20410 * 10**6,
    0.46500 * 10**5,
    0.28350 * 10**3,
    0.14000 * 10**-1,
    0.49000 * 10**-1,
    0.17400 * 10**-1,
    0.45900 * 10**-1,
    26418 * 0.3048,
    0.64359 * 10**-1,
    0.55988 * 10**-1,
0.12475,
    0.35167 * 10**6,
    0.44673 * 10**5 * 0.3048,
    0.10129 * 10**-9 * 10.7639,
    0.54005 * 1.6667 * 10**-5,
    0.55782 * 10**3 * 0.514444)

#B777-300
B777 = Airplane(
    "B777",
    0.237680 * 10**6,
    0.29930 * 10**6,
    0.64900 * 10**5,
    0.42804 * 10**3,
    0.17300 * 10**-1,
    0.48400 * 10**-1,
    0.15700 * 10**-1,
    0.42000 * 10**-1,
    36122 * 0.3048,
    0.44239 * 10**-1,
    0.41065 * 10**-1,
0.92921,
    0.42577 * 10**6,
    0.48987 * 10**5 * 0.3048,
    0.66146 * 10**-9 * 10.7639,
    0.87843 * 1.6667 * 10**-5,
    0.36897 * 10**3 * 0.514444)

