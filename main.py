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
from PIL import Image, ImageTk


# For drawer
drawerX = -500
drawerState= 0
# For the new data from the submit function
submittedData = None

def fetchdata():
    try:
        # Establish database connection
        dsn = cx_Oracle.makedsn("192.168.4.41", "1521", service_name="nerp")

        connection = cx_Oracle.connect(user="plstatusbkp", password="plstatusbkp2022", dsn=dsn)
        print("Connected to Oracle Database")

        # Create a cursor
        cursor = connection.cursor()

        # Execute a SQL query
        #sql_query = "SELECT * FROM V_PLANT_PROD"
        sql_query = '''
            SELECT * FROM V_PLANT_PROD 
            ORDER BY 1 DESC FETCH FIRST 365 ROWS ONLY
        '''
        cursor.execute(sql_query)

        # Fetch all rows from the executed query
        columns = ['Production Date', 'Hot Metal', 'Crude Steel', 'Saleable Steel']
        rows = cursor.fetchall()
        rawDf = pd.DataFrame(rows, columns=columns)

        # Sort the DataFrame by 'Production Date' in descending order
        df = rawDf.sort_values(by='Production Date', ascending=True)

        # Ensure the 'Production Date' column is in datetime format
        df['Production Date'] = pd.to_datetime(df['Production Date'])

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
            
# Close App Function
def close_app():
    #confirm = messagebox.askokcancel("Exit", "Are you sure, you want to exit?")
    confirm = 1
    if confirm:
        app.quit() 

df = fetchdata()
date_time = pd.to_datetime(df['Production Date']).dt.strftime('%d-%m-%Y').to_list()
dateTime = pd.Series(df['Production Date']).tail(20).dt.date.to_list()
hotMetal = df['Hot Metal'].tail(20).tolist()
crudeSt = df['Crude Steel'].tail(20).tolist()
salebleSt = df['Saleable Steel'].tail(20).tolist()

