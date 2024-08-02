from math import ceil

def organaizer(arr:list, page:int, page_size = 3, line_size = 2):

    ar_len = len(arr)
    start_ix = page*line_size * page_size
    if ar_len < start_ix + 1:  return [[],]
    page_remain = ceil(ceil(ar_len/line_size)%3)
    line_remain = ceil(ar_len%line_size)
    


    result = [ [arr[start_ix + i*line_size + j] for j in range(0, line_size if (ar_len - (start_ix + i*line_size)) >= line_size else line_remain)] 
              for i in range(0, page_size if ceil(ar_len/line_size) - start_ix//line_size >= page_size else page_remain)]

    return result