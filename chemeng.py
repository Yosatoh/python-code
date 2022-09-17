import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy


class CoefBank(object):
    
    def __init__(self):
        pass

    
class Antoine(object):
    
    def __init__(self, comp_list=None, param_file=None):
        
        self.comp_dict = None
        self._calc_flag = False

        if isinstance(comp_list, dict):
            temp_comp_list = []
            temp_value_list = []
            for comp, value in comp_list.items():
                temp_comp_list.append(comp)
                temp_value_list.append(value)
            self.components = temp_comp_list.copy()
            temp_arr = np.array(temp_value_list)
            total = temp_arr.sum()
            temp_value_list = (temp_arr/total).tolist()
            comp_dict = {}
            for i, comp in enumerate(temp_comp_list):
                comp_dict[comp] = temp_value_list[i]
            self.comp_dict = comp_dict
        elif isinstance(comp_list, list):
            self.components = comp_list
        else:
            raise Exception("the type of comp_list is list or dictionary") 

        if param_file is None:
            self.databank = {
                'aceton': (7.29958, 1312.25, 240.705),
                'methanol' : (8.07919, 1583.34, 239.650),
                'ethanol': (8.12187, 1598.673, 226.726),
                'hexane':(6.89122, 1178.802, 225.200),
                'heptane': (6.89798, 1265.235, 216.533),
                'benzene': (7.60093, 1660.652, 271.689),
                'toluene': (6.96554, 1351.272, 220.191),
                'methyl ethyl ketone': (6.86450, 1150.207, 209.246),
                'water' : (8.02754, 1705.62, 231.405),
            }
        else:
            df = pd.read_csv('antoine_params.csv', header=0)
            temp_dict = {}
            for v in df.itertuples():
                temp_dict[v[1]] = v[2]
            self.databank = temp_dict
    
    def equation(self):
        print(r'$\log{P} = A - \frac{B}{t+C}$ </br> t:温度[degree],P:蒸気圧[mmHg]')

    def create_antoine_params(self, sort=False,temp=100):
        
        antoine_dict = {}
        
        for comp in self.components:
            
            if comp in self.databank.keys():
                antoine_dict[comp] = self.databank[comp]
            else:
                A = float(input(f'enter antoine param A of {comp}'))
                B = float(input(f'enter antoine param B of {comp}'))
                C = float(input(f'enter antoine param C of {comp}'))
                antoine_dict[comp] = (A,B,C)

        self._calc_flag = True
        self.antoine_dict = antoine_dict.copy()

        if sort==False:
            return antoine_dict
        elif sort==True:
            P = {}
            for comp in self.components:

                A, B, C = antoine_dict[comp]            
                P[comp] = 10**(A - B/(temp+C))

            sorted_P = sorted(P.items(), key=lambda x: x[1], reverse=True)

            sorted_antoine_list = []
            for i in range(len(P)):
                comp = sorted_P[i][0]
                sorted_antoine_list.append([comp, antoine_dict[comp]])

            return sorted_antoine_list
        
    def calc_pressure(self, temp=100, show=False, comp_dict=None, init_comp_using=True):
        """
        comp_dict に変数を入力しても、instance時にcomp_dictを入力した場合には、そちらが優先される。
        instance時に入力した値を使用したくない場合は、init_comp_using=Falseとする。
        """
        if self._calc_flag == False:
             self.create_antoine_params()
        
        if init_comp_using == True:
            comp_dict = self.comp_dict
            comp_list = self.components
        
        P = {}
        for comp in self.components:
            A, B, C = self.antoine_dict[comp]
            if comp_dict is None:
                P[comp] = 10**(A - B/(temp+C))
            else:
                P[comp] = 10**(A - B/(temp+C)) * comp_dict[comp]
            
        if show == True:
            print(f"Vapor pressure at {temp} degree C")
            for comp in self.components:
                print(f" {comp}: {P[comp]:.2f} mmHg")
            print()
            
        return P
    
    def calc_temperature(self, pressure=760, temp=50, iteration=1000, error = 0.05, epsilon=0.0001, comp_dict=None, init_comp_using=True):
        
        if self._calc_flag == False:
            self.create_antoine_params()        
        
        n = 0
        while n < iteration:
            n += 1
            P = self.calc_pressure(temp=temp, comp_dict=comp_dict, init_comp_using=init_comp_using)
            solution = sum(P.values())
            if abs(solution - pressure) < error:
                return temp
            else:
                P = self.calc_pressure(temp=temp+epsilon, comp_dict=comp_dict, init_comp_using=init_comp_using)
                P_plus = sum(P.values())
                
                P = self.calc_pressure(temp=temp-epsilon, comp_dict=comp_dict, init_comp_using=init_comp_using)
                P_minus = sum(P.values())
                diff = (P_plus - P_minus) / (2*epsilon)
                temp -= (solution - pressure) / diff

        raise Exception("Can't solve this problem")
    
    def data_to_csv(self, filename):
        
        labels = ['component', 'params']
        with open(filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=labels)
            writer.writeheader()
            for k, v in self.databank.items():
                writer.writerow({'component': k, 'params': v})
            
            
                
