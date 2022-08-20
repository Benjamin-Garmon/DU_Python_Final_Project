"""
Name: Ben Garmon
Date: 08/19/2022
Week 10: Stocks Portfolio
Objective: Create a GUI for stocks
"""

# Import packages
import yfinance as yf
from tkinter import *
import tkinter.messagebox
from matplotlib import pyplot as plt

# Adds symbol to the tkinter listbox
def AddTicker():
    symbol = ticker_entry_box.get().upper()  # capitalize the ticker symbols
    if symbol not in tickers_list and len(symbol) > 0:
        tickers_list.append(symbol)
        ticker_listbox.insert(tkinter.END, symbol)
        ticker_entry_box.delete(0, tkinter.END)  # deletes the text entry box
    else:
        ticker_entry_box.delete(0, tkinter.END)  # keeps from having duplicates in listbox


# Deletes symbol from the listbox
def DeleteTicker():
    try:
        ticker_index = ticker_listbox.curselection()[0]
        ticker_listbox.delete(ticker_index)
        tickers_list.remove(tickers_list[ticker_index])
    except:
        # if the button click fails. don't do anything
        pass


# Fetch the data
def UpdateData():
    error_list = []  # This is a list of entered tickers that fail to download / don't exist
    for ticker in tickers_list:
        if ticker not in tickers_dict:
            print(f'Downloading {ticker} data')
            ticker_data = yf.download(ticker, period='5y')  # gets the last 5 years of pricing
            if not ticker_data.empty:
                tickers_dict[ticker] = ticker_data
            else:
                error_list.append(ticker)

    if len(error_list) > 0:
        error_label.config(text=f'{error_list} \n is not valid')  # shows what symbols failed to download
    else:
        error_label.config(text='')  # this will clear the label if everything passes

    ShowGraph(tickers_dict, tickers_list)  # Function that creates the graph


def ShowGraph(stock_dict, symbol_list):
    # clear graph as to avoid multiples
    plt.clf()

    # loop through the tickers and pull the dataframe from the dictionary and plot to graph
    for stock in symbol_list:
        try:
            df = stock_dict.get(stock)
            plt.plot(df.index, df['Close'], label=stock)  # yfinance has dates set as the indexing
        except:
            print(f'{stock}: Check stock ticker symbol')  # a double check for a failed download

    # rotate x-axis values 35 deg for readability and labels for the graph
    plt.style.use('classic')
    plt.xticks(rotation='35')
    plt.title('Closing Price of Stocks')
    plt.xlabel('Dates')
    plt.ylabel('Price Per Share (USD)')
    plt.legend(loc='upper left')
    plt.show()


def ReportWindow():

    new_window = Toplevel(root)
    new_window.title('Stock Grade Report')

    try:
        # Loop for errors and dict creation in case you don't create a graph
        error_list = []
        for ticker in tickers_list:
            if ticker not in tickers_dict:
                print(f'Downloading {ticker} data')
                ticker_data = yf.download(ticker, period='5y')
                if not ticker_data.empty:
                    tickers_dict[ticker] = ticker_data

                    # print the latest grade of the stock if it's not in the dictionary
                    sym_label = Label(new_window, text=f'\n {ticker}')
                    sym_label.pack()

                    # Parsing out grade recommendation info to make it more readable
                    rec_label = Label(new_window, text=((
                                                            str(yf.Ticker(ticker).recommendations.iloc[-1][:2])[:-24])
                                                            .replace('Name', 'Date'))
                                                            .replace('To Grade', 'Grade:'))
                    rec_label.pack()

                else:
                    error_list.append(ticker)
            else:
                # print the latest grade of the stock if it is in the dictionary
                sym_label = Label(new_window, text=f'\n {ticker}')
                sym_label.pack()

                # Parsing out grade recommendation info to make it more readable
                rec_label = Label(new_window, text=((
                                                        str(yf.Ticker(ticker).recommendations.iloc[-1][:2])[:-24])
                                                        .replace('Name', 'Date'))
                                                        .replace('To Grade', 'Grade:'))
                rec_label.pack()

        if len(error_list) > 0:
            error_label.config(text=f'{error_list} \n is not valid')
        else:
            error_label.config(text='')

    except:
        error_label.config(text=f'Issue with pulling data\nCheck ticker symbol')
        print('Issue with pulling data\nCheck ticker symbol')



    # Save ticker price history to csv button
    save_ticker_data_button = Button(new_window, text='Export Stocks History', command=ToCSV, bg='gray')
    save_ticker_data_button.pack(side=BOTTOM)


# Send downloaded chart data to csv
def ToCSV():
    try:
        for ticker in tickers_list:
            if ticker in tickers_dict:
                tickers_dict.get(ticker).to_csv(f'{ticker}.csv')
                print(f'{ticker} 5 year history saved to {ticker}.csv')
    except:
        pass  # do nothing for a failed button click


########################### Main Program ###########################

# create root tkinter GUI frame
root = Tk()

root.title('Create Stock Comparison Graph')

# Define the ticker list for listbox
tickers_list = []

# Serves to keep from downloading the same data when you change the graph
tickers_dict = {}


# Frames for list and  buttons
# separate frame in same window for the listbox
frame_tickers = tkinter.Frame(root)
frame_tickers.pack(side=LEFT)

frame_buttons = tkinter.Frame(root)
frame_buttons.pack(side=RIGHT)


# Plotting boxes and buttons to GUI to organize the style
# instructions label
instruction_label = Label(frame_buttons, text='Enter a Ticker Symbol', font=10)
instruction_label.pack(side=TOP)

# create input box for ticker symbols
ticker_entry_box = Entry(frame_buttons, width=7)
ticker_entry_box.pack(side=TOP)

# Create label for ticker box
ticker_listbox_label = Label(frame_tickers, text='Stocks', font=14)
ticker_listbox_label.pack(side=TOP)

# a third frame for just the symbols and scrollbar, so they are the same size
frame_tickers_box = tkinter.Frame(frame_tickers)
frame_tickers_box.pack()


# Create listbox of ticker symbols
ticker_listbox = tkinter.Listbox(frame_tickers_box, height=7, width=7)
scrollbar = tkinter.Scrollbar(frame_tickers_box)
scrollbar.pack(side=tkinter.LEFT, fill=tkinter.Y)
scrollbar.config(command=ticker_listbox.yview)
ticker_listbox.pack()

# Create label for errors
error_label = Label(frame_tickers)
error_label.pack(side=BOTTOM)



# Buttons
# Add Stock to graph, Under the text entry box
add_ticker_button = Button(frame_buttons, text='Add Stock', command=AddTicker)
add_ticker_button.pack(side=TOP)

# Delete stock from graph, Under the list of stocks box
del_ticker_button = Button(frame_tickers, text='Delete Stock', command=DeleteTicker)
del_ticker_button.pack(side=tkinter.BOTTOM)

# Update Graph after adding or deleting stocks, Under graph
update_ticker_button = Button(frame_buttons, text='Update Graph', command=UpdateData)
update_ticker_button.pack(side=TOP)

# Open new window with stock reports
generate_report_button = Button(frame_buttons, text='Generate Report', command=ReportWindow)
generate_report_button.pack(side=BOTTOM)


# run the tkinter GUI
root.mainloop()
