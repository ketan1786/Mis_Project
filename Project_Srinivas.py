#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 00:09:40 2024

@author: jashwanthsrinivas
"""

import pandas as pd

# Paths to the primary .txt files
sales_file_path = "sales.txt"
timesheet_file_path = "timesheet.txt"
evaluation_file_path = "evaluation.txt"
emp_beg_yr_file_path = "emp_beg_yr.txt"

# Helper function to trim whitespace in DataFrame
def trim_whitespace(data):
    """
    Trims whitespace from string columns in a DataFrame.
    """
    for col in data.select_dtypes(include=["object"]).columns:
        data[col] = data[col].str.strip()
    return data

# Clean and process the data
def clean_data(data, numeric_columns=[]):
    """
    Cleans a DataFrame by removing duplicates, trimming whitespace,
    and converting specified columns to numeric.
    """
    data = data.drop_duplicates()  # Remove duplicates
    data = trim_whitespace(data)  # Trim whitespace
    for col in numeric_columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")  # Convert to numeric
    return data

# Loading the primary .txt files into DataFrames
sales_data = pd.read_csv(sales_file_path, header=None, names=["EmployeeID", "Sales"])
timesheet_data = pd.read_csv(timesheet_file_path, header=None, names=["EmployeeID", "HoursWorked"])
evaluation_data = pd.read_csv(evaluation_file_path, header=None, sep="#", names=["EmployeeID", "Comments"])
emp_data = pd.read_csv(emp_beg_yr_file_path)

# Cleaning the datasets
sales_data = clean_data(sales_data, numeric_columns=["EmployeeID", "Sales"])
timesheet_data = clean_data(timesheet_data, numeric_columns=["EmployeeID", "HoursWorked"])
evaluation_data = clean_data(evaluation_data)  # Comments are not numeric
emp_data = clean_data(emp_data, numeric_columns=["ID", "BasePay"])

# Cross-check Employee IDs against emp_beg_yr.txt and log errors
valid_employee_ids = set(emp_data["ID"])
errors = []

def validate_ids(data, id_column, file_name):
    """
    Validates that all Employee IDs in a DataFrame exist in emp_data.
    Logs errors for unrecognized IDs.
    """
    invalid_ids = data[~data[id_column].isin(valid_employee_ids)]
    if not invalid_ids.empty:
        for idx in invalid_ids[id_column]:
            errors.append(f"{idx} in {file_name}")
    return data[data[id_column].isin(valid_employee_ids)]

# Validating Employee IDs in all files
sales_data = validate_ids(sales_data, "EmployeeID", "sales.txt")
timesheet_data = validate_ids(timesheet_data, "EmployeeID", "timesheet.txt")
evaluation_data = validate_ids(evaluation_data, "EmployeeID", "evaluation.txt")

# Log all errors to a temporary error log
error_log_path = "error.txt"  # Adjust path as needed
with open(error_log_path, "w") as error_log:
    error_log.write("Error Log\n")
    for error in errors:
        error_log.write(f"{error}\n")

# Displaying cleaned data for verification
print("\nCleaned Sales Data:\n", sales_data.head())
print("\nCleaned Timesheet Data:\n", timesheet_data.head())
print("\nCleaned Evaluation Data:\n", evaluation_data.head())
print("\nCleaned Employee Data:\n", emp_data.head())

# Calculate Utilization Rates
def calculate_utilization(timesheet_data):
    """
    Calculates utilization rates for employees using the formula:
    Utilization Rate = (Total Hours Worked / 2250) * 100
    """
    total_hours = timesheet_data.groupby("EmployeeID")["HoursWorked"].sum()  # Total hours worked by employee
    utilization_rate = (total_hours / 2250) * 100  # Calculate utilization rate
    utilization_rate = utilization_rate.round(2)  # Round to two decimal places
    return utilization_rate

utilization_rates = calculate_utilization(timesheet_data)

# Merge utilization rates into the employee data
emp_data = emp_data.set_index("ID")
emp_data["UtilizationRate"] = utilization_rates
emp_data["UtilizationRate"] = emp_data["UtilizationRate"].fillna(0)  # Fill NaN with 0 for employees without timesheet entries

# Save employee data with utilization rates
utilization_output_path = "Employee_Data_With_Utilization.csv"
emp_data.to_csv(utilization_output_path)
print(f"\nUtilization data saved to: {utilization_output_path}")

# Define keywords for evaluation metrics
positive_keywords = ["excellent", "good", "dependable", "prompt"]
negative_keywords = ["poor", "error", "unreliable", "late"]

def calculate_evaluation_score(evaluation_data):
    """
    Calculates qualitative evaluation scores based on positive and negative keywords.
    Rules:
    - Score = (# of positive keywords) / (# of negative keywords)
    - If no keywords are found, score is 1.
    - If no negative keywords are found, score is 10.
    """
    scores = []
    for _, row in evaluation_data.iterrows():
        comments = row["Comments"].lower()
        positive_count = sum(comments.count(word) for word in positive_keywords)
        negative_count = sum(comments.count(word) for word in negative_keywords)

        if positive_count == 0 and negative_count == 0:
            score = 1
        elif negative_count == 0:
            score = 10
        else:
            score = round(positive_count / negative_count, 1)
        scores.append(score)
    evaluation_data["EvaluationScore"] = scores
    return evaluation_data

# Calculate evaluation scores
evaluation_data = calculate_evaluation_score(evaluation_data)

# Merge evaluation scores into employee data (only for Consultants)
evaluation_scores = evaluation_data.set_index("EmployeeID")["EvaluationScore"]
emp_data["EvaluationScore"] = emp_data.index.map(evaluation_scores).fillna(0)

# Save employee data with evaluation scores
evaluation_output_path = "Employee_Data_With_Evaluation.csv"
emp_data.to_csv(evaluation_output_path)
print(f"\nEvaluation data saved to: {evaluation_output_path}")

