import pandas as pd

casualty_data = pd.read_csv('corrected_version.csv')

filtered_casualties = casualty_data[
    (casualty_data['age_band_of_casualty'] == "Nov-15") | #11-15
    (casualty_data['age_band_of_casualty'] == "06-Oct") #6-10
]

casualty_data['age_band_of_casualty'] = casualty_data['age_band_of_casualty'].replace("Nov-15", "11-15")
casualty_data['age_band_of_casualty'] = casualty_data['age_band_of_casualty'].replace("06-Oct", "06-10")

#print(len(filtered_casualties))

casualty_data.to_csv("2016_2022_dataset.csv", index=False)
