#!/usr/bin/env python3
from flask import Flask , request, jsonify, redirect, url_for, send_from_directory
from dbConnector import DbConnector, InvalidPubMethodError
import json
from bokeh.layouts import gridplot
from bokeh.plotting import figure, save,show, output_file
import numpy as np
import datetime
import time
import os

api = Flask(__name__, static_url_path='')
log = None

@api.route('/ean', methods=['PUT'])
def getEan():
    dbConn = DbConnector('wurst.db')
    attr = json.loads(request.data.decode())
    try:
        ean = dbConn.getEan(attr['volume'],attr['method'])
        ret = {'ean':ean}
    except InvalidPubMethodError as e:
        ret = {'error':e.message}
    dbConn.close()
    return json.dumps(ret)

@api.route('/code', methods=['PUT'])
def getCode():
    dbConn = DbConnector('wurst.db')
    attr = json.loads(request.data.decode())
    try:
        code = dbConn.getCode(attr['volume'],attr['method'])
        ret = {'code':code}
    except InvalidPubMethodError as e:
        ret = {'error':e.message}
    dbConn.close()
    return json.dumps(ret)

@api.route('/code/<code>', methods=['GET'])
def useCode(code):
    dbConn = DbConnector('wurst.db')
    valid = dbConn.useCode(code)
    dbConn.close()
    return json.dumps({'valid':valid})

@api.route('/check/<code>', methods=['GET'])
def checkCode(code):
    dbConn = DbConnector('wurst.db')
    valid = dbConn.checkCode(code)
    dbConn.close()
    return json.dumps({'valid':valid})

@api.route('/stats/open', methods=['GET'])
def statsOpen():
    dbConn = DbConnector('wurst.db')
    opens = dbConn.getStatOpen()
    dbConn.close()
    return json.dumps(opens)

@api.route('/stats/graphs', methods=['GET'])
def statsGraphs():
    dbConn = DbConnector('wurst.db')
    opens = dbConn.getStatOpen()
    dbConn.close()
    usedNum = []
    usedDate = []
    genNum = []
    genDate = []

    for date,use in sorted(opens['used'], key=lambda tup: tup[0]):
        if(len(usedNum)>0):
            usedNum.append(usedNum[-1]+use)
        else:
            usedNum.append(use)
        usedDate.append(datetime.datetime.fromtimestamp(date))
    for date,gen in sorted(opens['generated'], key=lambda tup: tup[0]):
        if(len(genNum)>0):
            genNum.append(genNum[-1]+gen)
        else:
            genNum.append(gen)
        genDate.append(datetime.datetime.fromtimestamp(date))
    # output to static HTML file
    root_dir = os.path.dirname(os.getcwd())

    output_file(os.path.join(root_dir, 'tmp',"lines.html"))

    # create a new plot with a title and axis labels
    p = figure(title="Wurst Down Chart", x_axis_label='Date', y_axis_label='',x_axis_type="datetime",plot_width=1000, plot_height=600)
    
    p.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    p.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    p.yaxis.visible = False

    # add a line renderer with legend and line thickness
    p.line(usedDate, usedNum, legend="used Wurstchers", line_width=2,color='#be1e3c')
    p.line(genDate, genNum, legend="generated Wurstchers", line_width=2,color='#66b4d3')
    p.line(usedDate, list(600 - np.asarray(usedNum)), legend="Wurst Reserve", line_width=2,color='#e16d00')
    p.legend.location = "top_left"

    # show the results
    save(p)
    time.sleep(0.1)
    return send_from_directory(os.path.join(root_dir, 'tmp'), 'lines.html')
@api.route('/stats/graphsspecialinternal', methods=['GET'])
def statsGraphsspecialinternal():
    dbConn = DbConnector('wurst.db')
    opens = dbConn.getStatOpen()
    dbConn.close()
    usedNum = []
    usedDate = []
    genNum = []
    genDate = []

    for date,use in sorted(opens['used'], key=lambda tup: tup[0]):
        if(len(usedNum)>0):
            usedNum.append(usedNum[-1]+use*10)
        else:
            usedNum.append(use*10)
        usedDate.append(datetime.datetime.fromtimestamp(date))
    for date,gen in sorted(opens['generated'], key=lambda tup: tup[0]):
        if(len(genNum)>0):
            genNum.append(genNum[-1]+gen*10)

        else:
            genNum.append(gen*10)
        genDate.append(datetime.datetime.fromtimestamp(date))
    # output to static HTML file
    root_dir = os.path.dirname(os.getcwd())

    output_file(os.path.join(root_dir, 'tmp',"lines_int.html"))

    # create a new plot with a title and axis labels
    p = figure(title="simple line example", x_axis_label='Date', y_axis_label='',x_axis_type="datetime",plot_width=1000, plot_height=600)
    

    # add a line renderer with legend and line thickness
    p.line(usedDate, usedNum, legend="used", line_width=2,color='#be1e3c')
    p.line(genDate, genNum, legend="generated", line_width=2,color='#66b4d3')
    p.line(usedDate, list(6000 - np.asarray(usedNum)), legend="wurstdown", line_width=2,color='#e16d00')
    p.legend.location = "top_left"

    # show the results
    save(p)
    time.sleep(0.1)
    return send_from_directory(os.path.join(root_dir, 'tmp'), 'lines_int.html')



@api.route('/method/<method>', methods=['post','put','delete'])
def methodStuff(method):
    dbConn = DbConnector('wurst.db')
    if request.method == 'PUT': 
        dbConn.addPubMethod(method)
        return ''
    if request.method == 'POST': 
        dbConn.enablePubMethod(method)
        return ''
    if request.method == 'DELETE':
        dbConn.blackList(method)
        return ''

    dbConn.close()


if __name__ == '__main__':
    api.run(host='0.0.0.0', port=5000,debug=False)
