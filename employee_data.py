#import the libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#load the data
def load_data(file_path):
    return pd.read_excel(file_path, engine="openpyxl")

#info about the data
def info_about_data (df):
    print(df.info())
    print("\nShape of the data:\n", df.shape)
    print("\nData type:\n", df.dtypes)
    print("\nMissing values:\n", df.isnull().sum())
    print("\nUnique values:\n", df.nunique())
    print("\nDuplicate Rows:\n", df.duplicated().sum())

#fill exit date
def fill_exit_date(df):
    """Fill missing Exit Dates based on Hire Date, Age, and retirement age (55 for females, 60 for males)."""
    df["Hire Date"] = pd.to_datetime(df["Hire Date"], errors='coerce')
    df["Exit Date"] = pd.to_datetime(df["Exit Date"], errors='coerce')
    df["Age"] = pd.to_numeric(df["Age"], errors='coerce')
    df["Gender"] = df["Gender"].str.strip().str.lower()

    # Define retirement ages
    retirement_ages = {"male": 60, "female": 55}

    # Identify rows where Exit Date is missing
    missing_exit = df["Exit Date"].isna()
    
    # Ensure only rows with valid Age and Gender are updated
    valid_age = df.loc[missing_exit, "Age"].notna()
    valid_gender = df.loc[missing_exit, "Gender"].isin(retirement_ages)

    # Calculate estimated exit date for missing values only
    def calculate_exit_date(row):
        retirement_age = retirement_ages[row["Gender"]]
        return row["Hire Date"] + pd.DateOffset(years=(retirement_age - row["Age"]))

    # Apply filling only where Exit Date was originally missing
    df.loc[missing_exit & valid_age & valid_gender, "Exit Date"] = df.loc[
        missing_exit & valid_age & valid_gender
    ].apply(calculate_exit_date, axis=1)

    return df

#clean the data
def clean_data(df):
    df.drop_duplicates(inplace=True)
    df["Full Name"].fillna("Not Provided", inplace=True)
    df["Country"].fillna("Not Provided", inplace=True)
    df["Gender"].fillna(df["Gender"].mode()[0] if not df["Gender"].mode().empty else "Not Provided", inplace=True)
    df["Job Title"].fillna(df.groupby("Department")["Job Title"].transform(lambda x: x.mode()[0] if not x.mode().empty else "Unknown"), inplace=True)
    df["Department"].fillna(df["Department"].mode()[0] if not df["Department"].mode().empty else "Not Assigned", inplace=True)
     # Fill missing ethnicity based on country
    for x in df.index:
        if pd.isna(df.loc[x, "Ethnicity"]) or str(df.loc[x, "Ethnicity"]).strip() == "":
            if df.loc[x, "Country"] == "China":
                df.loc[x, "Ethnicity"] = "Asian"
            elif df.loc[x, "Country"] == "Brazil":
                df.loc[x, "Ethnicity"] = "Latino"
            else:
                df.loc[x, "Ethnicity"] = "Not Provided"
    df["Age"].fillna(df["Age"].median(), inplace=True)
    df["Annual Salary"].fillna(df.groupby("Job Title")["Annual Salary"].transform(lambda x: x.median()), inplace=True)
    df["Bonus %"].fillna(df["Bonus %"].mean(), inplace=True)
    # Fill missing Hire Date with the earliest recorded date
    earliest_hire_date = df["Hire Date"].min()
    df["Hire Date"].fillna(earliest_hire_date, inplace=True)  
    # Fill missing cities based on country and ethnicity using a loop
    for x in df.index:
        if pd.isna(df.loc[x, "City"]) or str(df.loc[x, "City"]).strip() == "":
            if df.loc[x, "Country"] == "United States" and df.loc[x, "Ethnicity"] == "Caucasian":
                df.loc[x, "City"] = df["City"].mode()[0]
            else:
                df.loc[x, "City"] = "Not Provided"          
    df = fill_exit_date(df)
    return df

#modify the first five rows 
def modify_first_five_rows(df):
    sample_data = [
        ["Alice Johnson", "Software Engineer", "IT", 30, 120000],
        ["Bob Smith", "Data Scientist", "IT", 35, 135000],
        ["Charlie Brown", "Marketing Manager", "Marketing", 40, 95000],
        ["Diana Prince", "HR Specialist", "HR", 32, 85000],
        ["Ethan Hunt", "Sales Executive", "Sales", 45, 110000],
    ] 
    df.loc[:4, ["Full Name", "Job Title", "Department", "Age", "Annual Salary"]] = sample_data
    return df

#analyez for data
def analyze_data(df):
    max_salary = df["Annual Salary"].max()
    highest_salary_row = df[df["Annual Salary"] == max_salary]
    grouped_dept = df.groupby("Department")[["Age", "Annual Salary"]].mean()
    grouped_dept_ethnicity = df.groupby(["Department", "Ethnicity"])[["Age", "Annual Salary"]].agg(["max", "min", "median"])
    return highest_salary_row, grouped_dept, grouped_dept_ethnicity

#save the data in excle file 
def save_data(df,file_path):
    df.to_excel(file_path,index=False)

#the excute for the code 
file_path=r"C:\Users\user\Downloads\Employee Sample Data - A.xlsx"
df=load_data(file_path)
info_about_data(df)
df=clean_data(df)
info_about_data(df)
df=modify_first_five_rows(df)
highest_salary, grouped_dept, grouped_dept_ethnicity = analyze_data(df)
output_path = "Processed_Employee_Data.xlsx"
save_data(df, output_path)
print("Highest Salary Employee:\n", highest_salary)
print("\nAverage Age & Salary per Department:\n", grouped_dept)
print("\nDepartment + Ethnicity Analysis:\n", grouped_dept_ethnicity)
print("\nProcessed data saved to:", output_path)