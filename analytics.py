import pandas as pd 

def analytics_v4():

    df = pd.read_csv('./version_4_full.csv')

 
    if 'Class' in df.columns:

       
        class_counts = df['Class'].value_counts().to_dict()

        # Print the results
        print("Class : Total Requests\n\n")
        for class_name, count in class_counts.items():
            print(f'"{class_name}": {count}')
        

    else:
        print("Error: 'Class' column not found in the CSV file.")

