from scipy.stats import norm
import numpy as np

'''
    TODO
'''
class BsmOption:
    def __init__(self, isLong, Type, S, K, T, r, sigma=None, value=None, q=0.0):
        '''
        NOTE Only sigma OR value should be passed to the constructor \n

        isLong -> Long / short          [bool]          [False]         Short the option                \n
        Type -> 'P' or 'C'              [Char]          ['P']           Put option                      \n
        S -> Underlying Price           [$]             [100]           100$ Underlying                 \n
        K -> Strike                     [$]             [110]           110$ Strike                     \n
        T -> Time until expiration      [Decimal]       [20]            20 DTE                          \n
        r -> Risk free rate             [Decimal]       [0.01]          1% RFR Continous yield          \n
        sigma -> Volatility             [Decimal]       [0.45]          45% Vol                         \n
        value -> Option Price           [$]             [1.56]          1.56$                           \n
        q -> Dividend Value             [Decimal]       [0.01]          1% Continous Div yield         \n   
        '''
        self.isLong = isLong
        self.Type = Type.upper()
        self.S = S 
        self.K = K
        self.T = T / 365
        self.r = r
        self.q = q
        self.sigma = sigma
        self.value = value

        #Get sigma from market price
        if sigma is None:
            self.NewtonRaphson()

        if value is None:
            self.value = self.price()

        if (type(self.isLong) is not bool or type(self.Type) is not str):
            raise ValueError('Incorrect types for constructor')
        if ( not (self.Type == 'P' or self.Type == 'C')):
            raise ValueError('Must be "P" or "C"')

    
    @staticmethod
    def N(x):
        return norm.cdf(x)

    @staticmethod
    def N_prime(x):
        return norm.pdf(x)

    @property
    def params(self):
        return {'isLong': self.isLong,
                'Type': self.Type,
                'S': self.S,
                'K': self.K,
                'T': self.T,
                'r': self.r,
                'sigma': self.sigma,
                'value': self.value,
                'q': self.q}


    def NewtonRaphson(self):
        '''
        https://en.wikipedia.org/wiki/Newton%27s_method \n
        Get approximate sigma using Newton Raphson Method for root finding \n
        Iterates until 0.1% accuracy \n
        '''
        sigma_i_1 = 0
        sigma_i = 1 #arbitrary guess
        self.setSigma(sigma_i)
        while 1:
            sigma_i_1 = sigma_i - ((self.price() - self.value) / (self.vega() * 100))
            sigma_i = sigma_i_1
            self.setSigma(sigma_i)
            if ( abs((self.value - self.price()) /  self.value) < 0.001 ):
                self.setSigma(abs(sigma_i))
                return


    def d1(self):
        return (np.log(self.S/self.K) + ((self.r -self.q + self.sigma**2/2)*self.T)) / (self.sigma*np.sqrt(self.T))
    
    def d2(self):
        return self.d1() - self.sigma*np.sqrt(self.T)
    
    def _call_value(self):
        call_value = self.S*np.exp(-self.q*self.T)*self.N(self.d1()) - self.K*np.exp(-self.r*self.T) * self.N(self.d2())
        if (self.isLong):
            return call_value
        return -1 * call_value
                    
    def _put_value(self):
        put_value = (self.K*np.exp(-self.r*self.T) * self.N(-self.d2())) - (self.S*np.exp(-self.q*self.T)*self.N(-self.d1()))
        if (self.isLong):
            return put_value
        return -1 * put_value

    def delta(self):
        '''
        Return Delta Greek Value \n
        '''
        delta = 0
        if self.Type == 'C':
            delta = np.exp(-self.q * self.T) * self.N(self.d1())
        if self.Type == 'P':
            delta = -np.exp(-self.q * self.T) * self.N(-self.d1())

        if (self.isLong):
            return delta

        return delta * -1
        
        

    def gamma(self):
        '''
        Return Gamma Greek Value \n
        '''
        gamma =  np.exp(-self.q * self.T) * ((self.N_prime(self.d1())) / (self.S * self.sigma * np.sqrt(self.T)))

        if (self.isLong):
            return gamma

        return gamma * -1

    def vega(self):
        '''
        Return Delta Greek Value \n
        '''
        vega = self.S * np.exp(-self.q * self.T) * self.N_prime(self.d1()) * np.sqrt(self.T)

        vega /= 100 #adjustment factor to single share

        if (self.isLong):
            return vega

        return vega * -1


    def theta(self):
        '''
        Return theta Greek Value \n
        '''
        theta = 0
        if self.Type == 'C':
            theta = (-np.exp(-self.q * self.T) * ((self.S * self.N_prime(self.d1()) * self.sigma)/(2 * np.sqrt(self.T)))) - (self.r * self.K * np.exp(-self.r * self.T) * self.N(self.d2())) + (self.q * self.S * np.exp(-self.q * self.T) * self.N(self.d1()))
        if self.Type == 'P':
            theta = (-np.exp(-self.q * self.T) * ((self.S * self.N_prime(self.d1()) * self.sigma)/(2 * np.sqrt(self.T)))) + (self.r * self.K * np.exp(-self.r * self.T) * self.N(-self.d2())) - (self.q * self.S * np.exp(-self.q * self.T) * self.N(-self.d1()))

        theta /= 365

        if (self.isLong):
            return theta 

        return theta * -1


    def rho(self):
        '''
        Return rho Greek Value \n
        '''
        rho = 0
        if self.Type == 'C':
            rho = self.K * self.T * np.exp(-self.r * self.T) * self.N(self.d2())
        if self.Type == 'P':
            rho = -self.K * self.T * np.exp(-self.r * self.T) * self.N(-self.d2())
        
        rho /= 100 #adjustment factor to single share

        if (self.isLong):
            return rho
        
        return rho * -1
    
    def price(self):
        '''
        Return price of option \n
        '''
        if self.Type == 'C':
            return self._call_value()
        if self.Type == 'P':
            return self._put_value()


    def setSpot(self, spot):
        '''
        Sets new spot price \n
        '''
        self.S = spot

    def setDTE(self, DTE):
        '''
        Sets new DTE \n
        '''
        self.T = DTE / 365

    def setSigma(self, sigma):
        '''
        Sets new volatility value \n
        '''
        self.sigma = sigma



