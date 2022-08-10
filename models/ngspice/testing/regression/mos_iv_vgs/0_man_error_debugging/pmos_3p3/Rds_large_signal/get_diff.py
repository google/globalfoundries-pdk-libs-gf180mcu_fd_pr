import pandas as pd

measured  = pd.read_csv('0_measured_W10_L10.0.csv')
simulated = pd.read_csv('0_simulated_W10_L10.0.csv')

error_1 = round (100 * (abs(measured.iloc[:, 1]) - abs(simulated.iloc[:, 1]))/abs(measured.iloc[:, 1]),6)  
error_2 = round (100 * (abs(measured.iloc[:, 2]) - abs(simulated.iloc[:, 2]))/abs(measured.iloc[:, 2]),6)
error_3 = round (100 * (abs(measured.iloc[:, 3]) - abs(simulated.iloc[:, 3]))/abs(measured.iloc[:, 3]),6) 
error_4 = round (100 * (abs(measured.iloc[:, 4]) - abs(simulated.iloc[:, 4]))/abs(measured.iloc[:, 4]),6) 
error_5 = round (100 * (abs(measured.iloc[:, 5]) - abs(simulated.iloc[:, 5]))/abs(measured.iloc[:, 5]),6) 
error_6 = round (100 * (abs(measured.iloc[:, 6]) - abs(simulated.iloc[:, 6]))/abs(measured.iloc[:, 6]),6) 

df = pd.DataFrame(data=[error_1,error_2,error_3,error_4,error_5,error_6]).transpose()
df.to_csv("diff_table.csv")