class Wilson(object):
    
    def __init__(self, lambda_array=None):
        
        self.lambda_array = lambda_array
        self.gamma_array = None
    
    def equation(self):
        print(r"$\ln{\gamma_1}=-\ln(x_1+\Lambda_{12}x_2)+x_2[\frac{\Lambda_{12}}{x_1+\Lambda_{12}x_2}-\frac{\Lambda_{21}}{\Lambda_{21}x_1+x_2}]$  $\ln{\gamma_2}=-\ln(x_2+\Lambda_{21}x_1)-x_1[\frac{\Lambda_{12}}{x_1+\Lambda_{12}x_2}-\frac{\Lambda_{21}}{\Lambda_{21}x_1+x_2}]$")
        
    def equation_multi(self):
        print(r"$\ln{\gamma_k}=-\ln[\Sigma^{N}_{j=1}x_j\Lambda_{kj}]+1-\Sigma^{N}_{i=1} \frac{x_i\Lambda_{ik}}{\Sigma^{N}_{j=1}x_j\Lambda_{ij}}$")
    
    def calc(self, x_array):
        N = len(x_array)
        x = x_array.copy()
        x = x / x.sum()
        gamma_array = np.ones(N)
        
        if self.lambda_array is None:
            self.gamma_array = gamma_array
            return gamma_array
        
        A = self.lambda_array.copy()
        
        for k in range(N):
            first = 0
            for j in range(N):
                first += x[j]*A[k, j]
            
            third = 0
            for i in range(N):
                denominator = 0
                for j in range(N):
                    denominator += x[j] * A[i, j]
                third += (x[i]*A[i, k]) / denominator
            
            gamma_array[k] = np.exp(-np.log(first) + 1 - third)
        
        self.gamma_array = gamma_array
        
        return gamma_array
    
    def binary(self, first_component=0, second_component=1, x1_array=None, graph=True):
        
        if x1_array is None:
            x1_array = np.linspace(0, 1, 100)
        A12 = self.lambda_array[first_component, second_component]
        A21 = self.lambda_array[second_component, first_component]
        
        r1_list = []
        r2_list = []
        
        for x1 in x1_array:
            x2 = 1 - x1
            ln_r1 = - np.log(x1 + A12 * x2) + x2 * ( A12/(x1+A12*x2) - A21/(A21*x1+x2) )
            ln_r2 = - np.log(x2 + A21 * x1) - x1 * ( A12/(x1+A12*x2) - A21/(A21*x1+x2) )
            r1_list.append(np.exp(ln_r1))
            r2_list.append(np.exp(ln_r2))

        r1_array = np.array(r1_list)
        r2_array = np.array(r2_list)
        divide_r1_by_r2 = r1_array / r2_array
        
        area_A = np.log(divide_r1_by_r2[np.log(divide_r1_by_r2) >= 0]).sum()
        area_B = np.log(divide_r1_by_r2[np.log(divide_r1_by_r2) < 0]).sum()
        divide_A_by_B = area_A / (-1*area_B)
        
        I = np.sum(np.log(divide_r1_by_r2))
        D = 100 * I / (np.abs(area_A) + np.abs(area_B))
        
        ## for debag
        # print(f'I = {I:.3f}')
        # print(f'area_A = {area_A:.3f}')
        # print(f'area_B = {area_B:.3f}')

        if graph == False:
            print(f'D = {D:.3f}')
        elif graph == True:
            fig, ax = plt.subplots(1,2, figsize=(12, 4.5), sharex=True)

            i = 0
            ax[i].plot(x1_array, r1_list, c='blue', label='r1')
            ax[i].plot(x1_array, r2_list, c='indianred', label='r2')
            ax[i].axvline(x=0.5, color='black', ls='--', lw=1, alpha=0.3)
            ax[i].set_xlabel('x1')
            ax[i].set_ylabel('r1, r2')
            ax[i].set_title('x1 vs. r1/r2', size=16)
            ax[i].grid(alpha=0.5)
            ax[i].legend(loc='best')

            i = 1
            ax[i].plot(x1_array, np.log(divide_r1_by_r2))
            ax[i].axhline(y=0, color='black', lw=1)
            ax[i].set_xlabel('x1')
            ax[i].set_ylabel('ln(r1/r2)')
            ax[i].set_title('x1 vs. ln(r1/r2)')
            ax[i].grid(alpha=0.5)
            
            fig.text(0.8, 0.9, f'D = {D:.3f}', size=15, color='indianred')

            plt.show()
        
        return x1_array, r1_list, r2_list