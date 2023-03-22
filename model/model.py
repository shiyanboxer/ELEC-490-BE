import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import math
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import csv
from sklearn.metrics import accuracy_score
import pickle

def training_data(file_name):
    data_frame = pd.read_csv(file_name)
    data_array = data_frame.values

    date_array = []

    day_1 = data_array[0,0]
    final_day = data_array[len(data_array)-1,0]
    d1 = datetime.strptime(day_1, "%Y-%m-%d")
    d2 = datetime.strptime(final_day, "%Y-%m-%d")
    date_array.append(d1)
    time_delta = d2-d1

    power_benchmark = 247
    HR_benchmark = 220


    delta = d2 - d1
    date_array = [d1 + timedelta(days=i) for i in range(delta.days + 1)]



    intensity = [0]*len(date_array)


    i_counter = -1
    j_counter = -1
    power_benchmark = 247
    HR_benchmark = 220

    for i in range(len(date_array)):
        i_counter += 1
        for j in range(len(data_array)):
            j_counter +=1
            temp_date = datetime.strptime(data_array[j,0], "%Y-%m-%d")
            if date_array[i] == temp_date:
                intensity[i] = (data_array[j,1]*data_array[j,2])/power_benchmark
                temp_intensity = intensity[i]
                if math.isnan(temp_intensity) == True:
                    intensity[i] = (data_array[j, 3] * data_array[j, 2]) / HR_benchmark





    p_intercept = 0

    g_scaling = 1
    h_scaling = 1

    g_decay = 30
    h_decay = 10

    form = [0]*366
    sum_valFIT = 0
    sum_valFAT = 0

    for i in range(len(intensity)):
        sum_upperLIM = i
        print(sum_upperLIM)
        for j in range(sum_upperLIM):
            temp_intensity= intensity[j]
            if math.isnan(temp_intensity) == False:
                e_valFIT = math.exp((-(i-j)/g_decay))
                sum_valFIT += temp_intensity*e_valFIT

                e_valFAT = math.exp((-(i - j) / h_decay))
                sum_valFAT += temp_intensity * e_valFAT

        temp_form = p_intercept + (g_scaling*sum_valFIT)-(h_scaling*sum_valFAT)
        sum_valFAT=0
        sum_valFIT=0
        form[i] =temp_form

    return form


def find_two_max_points(data):
    # Initialize variables to hold the indices of the two maximum points
    max1_index = max2_index = 0

    # Iterate through the data and update the maximum points accordingly
    for i, value in enumerate(data):
        if value > data[max1_index]:
            max2_index = max1_index
            max1_index = i
        elif value > data[max2_index]:
            max2_index = i

    # Return the indices of the two maximum points
    return max1_index, max2_index

def shift_curve(data, shift):
    """
    Shifts a curve by a specified number of points.

    Parameters:
    data (numpy.ndarray): The input dataset, where the indices correspond to the x-axis component.
    shift (int): The number of points to shift the curve.

    Returns:
    numpy.ndarray: The shifted dataset.
    """
    shifted_data = np.roll(data, shift)
    return shifted_data

def normalize_lists(form1, form2, form3, form4):
    # Normalize form1 so that its maximum value is 1
    max_val = max(form1)
    if max_val > 0:
        for i in range(len(form1)):
            form1[i] = form1[i] / max_val

    # Normalize form2 so that its maximum value is 1
    max_val = max(form2)
    if max_val > 0:
        for i in range(len(form2)):
            form2[i] = form2[i] / max_val

    # Normalize form3 so that its maximum value is 1
    max_val = max(form3)
    if max_val > 0:
        for i in range(len(form3)):
            form3[i] = form3[i] / max_val

    # Normalize form4 so that its maximum value is 1
    max_val = max(form4)
    if max_val > 0:
        for i in range(len(form4)):
            form4[i] = form4[i] / max_val

    return form1, form2, form3, form4


