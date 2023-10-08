import csv
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd

patron_list = None
tier_list = {}  # Key: name, Value: Dict{'count', 'checkbox_var', 'checkbox_widget', 'minpledge_var', 'minpledge_widget', 'minpledge_curlabel'}


def key_order(text: str):
    """This function handles alphabetical sorting. Any special rules or character replacements go here."""
    # Any characters inside the brackets will be ignored when sorting. Separate with commas and enclose in quotes.
    chars_to_ignore = ['~', "'", " "]

    # Any characters that should be treated as a different character go here.
    # This is for sorting purposes only and will not change the final output.
    chars_to_replace = [('à', 'a'), ('é', 'e'), ('ì', 'i'), ('ò', 'o'), ('ù', 'u')]

    to_return = []
    for char in text:
        char_to_append = char.lower()
        if char_to_append in chars_to_ignore:
            continue
        for pair in chars_to_replace:
            if char_to_append == pair[0]:
                char_to_append = pair[1]
        to_return.append(char_to_append)
    return to_return


def key_alpha_order(item: str):
    """Helper function that calls key_order() for simple alphabetical sorting."""
    return key_order(item[0])


def key_pledge_order(item: (str, float)):
    """Helper function that calls key_order() to sort by pledge amounts first, and alphabetically second."""
    pledge_str = format((1000000 - item[1]), '.2f')     # Subtract from a large value to ensure highest to lowest sort, and convert to a string with exactly two decimal places.
    pledge_str = pledge_str.zfill(10)                   # Add leading zeros to conform all values to the same string length.
    return key_order(pledge_str + item[0])


def generate_list():
    """Produces the final list with all checked tiers, and displays it in the textbox"""
    text = ""
    if separation_var.get() == 'mix':
        # If mix tiers is selected, create a list of all checked tiers and process them all at once.
        tiers = []
        for key in tier_list.keys():
            if tier_list[key]['checkbox_var'].get() == 1:
                tiers.append(key)
        text = process_tier(tiers, patron_list)[0]
    else:
        current_list = list(patron_list)
        for key in tier_list.keys():
            if tier_list[key]['checkbox_var'].get() == 1:
                result = process_tier([key], current_list)
                text += '----------------------------------------\n'
                text += key
                text += '\n----------------------------------------\n'
                text += result[0]
                text += "\n\n"
                current_list = result[1]    # Prepare for the next tier by replacing the list of patrons with the returned list of unprocessed patrons.
    textbox.config(state='normal')
    textbox.delete("1.0", END)
    textbox.insert(END, text)


def process_tier(tiers: list, patrons: list) -> (str, list):
    """Returns a text list of patrons of the specified tier according to the user's selected options, and a list of the
    remaining unprocessed patrons."""
    processed_list = []
    remaining_patrons = []

    for patron in patrons:
        name_found = False

        # If Patreon ever changes their CSV headers, this section will need updating.
        status = patron["Patron Status"]
        patron_name = patron["Name"]
        patron_email = patron["Email"]
        pledge = float(patron["Pledge Amount"])
        frequency = patron["Charge Frequency"]
        listed_tier = patron["Tier"]

        # Skip name if not active
        if status != "Active patron":
            continue

        # Convert annual pledges to the monthly amount.
        if frequency == "annual":
            pledge = round((pledge / 12), 2)

        if categorize_var.get() == 'listed':
            if listed_tier in tiers:
                name_found = True
        elif categorize_var.get() == 'amount':
            for tier in tiers:
                if pledge >= tier_list[tier]['minpledge_var'].get():
                    name_found = True

        if not name_found:
            remaining_patrons.append(patron)
            continue

        # If name is blank, either skip it or replace with email address.
        if len(patron_name) == 0:
            if replace_var.get() == 'full':
                name_to_add = patron_email
            elif replace_var.get() == 'partial':
                for i in range(0, len(patron_email)):
                    if patron_email[i] == "@":
                        modified_email = patron_email[:i]
                        print("EMAIL: " + patron_email + " changed to " + modified_email)
                        name_to_add = modified_email
                        break
            else:
                continue
        else:
            name_to_add = patron_name

        processed_list.append((name_to_add, pledge))

    if sort_var.get() == 'alpha':
        sorted_list = sorted(processed_list, key=key_alpha_order)
    else:
        sorted_list = sorted(processed_list, key=key_pledge_order)

    sorted_list_simplified = []
    for item in sorted_list:
        sorted_list_simplified.append(item[0])
    sorted_list = sorted_list_simplified

    columns = []
    for i in range(columns_var.get()):
        columns.append([])
    counter = 0
    for name in sorted_list:
        columns[counter % columns_var.get()].append(name)
        counter += 1

    # Add blank lines to separate each column.
    output = ""
    for i in range(len(columns)):
        if columns_var.get() > 1:
            output += '-----COLUMN ' + str(i) + '-----\n\n'
        for name in columns[i]:
            output += (name + "\n")
        output += "\n\n"

    return output, remaining_patrons


