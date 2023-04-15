#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import argparse


QUERY = """
            SELECT DATETIME(ROUND(t1.timestamp / 1000), 'unixepoch') AS date_column, 
            t2.name  AS category, 
            t1.debit / 100 AS amount
            FROM TransactionItem AS t1 
            JOIN Category AS t2 
            ON t1.categoryId = t2.id
        """


def parseDBFile():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--dbfile', type=str, help='The path to expense manager backup db file')
    args = parser.parse_args()
    backupDBFile = args.dbfile
    return backupDBFile

def initDBAndCreateDF(backupDBFile):
    """
    Initializes the db and create the dataframe
    """
    conn = sqlite3.connect(backupDBFile)
    df = pd.read_sql(QUERY, conn)
    df['date_column'] = pd.to_datetime(df['date_column'], format='%Y-%m-%d')
    return df


"""
This function is generated by ChatGPT
"""
def exportLineChartFromDF(df):
    # Group the data by month and category using the pd.Grouper function
    monthly_grouped = df.groupby([pd.Grouper(key='date_column', freq='M'), 'category'])

    # Sum the values in the 'amount' column for each group
    monthly_summed = monthly_grouped['amount'].sum()

    # Reset the index of the resulting DataFrame
    monthly_summed = monthly_summed.reset_index()

    # Group the data by category and sum the values in the 'amount' column
    category_sums = monthly_summed.groupby('category')['amount'].sum()

    # Convert the resulting Series to a DataFrame and rename the column
    category_sums = category_sums.to_frame().reset_index().rename(columns={'amount': 'total_amount'})

    # Merge the sums into the original DataFrame
    monthly_summed = monthly_summed.merge(category_sums, on='category')

    # Pivot the DataFrame to get the total amount in each category for each month
    pivoted = monthly_summed.pivot(index='date_column', columns='category', values='amount')

    # Add a 'total_amount' column to the pivoted DataFrame
    pivoted['total_amount'] = pivoted.sum(axis=1)

    # Plot a line chart with the x axis as month and the y axis as total amount
    pivoted['total_amount'].plot(kind='line', marker='o')

    # Open the chart in an image viewer
    plt.show()


def main():
    backupDBFile = parseDBFile()
    df = initDBAndCreateDF(backupDBFile)
    exportLineChartFromDF(df)


if __name__ == "__main__":
    main()
