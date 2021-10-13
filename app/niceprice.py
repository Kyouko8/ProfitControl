import math

class CalculatorNicePriceV2:
    """
        Obtener un buen precio en base a:

        Costo
        Condición (nuevo/usado)
        Nivel de precio

            Nivel       Ganancia        Nombre
            -----       --------        ------
            0           0%  - 5%        Demasiado Barato
            1           10% - 20%       Muy Barato
            2           20% - 30%       Barato
            3           30% - 55%       Recomendado
            4           55% - 85%       Aceptable
            5           85% - 140%      Poco Aceptable
            6           140% - 200%     No recomendado
            7           200% - 270%     Definitivamente no recomendado
            8           270% - 350%     Demasiado Caro
            9           350% - Max.     Extremo
    """
    MAX_LEVEL = 9
    MIN_LEVEL = 0
    DEFAULT_LEVEL = 3
    MAX_RECOMENDED_LEVEL = 7
    MIN_RECOMENDED_LEVEL = 3

    def get_price(self, cost: int, new: bool=True, level: int=0) -> int:
        level = min(self.MAX_LEVEL, max(self.MIN_LEVEL, level))
        cost_multiply = self.cost_multiplier(cost)
        multiply = self.level_multiplier(new, level, cost_multiply=cost_multiply)
        price = multiply*cost
        if level >= 4:
            round_by = self.get_round_by(price*0.85)
        else:
            round_by = self.get_round_by(cost)
        
        return self.ceil_round(price, round_by)


    def ceil_round(self, amount: int, round_by: int) -> int:
        return int(math.ceil(amount / round_by)*round_by)


    def get_round_by(self, amount: int) -> float:
        """ Recibe:
        amount: Valor a redondear

        retorna: Valor por el que se debe redondear
        """
        
        # key: amount
        # value: round_by

        amounts = {
            0: 1,
            50: 5,
            150: 10,
            300: 25,
            700: 50,
            1500: 100,
            3000: 250,
            5000: 500,
            25000: 1000,
            100000: 5000,
        }

        if amount >= 400000:
            round_by = int("1"+"0"*len(str(int(amount))[3:]))
            
            if round_by <= amount*0.008:
                round_by = round_by*5

            print(amount, "···", len(str(int(amount))[3:]),  "->", round_by)

        else:
            round_by = 1
            for key, value in sorted(amounts.items(), key=lambda item: item[0]):
                if amount >= key:
                    round_by = value

        return round_by
        

    def level_multiplier(self, new: bool, level: int=0, cost_multiply: float=None) -> float:
        if level == 0: # Demasiado Barato
            mult = 1.0

        elif level == 1: # Muy Barato
            mult = 1.15

        elif level == 2: # Barato
            mult = 1.3

        elif level == 3: # Recomendado
            mult = 1.50

        elif level == 4: # Aceptable
            mult = 1.85

        elif level == 5: # Poco Aceptable
            mult = 2.30

        elif level == 6: # No Recomendado
            mult = 2.85

        elif level == 7: # Definitivamente no recomendado
            mult = 3.5

        elif level == 8: # Demasiado Caro
            mult = 4.5

        elif level == 9: # Extremo
            mult = 6

        else:
            raise Exception(f"Invalid level {level}")

        # Cost Multiply?
        if cost_multiply is not None:
            mult = mult * cost_multiply

        # New?
        if new:
            return max(1, mult)
        
        return max(1, mult * 0.95)


    def cost_multiplier(self, cost: int) -> float:
        if cost >= 1200:
            multiply = 0.90

        elif cost >= 900:
            multiply = 0.91
                
        elif cost >= 750:
            multiply = 0.93
        
        elif cost >= 500:
            multiply = 0.95

        elif cost >= 300:
            multiply = 0.98

        elif cost >= 100:
            multiply = 1
        
        elif cost >= 50:
            multiply = 1.2

        elif cost >= 25:
            multiply = 1.3
        
        else:
            multiply = 1.35

        return multiply


    def get_all_nice_price(self, amount, new=True):
        prices = []
        for level in range(10):
            prices.append(nice_price(amount, new, level))

        return prices


    def get_level_name(self, level):
        return {
            0: 'Demasiado Barato',
            0.8: 'Muy Barato',
            1: 'Muy Barato',
            1.8: 'Muy Barato',
            2: 'Barato',
            2.8: 'Casi Recomendado',
            3: 'Recomendado',
            3.8: 'Casi Aceptable',
            4: 'Aceptable',
            4.8: 'Límite Aceptable',
            5: 'Poco Aceptable',
            5.8: 'Caro',
            6: 'No Recomendado',
            6.8: 'Muy Caro',
            7: 'Muy Caro',
            7.8: 'Demasiado Caro',
            8: 'Demasiado Caro',
            8.8: 'Demasiado Caro',
            9: 'Extremo'
        }.get(level, "No Definido")
    

    def get_level_colors(self, level):
        return {
            0: 'indigo',
            1: 'indigo',
            2: 'indigo',
            3: 'blue',
            4: 'green',
            5: 'yellow',
            6: 'red',
            7: 'red',
            8: 'red',
            9: 'red',
        }.get(int(round(level)), "red")


    def get_price_status(self, price, cost, new, approximate=True):
        prev = self.get_price(cost, new, level=self.MIN_LEVEL)
        for level in range(self.MAX_LEVEL, self.MIN_LEVEL-1, -1):
            prev = self.get_price(cost, new, level=level-1)
            current = self.get_price(cost, new, level=level)
            if price >= current:
                break

            elif price >= round(current-(current-prev)*0.255):
                level = level-0.2
                break

        return max(self.MIN_LEVEL, min(self.MAX_LEVEL, level))


    def get_range_levels(self):
        return range(self.MAX_LEVEL, self.MIN_LEVEL-1, -1)