def save_form_data_to_csv(form1, form2, form3, form4):
    # Create a list of tuples with the form data
    data = [(i, form1[i], form2[i], form3[i], form4[i]) for i in range(len(form1))]

    # Write the data to a CSV file
    with open('formdata.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Index', 'Form1', 'Form2', 'Form3', 'Form4'])
        writer.writerows(data)

form1 = training_data('Emma20-21.csv')
form2 = training_data('Emma21-22.csv')
form3 = training_data('Jack20-21.csv')
form4 = training_data('Jack21-22.csv')

plt.plot(form1, label = 'Form1')
plt.plot(form2, label = 'Form2')
plt.plot(form3, label = 'Form3')
plt.plot(form4, label = 'Form4')

# Add labels and a title
plt.xlabel('Day of the year')
plt.ylabel('Form')
plt.title('Raw data for the form regression model')

# Show the plot
plt.legend()
plt.show()
y_reg = np.arange(0,366)

form1_max1, form1_max2 = find_two_max_points(form1)
form2_max1, form2_max2 = find_two_max_points(form2)
form3_max1, form3_max2 = find_two_max_points(form3)
form4_max1, form4_max2 = find_two_max_points(form4)

form1_diff = 250 - form1_max2
form2_diff = 250 - form2_max2
form3_diff = 250 - form3_max2
form4_diff = 250 - form4_max2

form1 = shift_curve(form1, form1_diff)
form2 = shift_curve(form2, form1_diff)
form3 = shift_curve(form3, form1_diff)
form4 = shift_curve(form4, form1_diff)



form1, form2, form3, form4 = normalize_lists(form1, form2, form3, form4)


plt.plot(form1, label = 'Form1')
plt.plot(form2, label = 'Form2')
plt.plot(form3, label = 'Form3')
plt.plot(form4, label = 'Form4')

save_form_data_to_csv(form1, form2, form3, form4)

#plt.plot(form1, label = 'Form1')
#plt.plot(form2, label = 'Form2')
#plt.plot(form3, label = 'Form3')
#plt.plot(form4, label = 'Form4')

# Add labels and a title
plt.xlabel('Day of the year')
plt.ylabel('Form')
plt.title('Cleaned Data')

# Show the plot
plt.legend()
plt.show()
y_reg = np.arange(0,366)

counter = 0
training_form = np.empty([366,2])

for i in range(366):
    training_form[counter,0]= form1[i]
    training_form[counter, 1] = i
    counter += 1

    #training_form[counter,0]= form2[i]
    #training_form[counter, 1] = i
    #counter += 1

    #training_form[counter,0]= form3[i]
    #training_form[counter, 1] = i
    #counter += 1

    #training_form[counter,0]= form4[i]
    #training_form[counter, 1] = i
    #counter += 1

# Extract the x and y values from the training data set
x = training_form[:, 1].reshape(-1, 1)
y = training_form[:, 0].reshape(-1, 1)

# Create polynomial features with degree 2
poly = PolynomialFeatures(degree=8)
X = poly.fit_transform(x)

# Train the model
reg = LinearRegression().fit(X, y)

# Get the coefficients of the linear regression model
coeffs = reg.coef_[0]
intercept = reg.intercept_[0]

# Form the equation of the regression function
equation = "y = {:.100f}".format(intercept)
for i in range(len(coeffs)):
    equation += " + {:.100f}*x^{}".format(coeffs[i], i+1)

# Print the equation
print("Regression function equation:", equation)

# Plot the regression line
X_new = poly.fit_transform(x)
y_pred = reg.predict(X_new)
plt.scatter(x, y, color='red')
plt.plot(x, y_pred, color='blue')
plt.show()

# Test accuracy - TODO
# accuracy_score(y_test, np.around(model.predict(X_test),0))

# Pickle the model so it can be loaded in the Flask API
pickl = {'model': reg.fit(x, y)}
pickle.dump( pickl, open( 'model_file' + ".p", "wb" ) )

file_name = "model_file.p"
with open(file_name, 'rb') as pickled:
    data = pickle.load(pickled)
    model = data['model']