def toggle_child_widgets(parent, mode):
    for child in parent.winfo_children():
        child_type = child.winfo_class()
        if child_type in ('TFrame', 'TLabelFrame'):
            toggle_child_widgets(child, mode)
        elif child_type not in ('TSeparator', 'Treeview'):
            try:
                child.config(state=mode)
            except:
                print('Invalid mode for toggle_child_widgets')


def show_amounts():
    """Adds widgets to allow entry of each tier's pledge amount"""
    row_count = 1
    for key in tier_list.keys():

        new_var = IntVar()
        new_var.set(1)
        tier_list[key]['checkbox_var'] = new_var

        new_button = ttk.Checkbutton(frame_tiers, text=key + ' (' + str(tier_list[key]['count']) + ')', variable=new_var)
        new_button.grid(column=1, row=row_count, padx=10, sticky='W')
        tier_list[key]['checkbox_widget'] = new_button

        new_amount = IntVar()
        new_amount.set(0)
        tier_list[key]['minpledge_var'] = new_amount

        new_currency_label = ttk.Label(frame_tiers, text='$')
        new_currency_label.grid(column=2, row=row_count, sticky='E')
        tier_list[key]['minpledge_curlabel'] = new_currency_label
        new_amount_widget = ttk.Spinbox(frame_tiers, from_=0, to=9999, textvariable=new_amount)
        new_amount_widget.grid(column=3, row=row_count, sticky='E')
        tier_list[key]['minpledge_widget'] = new_amount_widget

        row_count += 1

def hide_amounts():
    """Removes the pledge amount widgets"""
    for key in tier_list.keys():
        tier_list[key]['minpledge_widget'].grid_remove()
        tier_list[key]['minpledge_curlabel'].grid_remove()


