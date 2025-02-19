import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import logging
from tkinter import *
from tkinter import messagebox
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.ticker as ticker
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import cx_Oracle
import pandas as pd
import time
from PIL import Image, ImageTk
import sys
import os

# For drawer
drawerX = -500
drawerState= 0

def fetchdata():
    try:
        # Establish database connection
        dsn = cx_Oracle.makedsn("192.168.4.41", "1521", service_name="nerp")

        connection = cx_Oracle.connect(user="plstatusbkp", password="plstatusbkp2022", dsn=dsn)
        print("Connected to Oracle Database")

        # Create a cursor
        cursor = connection.cursor()

        # Execute a SQL query
        sql_query = '''
            SELECT * FROM V_PLANT_PROD 
            ORDER BY 1 DESC FETCH FIRST 365 ROWS ONLY
        '''
        #sql_query = "SELECT * FROM V_PLANT_PROD"
        cursor.execute(sql_query)

        # Fetch all rows from the executed query
        #columns = ['Production Date', 'Hot Metal', 'Crude Steel', 'Saleable Steel']
        rows = cursor.fetchall()
        rawDf = pd.DataFrame(rows)
        print(rawDf)

        # Sort the DataFrame by 'Production Date' in descending order
        #df = rawDf.sort_values(by='Production Date', ascending=True)

        # Ensure the 'Production Date' column is in datetime format
        #df['Production Date'] = pd.to_datetime(df['Production Date'])

    except cx_Oracle.DatabaseError as e:
        print("There was a problem connecting to the Oracle database:", e)
        logging.error("Database connection error: %s", e)
        messagebox.showerror("Database Error", f"Could not connect to database:\n{e}")
        rawDf = pd.DataFrame()
        df = pd.DataFrame()

    finally:
        try:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                print("Connection closed.")
                return df
        except Exception as ex:
            print("Error while closing database connection:", ex)
            logging.error("Error while closing database connection: %s", ex)
            
fetchdata()