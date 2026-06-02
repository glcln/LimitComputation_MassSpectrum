rates = [0.00147992,0.000159354,1.76729e-5,1.80017e-6,1.9e-7]
#rates = [0.000451036,4.7749E-5,5.34376E-6,5.45292E-7,5.2E-8]

def linear_normalization_factor(y_value):
    y_values = [3000, 4000, 5000, 6000, 7000]

    y_value = min(max(y_value, min(y_values)), max(y_values))
    lower_y = max(filter(lambda y: y <= y_value, y_values))
    upper_y = min(filter(lambda y: y >= y_value, y_values))

    if lower_y != upper_y:
        factor = rates[y_values.index(lower_y)] + (rates[y_values.index(upper_y)] - rates[y_values.index(lower_y)]) * (y_value - lower_y) / (upper_y - lower_y)
        return factor
    else:
        return rates[y_values.index(lower_y)]

y_value_to_normalize = 4500
normalization_factor = linear_normalization_factor(y_value_to_normalize)

normalization_factor2 = linear_normalization_factor(5500)
normalization_factor3 = linear_normalization_factor(6500)

print("Normalisation for 4000 :",rates[1]*10000)
print("Normalisation for 4500 :",normalization_factor*10000)
print("Normalisation for 5000 :",rates[2]*10000)

print("Normalisation for 5000 :",rates[2]*10000)
print("Normalisation for 5500 :",normalization_factor2*10000)
print("Normalisation for 6000 :",rates[3]*10000)


print("Normalisation for 6000 :",rates[3]*10000)
print("Normalisation for 6500 :",normalization_factor3*10000)
print("Normalisation for 7000 :",rates[4]*10000)