def open_file():
    """Opens a CSV file, converts its contents to a dictionary, and sets up the rest of the interface."""

    filetypes = [('CSV files', '*.csv')]
    filename = fd.askopenfilename(filetypes=filetypes)

    try:
        with open(filename, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            global patron_list
            patron_list = list(reader)
    except FileNotFoundError:
        return

    if len(frame_tiers.winfo_children()) > 1:
        for child in frame_tiers.winfo_children():
            child.grid_remove()
    ttk.Label(frame_tiers, text="Name").grid(column=1, row=0)
    ttk.Label(frame_tiers, text="Minimum Required Pledge").grid(column=3, row=0)

    tier_list.clear()
    for patron in patron_list:
        tier = patron['Tier']
        if tier == '':
            tier = "(no tier listed)"
        if tier not in tier_list.keys():
            tier_list[tier] = {}
            tier_list[tier]['count'] = 0
        else:
            tier_list[tier]['count'] += 1

    # Create the list of tiers and their associated checkboxes.
    row_count = 1
    for key in tier_list.keys():

        new_var = IntVar()
        new_var.set(1)
        tier_list[key]['checkbox_var'] = new_var

        new_button = ttk.Checkbutton(frame_tiers, text=key + ' (' + str(tier_list[key]['count']) + ')', variable=new_var)
        new_button.grid(column=1, row=row_count, padx=10, sticky='W')
        tier_list[key]['checkbox_widget'] = new_button

        row_count += 1
    if categorize_var.get() == 'amount':
        show_amounts()

    toggle_child_widgets(frame_options, 'enabled')

    generate_button.config(state='enabled')


def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append((textbox.get("1.0", END)))


# GUI SETUP
root = Tk()
root.title("Patreon CSV to List")

frame = ttk.Frame(root, padding=10)
frame.grid(column=0, row=0, sticky=(N,W,E,S))

load_button = ttk.Button(frame, text="Load CSV File", command=open_file)
load_button.grid(column=1, row=1)

frame_tiers = ttk.LabelFrame(frame, padding=10, text="Tier(s) To Include")
frame_tiers.grid(column=1, row=2, sticky=(N, S))

# OPTIONS
frame_options = ttk.LabelFrame(frame, padding=10, text="Output Options")
frame_options.grid(column=1, row=4)
frame_options['borderwidth'] = 2
frame_options['relief'] = 'solid'

# Separation Frame
separation_var = StringVar()
separation_var.set('mix')
frame_separation = ttk.Frame(frame_options, padding=10)
frame_separation.grid(row=1, sticky=(N,W,E,S))

rbutton_single = ttk.Radiobutton(frame_separation, text='Mix Tiers Together', variable=separation_var, value='mix')
rbutton_single.grid(column=1, row=1, padx=20)
rbutton_separate = ttk.Radiobutton(frame_separation, text='Keep Tiers Separated', variable=separation_var, value='separate')
rbutton_separate.grid(column=2, row=1, padx=20)

ttk.Separator(frame_options, orient='horizontal').grid(row=2, sticky=(N, S, E, W))

# Columns Frame
frame_columns = ttk.Frame(frame_options, padding=10)
frame_columns.grid(row=2, sticky=(N,W,E,S))
columns_var = IntVar()
columns_var.set(1)

label_columns = ttk.Label(frame_columns, text='Number of columns:')
label_columns.grid(column=1, row=1)
entry_columns = ttk.Spinbox(frame_columns, from_=1, to=99, textvariable=columns_var)
entry_columns.grid(column=2, row=1)

ttk.Separator(frame_options, orient='horizontal').grid(row=3, sticky=(N, S, E, W))

# Sorting method
frame_sort = ttk.Frame(frame_options, padding=10)
frame_sort.grid(row=3, sticky=(N,W,E,S) )

label_sort = ttk.Label(frame_sort, text='Sort patron list by:')
label_sort.grid(column=1, row=1, columnspan=2, sticky=(N, S, E, W))
sort_var = StringVar()
sort_var.set('alpha')
rbutton_sort_alpha = ttk.Radiobutton(frame_sort, text='Alphabetically', variable=sort_var, value='alpha')
rbutton_sort_alpha.grid(column=1, row=2, padx=20)
rbutton_sort_pledge = ttk.Radiobutton(frame_sort, text='By Pledge Amount', variable=sort_var, value='pledge')
rbutton_sort_pledge.grid(column=2, row=2, padx=20)

ttk.Separator(frame_options, orient='horizontal').grid(column=1, row=40, sticky=(N, S, E, W))

# Replace blank names
frame_replace = ttk.Frame(frame_options, padding=10)
frame_replace.grid(row=4)

label_sort = ttk.Label(frame_replace, text='Replace empty name fields with:')
label_sort.grid(column=1, row=1, columnspan=3, sticky=(N, S, E, W))
replace_var = StringVar()
replace_var.set('none')
rbutton_sort_alpha = ttk.Radiobutton(frame_replace, text='Nothing', variable=replace_var, value='none')
rbutton_sort_alpha.grid(column=1, row=42, padx=20)
rbutton_sort_pledge = ttk.Radiobutton(frame_replace, text='Full Email', variable=replace_var, value='full')
rbutton_sort_pledge.grid(column=2, row=42, padx=20)
rbutton_sort_pledge = ttk.Radiobutton(frame_replace, text='Partial Email', variable=replace_var, value='partial')
rbutton_sort_pledge.grid(column=3, row=42, padx=20)

# Categorize by pledge
frame_categorize = ttk.Frame(frame_options, padding=10)
frame_categorize.grid(row=5, sticky=(N, S, E, W))

label_categorize = ttk.Label(frame_categorize, text='Categorize patrons into tiers by:')
label_categorize.grid(column=1, row=1, columnspan=2, sticky=(N, S, E, W))
categorize_var = StringVar()
categorize_var.set('listed')
rbutton_sort_listed = ttk.Radiobutton(frame_categorize, text='Listed Tier', variable=categorize_var, value='listed', command=hide_amounts)
rbutton_sort_listed.grid(column=1, row=2, padx=20)
rbutton_sort_amount = ttk.Radiobutton(frame_categorize, text='Pledge Amount', variable=categorize_var, value='amount', command=show_amounts)
rbutton_sort_amount.grid(column=2, row=2, padx=20)

toggle_child_widgets(frame_options, 'disabled')

generate_button = ttk.Button(frame, text='Generate List', command=generate_list)
generate_button.grid(column=1, row=5)
generate_button.config(state='disabled')

textbox = Text(frame)
textbox.grid(column=1, row=6)
textbox.config(state='disabled')

copy_button = ttk.Button(frame, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.grid(column=1, row=7)


root.mainloop()