class NicePrice:
    calc = CalculatorNicePriceV2()

    def get_price(self, rcost, new=True, level=calc.DEFAULT_LEVEL):
        return self.calc.get_price(rcost, new, level)

    def get_levels_range(self):
        return self.calc.get_range_levels()

    def get_all_levels_name(self):
        return [(self.calc.get_level_name(i) for i in self.get_range_levels())]

    def get_level_name(self, level):
        return self.calc.get_level_name(level)

    def get_price_status(self, price, rcost, new=True, approximate=False):
        return self.calc.get_price_status(price, rcost, new, approximate=approximate)

    def get_price_status_as_word(self, price, rcost, new=True):
        return self.calc.get_level_name(
            self.get_price_status(price, rcost, new=new, approximate=True)
        )

    def get_price_status_color(self, price, rcost, new=True):
        return self.calc.get_level_colors(
            self.get_price_status(price, rcost, new=new)
        )

    def get_price_status_percent(self, price, rcost, new=True):
        max_price = self.get_price(rcost=rcost, new=new, level=self.calc.MAX_RECOMENDED_LEVEL)
        percent = round(100*(price-rcost) / max(0.1, max_price-rcost))
        return int(percent)
   
    def get_price_difference(self, price, rcost, new=True, level=1):
        return self.get_price(rcost, new=new, level=level) - price

    def get_percent_gain_by_cost(self, rcost, new=True, level=1):
        gain = self.get_gain(rcost, new, level)
        return int(round(100*(gain / max(0.5, rcost))))

    def get_percent_cost(self, rcost, new=True, level=1):
        price = self.get_price(rcost, new, level)
        return int(round(100*(rcost/price)))

    def get_percent_gain(self, rcost, new=True, level=1):
        return 100-self.get_percent_cost(rcost, new, level)

    def get_gain(self, rcost, new=True, level=1):
        return self.get_price(rcost, new, level) - rcost

    def get_profile_gain(self, profile_number, rcost, new=True, level=1):
        return int(round(self.get_gain(rcost, new, level) / profile_number))