def create_responsive_ui():
    # Create the main application window with a theme
    app = ttk.Window(themename="cosmo")
    app.title("Responsive Frames Example")
    app.geometry("1600x900")  # Initial window size
    app.attributes('-fullscreen', True)

    # Configure the grid to make it responsive
    app.columnconfigure(0, weight=1)  # Single column, fills horizontally
    app.columnconfigure(1, weight=1)  # Add column 1 for layout purposes
    app.rowconfigure(0, weight=1)     # Top frame (1 part)
    app.rowconfigure(1, weight=5)     # Bottom frame (5 parts)

    # Create two frames with ttkbootstrap styling
    frame_top = ttk.Frame(app, bootstyle="info")
    frame_bottom = ttk.Frame(app,  bootstyle="info")

    # Place the frames in the grid
    frame_top.grid(row=0, column=0, sticky="nsew", columnspan=2)     # Stretches to fill
    frame_bottom.grid(row=1, column=0, columnspan=2, sticky="nsew") # Stretches to fill

    # Making top frame row column responsive
    frame_top.columnconfigure(0, weight=2)
    frame_top.columnconfigure(1, weight=1)
    frame_top.columnconfigure(2, weight=2)
    frame_top.columnconfigure(3, weight=2)
    frame_top.columnconfigure(4, weight=2)

    frame_top.rowconfigure(0, weight=1)
    frame_top.rowconfigure(1, weight=1)
    frame_top.rowconfigure(2, weight=1)

    frame_drawer = ttk.Frame(frame_bottom, bootstyle="info")
    frame_drawer.columnconfigure(0, weight=1)  # Ensure column expands to fill space

    separatorH1 = ttk.Separator(frame_drawer, orient="horizontal") #For the drawer top white line
    separatorH1.grid(row=0, column=0, sticky="new")

    label = ttk.Label(frame_top, text="     RSP Production Analytics", font=("Helvetica", 32, "bold"), bootstyle="inverse-info")
    label.grid(row=0, column=0, pady=(5, 5), sticky="ew")

    # Drawer Table 
    columns = ('dt', 'hm', 'cs', 'ss')
    dataTable = ttk.Treeview(frame_drawer, height=80, columns=columns, show='headings')
    dataTable.grid(row=0, column=0, pady=5)

    style = ttk.Style()
    style.configure('Custom.Treeview',font=('Arial', 12, 'bold'),background = '#a054bc',rowheight = 36, foreground='white')
    dataTable.configure(style='Custom.Treeview')
    style.configure("Treeview.Heading", 
                    font=("Arial", 11, "bold"), 
                    rowheight = 30,
                    background="green",  # Background color for the headings (set to blue)
                    foreground="white")  # Set heading text color to white
    
    # Create Vertical Scrollbar
    v_scrollbar = ttk.Scrollbar(frame_drawer, orient=VERTICAL, command=dataTable.yview)
    v_scrollbar.grid(row=0, column=1, sticky="ns")

    # Configure column headings
    dataTable.heading('dt', text='Date')
    dataTable.heading('hm', text='Hot Metal')
    dataTable.heading('cs', text='Crude Steel')
    dataTable.heading('ss', text='Saleable Steel')

    #dataTable.column('slNo', width=65, anchor='center')
    dataTable.column('dt', width=94, anchor='center')
    dataTable.column('hm', width=120, anchor='center')
    dataTable.column('cs', width=120, anchor='center')
    dataTable.column('ss', width=120, anchor='center')

    def populate_treeview(dataframe, treeview_widget):
        # Clear existing rows in the Treeview
        for item in treeview_widget.get_children():
            treeview_widget.delete(item)
    
        # Insert new rows into the Treeview
        for index, row in dataframe.iterrows():
            treeview_widget.insert(
                "",
                "end",
                values=(
                    #index + 1,  # Serial Number
                    row['Production Date'],  # Production Date
                    row['Hot Metal'],  # Hot Metal
                    row['Crude Steel'],  # Crude Steel
                    row['Saleable Steel']  # Saleable Steel
                )
            )
    # Fetch data and populate Treeview
    treeDf = df.tail(30)
    if not treeDf.empty:
        #treeDf['Production Date'] = pd.to_datetime(treeDf['Production Date']).dt.strftime('%d-%m-%Y')  # Format date
        treeDf.loc[:, 'Production Date'] = pd.to_datetime(treeDf['Production Date']).dt.strftime('%d-%m-%Y')
        populate_treeview(treeDf, dataTable)
    else:
        print("No data available.")

    #Creating the drawer button
    drawerImage_path = "menuIcon.png"  # Replace with your PNG file path
    image = Image.open(drawerImage_path).resize((30, 25))  # Resize to desired dimensions
    drawerButton_image = ImageTk.PhotoImage(image)

    def drawer_open():
        global drawerX  # Declare drawerX as global to modify it inside the function
        global drawerState
        if drawerState == 0:  # Stop if the drawer is fully opened
            drawerX += 5  # Increment the position by 10 pixels per step
            frame_drawer.place(x=drawerX, y=0, width=500, height=1000)  # Adjust height if necessary
            frame_drawer.lift()
            if drawerX == 0:
                drawerState=1
            else:
                app.after(10, drawer_open)
        else:  # Stop if the drawer is fully opened
            drawerX -= 5  # Increment the position by 10 pixels per step
            frame_drawer.place(x=drawerX, y=0, width=500, height=1000)  # Adjust height if necessary
            frame_drawer.lift()
            if drawerX == -500:
                drawerState=0
            else:
                app.after(10, drawer_open)

    if drawerButton_image:
        image_button = ttk.Button(
            frame_top,
            bootstyle='info',
            takefocus=False,
            image=drawerButton_image,
            command= drawer_open,  # Action when clicked
            text="",
        )
    image_button.grid(row=0, column=4, padx= (0, 40), pady=(5, 5), sticky="e")
    frame_top.image_ref = drawerButton_image

    separatorH = ttk.Separator(frame_top, orient="horizontal")
    separatorH.grid(row=1, column=0, columnspan=5, sticky="new")

    separatorV1 = ttk.Separator(frame_top, orient="vertical")
    separatorV1.grid(row=1, column=1, rowspan=5, padx=(0, 10), sticky="nse")

    def submit():
        global submittedData
        try:
                # Get selected dates from the user inputs
                start_date = startDate_entry.entry.get()
                end_date = endDate_entry.entry.get()
        
                # Convert the selected dates to datetime format
                start_date = pd.to_datetime(start_date, format="%Y-%m-%d", errors="coerce")
                end_date = pd.to_datetime(end_date, format="%Y-%m-%d", errors="coerce")
        
                # Validate the entered dates
                if pd.isna(start_date) or pd.isna(end_date):
                    messagebox.showerror("Invalid Input", "Please enter valid dates in YYYY-MM-DD format.")
                    return
        
                # Ensure the start date is not after the end date
                if start_date > end_date:
                    messagebox.showerror("Invalid Range", "The start date cannot be after the end date.")
                    return
        
                # Ensure the DataFrame's 'Production Date' column is in datetime format
                if 'Production Date' not in df.columns:
                    messagebox.showerror("Missing Column", "'Production Date' column is not found in the data.")
                    return
        
                if not pd.api.types.is_datetime64_any_dtype(df['Production Date']):
                    df['Production Date'] = pd.to_datetime(df['Production Date'], errors='coerce')
        
                # Drop rows with invalid 'Production Date' values
                df.dropna(subset=['Production Date'], inplace=True)
        
                # Filter the data based on the selected date range
                filtered_df = df[(df['Production Date'] >= start_date) & (df['Production Date'] <= end_date)]
        
                if filtered_df.empty:
                    messagebox.showinfo("No Data", "No data available for the selected date range.")
                else:
                    submittedData = filtered_df
                    print(submittedData)
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            logging.error("Error in submit function: %s", e)
        # Add start DateEntry (dropdown calendar)
    startDate_entry = ttk.DateEntry(frame_top, bootstyle=SUCCESS, 
                                    width=20, dateformat="%Y-%m-%d")
    startDate_entry.grid(row=1, column=0, padx=40, pady=(5,0), sticky="w")
    startDate_entry.entry.configure(font=("Arial", 12, "bold"), foreground="#a054bc")

    # Add end DateEntry (dropdown calendar)
    endDate_entry = ttk.DateEntry(frame_top, bootstyle=SUCCESS, 
                                    width=20, dateformat="%Y-%m-%d")
    endDate_entry.grid(row=1, column=0, padx=(80,0), pady=(5,0))
    endDate_entry.entry.configure(font=("Arial", 12, "bold"), foreground="#a054bc")

    # Fetch the main application's background color
    info_background = app.style.colors.get("info")  # Info theme background color
    text_color = app.style.colors.get("light")  # Light text color for contrast

    # Use an existing round checkbutton layout and customize it
    app.style.configure(
        "Custom.Round.Toggle.TCheckbutton",
        font=("Helvetica", 12, "bold"),
        background=info_background,  # Match the app's theme background
        foreground=text_color,       # Text color for readability
        indicatorsize=16, 
        indicatorcolor=info_background,  # Background for indicator
        focuscolor=info_background,  # Focus highlight color
    )

    # Variables for checkbuttons
    var_hotmetal = ttk.IntVar()
    var_crudesteel = ttk.IntVar()
    var_saleablesteel = ttk.IntVar()

    # Hot Metal Checkbutton
    chk_hotmetal = ttk.Checkbutton(
        frame_top,
        text="  Hot Metal",
        variable=var_hotmetal,
        style="Custom.Round.Toggle.TCheckbutton",
        bootstyle="success-round-toggle",
        command=lambda: print("Hot Metal Toggled"),
    )
    chk_hotmetal.grid(row=2, column=0, padx=40, sticky="sw")

    # Crude Steel Checkbutton
    chk_crudesteel = ttk.Checkbutton(
        frame_top,
        text="  Crude Steel",
        variable=var_crudesteel,
        style="Custom.Round.Toggle.TCheckbutton",
        bootstyle="success-round-toggle",
        command=lambda: print("Crude Steel Toggled"),
    )
    chk_crudesteel.grid(row=2, column=0, padx=200, sticky="sw")
    # Saleable Steel Checkbutton
    chk_saleablesteel = ttk.Checkbutton(
        frame_top,
        text="  Saleable Steel",
        variable=var_saleablesteel,
        style="Custom.Round.Toggle.TCheckbutton",
        bootstyle="success-round-toggle",
        command=lambda: print("Saleable Steel Toggled"),
    )
    chk_saleablesteel.grid(row=2, column=0, padx=360, sticky="sw")

    # Function to draw a combined plot
    def drawCombinedPlot(data1=dateTime, data2=hotMetal, 
                            data3=crudeSt, data4=salebleSt, 
                            plotItems=None, frame_bottom=None):
        try:
            # Fallback for None values
            data1 = data1 if data1 is not None else []
            data2 = data2 if data2 is not None else []
            data3 = data3 if data3 is not None else []
            data4 = data4 if data4 is not None else []
            plotItems = plotItems if plotItems else []

            plot_canvases = []  # Initialize the list

            fig = Figure(figsize=(20, 7.8), dpi=100)
            ax = fig.add_subplot(111)
            ax.grid(alpha=0.3)

            # remove the outer figure background and the axes background 
            fig.patch.set_visible(False)
            ax.set_facecolor("none")
            
            fig.subplots_adjust(left= 0.06, right=0.98)

            fig.text(0.8, 0.145, "C&IT", fontsize=80, color= "#9C54BC", alpha= 0.1)
            fig.text(0.8, 0.12, "Rourkela Steel Plant", fontsize=20, color= "#9C54BC", alpha= 0.2)
            

            # Make all spines (borders) invisible
            for spine in ax.spines.values():
                spine.set_visible(False)

            if 'Hot Metal' in plotItems:
                ax.plot(data1, data2, label="Hot Metal", marker='o', color='red', linewidth=0.7, alpha=0.5)
            if 'Crude Steel' in plotItems:
                ax.plot(data1, data3, label="Crude Steel", marker='o', color='green', linewidth=0.7, alpha=0.5)
            if 'Saleable Steel' in plotItems:
                ax.plot(data1, data4, label="Saleable Steel", marker='o', color='blue', linewidth=0.7, alpha=0.5)

            ax.invert_xaxis()

            ax.set_xlabel("Date", fontsize=16,color= "#9C54BC", labelpad=12)
            ax.set_ylabel("Production Quantity", fontsize=16,color= "#9C54BC", labelpad=12)
            # Customize tick labels color
            ax.tick_params(axis='x', colors="#a054bc")  # Change the color of the x-axis (date) ticks
            ax.tick_params(axis='y', colors="#a054bc")

            if plotItems:
                ax.legend(
                fontsize=12,  # Adjust the font size of the legend
                labelcolor="#a054bc",  # Change the text color of the legend labels
                edgecolor="#a054bc"  # Border color of the legend box
            )

            ax.grid(True, which='minor', color= "#9C54BC", linestyle='--', linewidth=0.5, alpha=0.1)
            # To view minor grids
            ax.minorticks_on()

            def reset_home():
                # Reset the axes limits
                ax.set_xlim([None, None])  # Reset x-limits to auto
                ax.set_ylim([None, None])  # Reset y-limits to auto
            
                # Ensure pan and zoom modes are deactivated
                if fig.canvas.manager.toolbar.mode == 'pan':
                    fig.canvas.manager.toolbar.pan()
                if fig.canvas.manager.toolbar.mode == 'zoom rect':
                    fig.canvas.manager.toolbar.zoom()

                fig.canvas.draw()  # Redraw the figure

            # List to store annotations
            annotations = []
            annotation_mode = {"active": False}
            
            def toggle_annotation_mode():
                annotation_mode["active"] = not annotation_mode["active"]
                start_annotation_button["text"] = "Stop Annotation" if annotation_mode["active"] else "Start Annotation"
            
            start_annotation_button = ttk.Button(
                frame_top,
                bootstyle='success-outline',
                text="Start Annotation",
                padding=(30, 5, 30, 5),
                takefocus=False,
                command=toggle_annotation_mode
            )
            start_annotation_button.grid(row=3, column=2, padx=(0, 10), pady=(10, 5), sticky="e")
            
            tooltip = ax.annotate(
                "", 
                xy=(0, 0), 
                xytext=(8, 8), 
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.3", fc="#a054bc", alpha=0.8, edgecolor="green", linewidth=1), 
                fontsize=12, 
                visible=False,  # Hidden by default
                color="#FFFFFF"
            )
            
            def on_click(event):
                if annotation_mode["active"] and event.inaxes == ax:
                    x, y = event.xdata, event.ydata
                    if x is not None and y is not None:
                        readable_date = mdates.num2date(x).strftime("%d-%m-%Y")
                        
                        # Create a new permanent annotation
                        new_annotation = ax.annotate(
                            f"Date: {readable_date}\nValue: {y:.2f}",
                            xy=(x, y),
                            xytext=(8, 8),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round,pad=0.3", fc="#a054bc", alpha=0.8, edgecolor="green", linewidth=1),
                            fontsize=12,
                            color="#FFFFFF"
                        )
                        annotations.append(new_annotation)
                        
                        # Update the tooltip for transient display
                        tooltip.set_text(f"Date: {readable_date}\nValue: {y:.2f}")
                        tooltip.xy = (x, y)
                        # To clear all the annotations all at atime make-: tooltip.set_visible(False)
                        tooltip.set_visible(True)
            
                        fig.canvas.draw_idle()
                else:
                    tooltip.set_visible(False)
            
            def clear_annotations():
                for annotation in annotations:
                    annotation.remove()
                annotations.clear()
                fig.canvas.draw_idle()

            
            clear_annotation_button = ttk.Button(
                frame_top,
                bootstyle='success-outline',
                text="Clear Annotation",
                padding=(30, 5, 30, 5),
                takefocus=False,
                command=clear_annotations
            )
            clear_annotation_button.grid(row=3, column=3, padx=(10, 0), pady=(10, 5), sticky="w")
            
            fig.canvas.mpl_connect("button_press_event", on_click)

            canvas = FigureCanvasTkAgg(fig, master=frame_bottom)
            canvas.draw()
            canvas.get_tk_widget().pack(ipadx=35, ipady=43)
            plot_canvases.append(canvas)

            global combined_plot_toolbar
            combined_plot_toolbar = NavigationToolbar2Tk(canvas)
            combined_plot_toolbar.update()
            combined_plot_toolbar.pack_forget()
        

            homButton = ttk.Button(frame_top, bootstyle='success-outline', text= 'Home', padding= (30,5,30,5), takefocus= False, command=reset_home)
            homButton.grid(row=3, column=2, pady=(10, 5), sticky="w")


            panButton = ttk.Button(frame_top, bootstyle='success-outline', text= 'Pan', padding= (30,5,30,5), takefocus= False, command=lambda: combined_plot_toolbar.pan())
            panButton.grid(row=3, column=3, padx=(0, 10), pady=(10, 5), sticky="e")

            ZomButton = ttk.Button(frame_top, bootstyle='success-outline', text= 'Zoom', padding= (30,5,30,5), takefocus= False, command=lambda: combined_plot_toolbar.zoom())
            ZomButton.grid(row=3, column=4,padx=(10, 0), pady=(10, 5), sticky="w")

            savButton = ttk.Button(frame_top, bootstyle='success-outline', text= '  Save  ', padding= (30,5,30,5), takefocus= False, command=lambda: combined_plot_toolbar.save_figure())
            savButton.grid(row=3, column=4, padx=(0, 10), pady=(10, 5), sticky="e")


        except Exception as ex:
            logging.error("Error creating combined plot: %s", ex)
            messagebox.showerror("Error", f"An error occurred while drawing the plot: {ex}")
    
    # Draw the plot and pass the frame_bottom to the function
    drawCombinedPlot(dateTime, hotMetal, crudeSt, salebleSt, 
                 ['Hot Metal', 'Crude Steel', 'Saleable Steel'], frame_bottom)


    exitButton = ttk.Button(frame_top, bootstyle='danger', text= '  Exit  ', padding= (35,5,35,5), takefocus= False, command=close_app)
    exitButton.grid(row=1, column=4, padx=(0, 10), pady=(10, 5), sticky="e")

    refButton = ttk.Button(frame_top, bootstyle='success', text= 'Refresh', padding= (30,5,30,5), takefocus= False)
    refButton.grid(row=2, column=4, padx=(0, 10), pady=(10, 5), sticky="e")

    subButton = ttk.Button(frame_top, bootstyle='success-outline', text= 'Submit', padding= (30,5,30,5), takefocus= False, command=submit)
    subButton.grid(row=3, column=0, padx=(200, 0), pady=(10, 5))

    homButton = ttk.Button(frame_top, bootstyle='success-outline', text= 'Home', padding= (30,5,30,5), takefocus= False, command=lambda: (combined_plot_toolbar.home()))
    homButton.grid(row=3, column=2, pady=(10, 5), sticky="w")

    panButton = ttk.Button(frame_top, bootstyle='success-outline', text= 'Pan', padding= (30,5,30,5), takefocus= False, command=lambda: combined_plot_toolbar.pan())
    panButton.grid(row=3, column=3, padx=(0, 10), pady=(10, 5), sticky="e")

    ZomButton = ttk.Button(frame_top, bootstyle='success-outline', text= 'Zoom', padding= (30,5,30,5), takefocus= False, command=lambda: combined_plot_toolbar.zoom())
    ZomButton.grid(row=3, column=4,padx=(10, 0), pady=(10, 5), sticky="w")

    savButton = ttk.Button(frame_top, bootstyle='success-outline', text= '  Save  ', padding= (30,5,30,5), takefocus= False, command=lambda: combined_plot_toolbar.save_figure())
    savButton.grid(row=3, column=4, padx=(0, 10), pady=(10, 5), sticky="e")
    return app
    

# Run the application
if __name__ == "__main__":
    app = create_responsive_ui()
    app.mainloop()
