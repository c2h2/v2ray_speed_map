import sys
import json
import unicodedata

def count_characters(s):
    return sum(2 if unicodedata.east_asian_width(ch) in ('W', 'F') else 1 for ch in s)

def east_asian_char_width(char):
    """Returns the width of an East Asian character."""
    if unicodedata.east_asian_width(char) in ('F', 'W'):
        return 2
    else:
        return 1

def custom_ljust(s, width):
    """Left-justifies a string in a field of given width, treating East Asian width characters as double width."""
    needed_padding = width - sum(east_asian_char_width(char) for char in s)
    return s + ' ' * needed_padding

def create_ascii_table(dict_list):
    # Check if the list is empty
    if not dict_list:
        return "No data provided."

    # Extract headers from the first dictionary
    headers = list(dict_list[0].keys())

    # Calculate column widths
    col_widths = {header: count_characters(header) for header in headers}
    for d in dict_list:
        for header, value in d.items():
            col_widths[header] = max(col_widths[header], count_characters(str(value)))
    
    # Build the top border
    top_border = '+' + '+'.join(['-' * (col_widths[header] + 2) for header in headers]) + '+'

    # Build the header row
    header_row = '| ' + ' | '.join(custom_ljust(header, col_widths[header]) for header in headers) + ' |'

    # Build the separator
    separator = '+' + '+'.join(['-' * (col_widths[header] + 2) for header in headers]) + '+'

    # Build the data rows
    data_rows = []
    for d in dict_list:
        row = '| ' + ' | '.join(custom_ljust(str(d[header]), col_widths[header]) for header in headers) + ' |'
        data_rows.append(row)

    # Build the bottom border
    bottom_border = top_border

    # Combine all parts
    table = [top_border, header_row, separator] + data_rows + [bottom_border]
    return '\n'.join(table)

#open argv file and test
if __name__ == "__main__":
    content = json.loads(open(sys.argv[1]).read())

    def print_ascii_table(list_of_dicts):
        new_list = []
        for l in content:
            new_list.append(l.copy())
            new_list[-1]["speed_mbps"] = round(new_list[-1]["speed_mbps"], 2)
            del new_list[-1]["airport"]
        print(create_ascii_table(new_list))

    print_ascii_table(content)
        
    
    
    


