import xlrd
import xlwt
import xlutils
import os
import pandas
import dataframes

def file_diff(f_old, f_new, output_dir=None, eps=0.0001):
    if output_dir is None:
       output_dir = os.path.dirname(f_old)
    xls_old = pandas.ExcelFile(f_old)
    # sheets = xls_old.sheet_names
    xls_new = pandas.ExcelFile(f_new)

    missing_sheetnames = set(xls_old.sheet_names) - set(xls_new.sheet_names)
    added_sheetnames = set(xls_new.sheet_names) - set(xls_old.sheet_names)

    for sheetn in set(xls_new.sheet_names) & set(xls_old.sheet_names):
        # parse with  : , na_values=['NA'] ?
        added, reldiff, missing = dataframes.df_diff(xls_old.parse(sheetn), xls_new.parse(sheetn), eps=0.0001)

    if added is not None or missing is not None or reldiff is not None:
        os.mkdir(output_dir+'/'+f_old)

    if added is not None:
    writer = ExcelWriter('output.xlsx')
>>> df1.to_excel(writer,'Sheet1')
>>> df2.to_excel(writer,'Sheet2')
>>> writer.save()