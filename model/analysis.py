from fitparse import FitFile
import gzip
import shutil
import matplotlib.pyplot as plt
import os

def Average(lst):
    return sum(lst) / len(lst)

heart_rate = []
avg_HR = []
timestamp = []
flag = 0
counter = 0

director = os.fsencode(r"\Users\henry\PycharmProjects\pythonProject2")

for file in os.listdir(r"\Users\henry\PycharmProjects\pythonProject2"):
    filename = os.fsdecode(file)
    if filename.endswith(".FIT.gz") or filename.endswith(".fit.gz"):
        print("fit file found")
        fit_filename = filename[:-6]
        fit_filename += "fit"
        print(filename)
        with gzip.open(str(filename), 'rb') as f_in:
            with open(str(fit_filename), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                flag = 0

        fit_file = FitFile(fit_filename)

        for record in fit_file.get_messages("record"):
            # Records can contain multiple pieces of data (ex: timestamp, latitude, longitude, etc)
            for data in record:
                # Print the name and value of the data (and the units if it has any)
                if data.name == 'heart_rate':
                    heart_rate.append(data.value)
                if data.name == 'timestamp' and flag == 0:
                    timestamp.append(data.value)
                    flag = 1
                    counter += 1
        if sum(heart_rate)>1:
            AverageHR = Average(heart_rate)
            avg_HR.append(AverageHR)

        else:
            avg_HR.append(0)

print(avg_HR)

benchmark = 198

intensity = []
for x in avg_HR:
    intensity.append(x/benchmark)
print(timestamp)
print(intensity)