'''
    TODO
        >Add selector for individual option
            *Can then call indivudal update functions that option
'''
class OptionPosition:
    def __init__(self, options=[]):
        '''
        option -> BSM option object LIST \n
        '''
        self.legs = []
        self.shares = 0
        for option in options:
            self.legs.append(option)


    def addLegs(self, options):
        '''
        option -> BSM option object LIST \n
        adds option leg to position \n
        '''
        for option in options:
            self.legs.append(option)

    def addShares(self, shares):
        '''
        shares -> Num shares \n
        adds shares to position \n
        '''
        self.shares += shares

    def removeShares(self, shares):
        '''
        shares -> Num shares \n
        removes shares from position \n
        '''
        self.shares -= shares

    def removeLeg(self, option):
        '''
        option -> BSM option object to be removed \n
        Removes leg from position \n
        '''
        try:
            self.legs.remove(option)
        except Exception as e:
            print(e)

    def getLeg(self, index):
        '''
        Get leg at specified index \n
        '''
        if (index > len(self.legs)):
            raise Exception("Cannot get index greater than size")

        return self.legs[index]

    def price(self):
        '''
        Returns current theoretical price of position \n
        '''
        value = 0
        for leg in self.legs:
            value += leg.price()
        return value

    def delta(self):
        '''
        Returns current delta of position \n
        '''
        value = 0
        for leg in self.legs:
            value += leg.delta()
        value += (self.shares/100)
        return value

    def gamma(self):
        '''
        Returns current gamma of position \n
        '''
        value = 0
        for leg in self.legs:
            value += leg.gamma()
        return value

    def vega(self):
        '''
        Returns current vega of position \n
        '''
        value = 0
        for leg in self.legs:
            value += leg.vega()
        return value

    def theta(self):
        '''
        Returns current theta of position \n
        '''
        value = 0
        for leg in self.legs:
            value += leg.theta()
        return value

    def rho(self):
        '''
        Returns current rho of position \n
        '''
        value = 0
        for leg in self.legs:
            value += leg.rho()
        return value

    def sigma(self):
        '''
        Returns average sigma of position \n
        '''
        value = 0
        for leg in self.legs:
            value += leg.sigma
        return value / len(self.legs)


    def updateDTE(self, DTE):
        '''
        Updates DTE of !ALL! options in position \n
        '''
        for leg in self.legs:
            leg.setDTE(DTE)

    def updateSigma(self, DTE):
        '''
        Updates DTE of !ALL! options in position \n
        '''
        for leg in self.legs:
            leg.setSigma(DTE)

    def updateSpot(self, spot):
        '''
        Updates Spot price of !ALL! options in position \n
        '''
        for leg in self.legs:
            leg.setSpot(spot)

    def updateSpotReturnPrice(self, spot):
        '''
        Updates Spot price of !ALL! options in position and returns new price \n
        '''
        for leg in self.legs:
            leg.setSpot(spot)
        return self.price()

    def getSpot(self):
        '''
        Return spot price of first leg.
        '''
        return self.legs[0].S
    
    def getR(self):
        '''
        Return RFR of first leg.
        '''
        return self.legs[0].r

    def getDTE(self):
        '''
        Return DTE of first leg
        '''
        return self.legs[0].T * 365

    


    




 