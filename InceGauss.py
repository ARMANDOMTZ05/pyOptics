import numpy as np
from scipy.special import factorial
import matplotlib.pyplot as plt

def Mesh_Elliptic(f, L, N):
    """"
    Creates eliptical coordinates

    Input

    """
    x, y = np.linspace(-L, L, N), np.linspace(-L, L, N)
    Y, X = np.meshgrid(x, y)

    xi = np.zeros((N,N))
    eta = np.zeros((N,N))

    en = np.arccosh((X[:N//2 + 1, N//2:] + 1j*Y[:N//2 + 1,N//2:])/f)
    ee = np.real(en)
    nn = np.imag(en)
    nn = nn + (nn < 0) * 2 * np.pi
    xi[:N//2 + 1, N//2:] = ee
    eta[:N//2 + 1, N//2:] = nn

    xi[:N//2 + 1, :N//2] = np.fliplr(xi[:N//2 + 1,N//2+1:])
    xi[N//2+1:, :] = np.flipud(xi[:N//2, :])
    eta[:N//2 + 1, :N//2] = np.pi - np.fliplr(eta[:N//2 + 1,N//2 + 1:])
    eta[N//2 + 1:,:] = np.pi + np.rot90(eta[:N//2, :], 2)

    return xi, eta, X,Y

def CInceIBG(p,m,q,z):
    if (m < 0) or (m  > p):
        raise ValueError('Wrong range for m')
    
    if (-1)**(m-p) != 1:
        raise ValueError('(p,m) must have same parity')
    
    if isinstance(z, np.ndarray):
        h,w = z.shape
        z = np.transpose(np.ravel(z, order='F'))

    normalization = 1

    if p % 2 == 0:
        l = p//2
        N = l+1
        n = m//2 + 1

        vec = np.concatenate(([2*q*l], q*(l-np.arange(1,N-1))))
        vec2 = np.concatenate(([0],4*(np.arange(0,N-1) + 1)**2))
        M = np.diag(q*(l+np.linspace(1,N-1,N-1)), k = 1) + np.diag(vec, k=-1) + np.diag(vec2)
        if p == 0:
            M = 0
            ets = np.array([0])
            A = np.array([1])[:,np.newaxis]
            index = np.array([0])

        else:
            ets, A = np.linalg.eig(M)
            index = np.argsort(ets)
            ets = np.sort(ets)
            A = A[:,index]

        if normalization == 0:
            n2 = 2*A[0,n-1] ** 2 + np.sum(A[1:N*1, n-1] **2)
            ns = np.sign(np.sum(A[:,n-1]))
            A = A/np.sqrt(n2)*ns
        
        else:
            mv = np.arange(2,p,2)
            n2 = np.sqrt(A[0,n-1] ** 2 * 2 * factorial(p/2) ** 2 + np.sum((np.sqrt(factorial((p+mv)/2) * factorial((p-mv)/2)) * A[1:p//2, n-1]) ** 2))
            ns = np.sign(np.sum(A[:,n-1]))
            A = A/n2*ns

        r = np.arange(0,N)
        R, X = np.meshgrid(r,z)
        ip = np.dot(np.cos(2*X*R),A[:, n-1])
        dip = np.dot(2*r*np.sin(2*X*R),A[:,n-1])
        eta = ets[n-1]
    else:
        l = (p-1)//2
        N = l + 1
        n = (m+1)//2

        diag_upper = q/2*(p + (2*np.arange(N-1) + 3))
        diag_lower = q/2*(p - (2*np.arange(1, N) - 1))
        diag_main = np.concatenate([[q/2 + p*q/2 + 1], (2 * np.arange(1, N) + 1)**2])

        M = np.diag(diag_upper, k = 1) + np.diag(diag_lower, k = -1) + np.diag(diag_main)

        ets, A = np.linalg.eig(M)
        index = np.argsort(ets)
        ets = np.sort(ets)
        A = A[:, index]

        if normalization:
            mv = np.arange(1,p+1,2)
            if mv.size == 0:
                mv = np.array([1])
            n2 = np.sqrt(np.sum((np.sqrt(factorial((p+mv)/2)*factorial((p-mv)/2)) * A[:,n-1]) ** 2))
            ns = np.sign(np.sum(A[:,n-1]))
            A = A/n2*ns

        else:
            n2 = np.sum(A[:,n] ** 2)
            ns = np.sign(np.sum(A[:,n]))
            A = A/n2*ns
            

        r = 2*np.arange(N) + 1
        R, X = np.meshgrid(r,z)
        ip = np.dot(np.cos(X * R), A[:,n-1])
        dip = np.dot(-R*np.sin(X * R), A[:, n-1])
        eta = ets[n-1]


    coef = A[:,n-1]

    if isinstance(z, int) or isinstance(z, float):

        return ip, eta, coef, dip
    
    else:

        ip = np.reshape(ip, [h,w])
        dip = np.reshape(dip, [h,w])

        return ip, eta, coef, dip

def SInceIGB(p,m,q,z):
    if (m < 1) or (m > p):
        raise ValueError('Wrong range for m')
    if (-1)**(m-p) != 1:
        raise ValueError('(p,m) must have the same parity')
    
    if isinstance(z, np.ndarray):
        h,w = z.shape
        z = np.transpose(np.ravel(z, order='F'))
    
    normalizaton = True
    if p % 2 == 0:
        l = p//2
        N = l + 1
        n = m//N

        diag_upper = q*(l + np.arange(2, N))
        diag_lower = q*(l - np.arange(1, N-1))
        diag_main = 4*(np.arange(N-1) + 1) ** 2
        M = np.diag(diag_upper, k = 1) + np.diag(diag_lower, k = -1) + np.diag(diag_main)

        ets, A = np.linalg.eig(M)
        index = np.argsort(ets)
        ets = np.sort(ets)
        A = A[:, index]

        # Normalization
        r = np.arange(1,N-1)

        if normalizaton:
            mv = np.arange(2, p + 1, 2)
            n2 = np.sqrt(np.sum((np.sqrt(factorial((p+mv)/2)*factorial((p-mv)/2)) * A[:,n-1]) ** 2))
            ns = np.sign(np.sum(r*A[:,n-1]))
            A = A/n2*ns

        else:
            n2 = np.sum(A[:,n-1]**2)
            ns = np.sign(np.sum(r*np.transpose(A[:,n-1])))
            A = A/np.sqrt(n2)*ns

        R,X = np.meshgrid(r,z)
        ip = np.dot(np.sin(2*X*R), A[:,n-1])
        dip = np.dot(2*R*np.cos(2*X*R), A[:, n-1])
        eta = ets[n-1]

    else:
        l = (p-1)//2
        N = l +1
        n = (m+1)//2

        diag_upper = q/2*(p + (2*np.arange(N-1) + 3))
        diag_lower = q/2*(p - (2*np.arange(1, N) - 1))
        diag_main = np.concatenate([[-q/2 - p*q/2 + 1], (2 * np.arange(1, N) + 1)**2])
        M = np.diag(diag_upper, k = 1) + np.diag(diag_lower, k = -1) + np.diag(diag_main)
        
        ets, A = np.linalg.eig(M)
        index = np.argsort(ets)
        ets = np.sort(ets)
        A = A[:, index]

        r = 2*np.arange(N) + 1

        if normalizaton:
            mv = np.arange(1,p+1,2)
            n2 = np.sqrt(np.sum((np.sqrt(factorial((p+mv)/2) * factorial((p-mv)/2)) * A[:, n - 1]) ** 2))
            ns = np.sign(np.sum(r*A[:,n-1]))
            A = A/n2*ns

        R, X = np.meshgrid(r, z)
        ip = np.dot(np.sin(X*R), A[:,n-1])
        dip = np.dot(R*np.cos(X*R), A[:,n-1])
        eta = ets[n-1]

    coef = A[:,n-1]

    if isinstance(z, int) or isinstance(z, float):

        return ip, eta, coef, dip
    
    else:

        ip = np.reshape(ip, [h,w])
        dip = np.reshape(dip, [h,w])

        return ip, eta, coef, dip

class InceGaussian:
    def __init__(self, L: float,
                 N: int,
                 parity,
                 p,
                 m,
                 e,
                 w0,
                 k,
                 z) -> None:
    
        self.L = L
        self.N = N
        self.parity = parity
        self.p = p
        self.m = m
        self.e = e
        self.w0 = w0
        self.k = k
        self.z = z


        if self.N % 2 == 0:
            raise Exception('N must be ODD')
        
        if self.parity == 0:
            if (self.m < 0) or (self.m > p):
                raise Exception('Wrong range from m')
        else:
            if (self.m < 1) or (self.m > p):
                raise Exception('Wrong range for m')
            
        if (-1) ** (self.m - self.p) != 1:
            raise Exception('(p,m) must have the same parity')
        
        self.f0 = np.sqrt(self.e / 2) * self.w0

        if self.z == 0:
            xhi,etha, X, Y = Mesh_Elliptic(self.f0,L,N)
            R = np.sqrt(X**2 + Y**2)

            if self.parity == 0:
                igb = CInceIBG(self.p, self.m, self.e,etha)[0] * CInceIBG(self.p,self.m, self.e, 1j*xhi)[0] * np.exp(-(R/self.w0) ** 2)
            else:
                igb = SInceIGB(self.p, self.m, self.e,etha)[0] * SInceIGB(self.p,self.m, self.e, 1j*xhi)[0] * np.exp(-(R/self.w0) ** 2)

            self.phase = np.ones_like(igb)
        else:
            zr = 1/2 * self.k * self.w0 ** 2
            wz = self.w0 * np.sqrt(1 + (z/zr) ** 2)
            Rz = z * (1 + (zr / z) ** 2)
            f = self.f0 * wz / w0
            xhi, etha, X, Y = Mesh_Elliptic(f, self.L, self.N)
            R = np.sqrt(X ** 2 + Y ** 2)

            self.phase = np.exp(1j * (self.k*z + self.k * R ** 2 / (2*Rz) - (self.p + 1) * np.arctan(z/zr)))

            if self.parity == 0:
                igb = (self.w0/wz) * (CInceIBG(self.p, self.m, self.e,etha)[0] * CInceIBG(self.p, self.m, self.e, 1j*xhi)[0]) * np.exp(-(R/wz) ** 2) * self.phase
            else:
                igb = (self.w0/wz) * (SInceIGB(self.p, self.m, self.e,etha)[0] * SInceIGB(self.p, self.m, self.e, 1j*xhi)[0]) * np.exp(-(R/wz) ** 2) * self.phase
        if self.parity == 0:
            c0, _, coef, _ = CInceIBG(self.p, self.m, self.e, 0)
            if self.p % 2 == 0:
                cp = CInceIBG(self.p, self.m, self.e, np.pi/2)[0]
                Norm = (-1) ** (self.m/2) * np.sqrt(2) * factorial(p/2) * coef[0] * np.sqrt(2/np.pi)/self.w0/c0/cp

            else:
                dcp = CInceIBG(self.p, self.m, self.e, np.pi/2)[-1]
                Norm = (-1)**((m+1)/2) * np.sqrt(2) * self.e * factorial((self.p + 1)/2) * np.sqrt(4*self.e/np.pi) * coef[0] / self.w0 / c0 / dcp
        else:
            if p % 2 == 0:
                _, _, coef, ds0 = SInceIGB(self.p,self.m,self.e,0)
                dsp = SInceIGB(self.p, self.m, self.e, np.pi/2)[-1]
                Norm = (-1) ** (self.m/2) * np.sqrt(2) * factorial((self.p + 2)/2) * coef[0] * np.sqrt(2/np.pi) / self.w0 / ds0 / dsp

            else:
                sp, _, coef, _ = SInceIGB(self.p, self.m, self.e, np.pi/2)
                ds0 = SInceIGB(self.p, self.m, self.m, 0)[-1]
                Norm = (-1) ** ((self.m-1)/2) * factorial((self.p + 1)/2) * np.sqrt(4*self.e/np.pi) * coef[0] / self.w0 / sp / ds0

        self.IGB = igb*Norm
        dx = np.abs(X[2,2] - X[1,0])
        Normalization = np.sum(np.sum(self.IGB * np.conj(self.IGB))) * dx ** 2
        print(f'Normalization: {np.real(Normalization)}')


    def plot_amplitude(self):
        plt.imshow(np.abs(self.IGB), extent=[-self.L, self.L, -self.L, self.L] ,cmap= 'gray')
        plt.title(f'Ince Gaussian Beam p={self.p}, m = {self.m}')
        plt.xlabel('x(m)')
        plt.ylabel('y(m)')
        plt.show()

    def plot_phase(self):
        plt.imshow(np.angle(self.IGB) ,cmap= 'gray')
        plt.title(f'Phase Ince Gaussian Beam p={self.p}, m = {self.m}')
        plt.xlabel('x(m)')
        plt.ylabel('y(m)')
        plt.show()

    def Hologam(self):
        '''
        Considering a DMD with resolution of 1920x1080
        '''
        Amp = np.abs(self.IGB)
        Amp = Amp/np.max(Amp)

        phi = np.angle(self.IGB)
        pp = np.arcsin(Amp)

        qq = phi

        self.CGH = 0.5 + 0.5 * np.sign(np.cos(pp) + np.cos(qq))



Ince = InceGaussian(15e-3, 501, 0, 6, 2, 2, 4e-3, (2*np.pi/632.8e-9), 0.375)
Ince.Hologam()

#xhi, etha, x, y = Mesh_Elliptic(0.0030, 0.015, 501)
#plt.imshow(etha, cmap= 'gray')
#plt.show()