# -*- coding: utf-8 -*-
# brdr.py

""" 
    @author: Christopher Pickering
    
    Report used to email a listing of what components caused a longer
    than standard lead time to be quoted to customers.
    
"""

from functions import *

def main(reportName):

    #initialize workbook
    my_workbook = Workbook(reportName)

    # create worksheets
    my_path = my_workbook.build_workbook()

    # create database connection
    me = Database()
    me.oracle_connect()

    # run report sql statement
    cur = me.run_url(str(Path(__file__).parents[0].joinpath('sql','brdr-BRDR.sql')))

    header = ["Item", "Description","EAU", "Planner", "Buyer", "Order Type", "Days Late"]
    html = "<table border=\"1px solid black\" align=\"center\" cellpadding=\"3\"><tr style=\"background-color:  #b3b3b3\">"     
    
    
    for i in header:
        if i ==1:
            html = html + "<td width = \"100\" style=\"white-space: nowrap;\' width=\"10%\"><b>" + i + "</b></td>"
        else:
            html = html + "<td width = \"100\" style=\"white-space: nowrap; max-width: 200px;\"><b>" + i + "</b></td>"
    
    html += "</tr><tr style=\" background-color:#e6ccb3;align:center\">"
  
    for i in cur:
        for n in range(len(header)):
            if n == 0 and i == 0:
                html = html + "<td style=\"white-space: nowrap; max-width: 200px;\">" + str(i[n]) + "</td>"
                
            elif n == 0:
                html = html + "</tr><tr style=\" background-color:#e6ccb3;align:center;\"><td style=\"white-space: nowrap; max-width: 200px;\">" + str(i[n]) + "</td>"
            
            elif n == 1:
                    html = html + "<td style=\"white-space: nowrap;\" width=\"10%\">"+ str(i[n])[:30] + "</td>"
            else:
                html = html + "<td style=\"white-space: nowrap; max-width: 200px;\">"+ str(i[n]) + "</td>"
                    
    html += "</tr></table>"  

    # close database connection
    me.close()

    # send report
    Email(reportName, html).SendMail()

if __name__ == '__main__':
    reportName = "BRDR"

    try:
        main(reportName)
    except BaseException as e:
        print(str(e))
        Email(reportName + ' error', "<br><center>" + str(e) + "</center>").SendMail()
        pass