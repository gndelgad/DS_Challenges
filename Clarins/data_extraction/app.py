from flask import Flask, render_template, request, make_response
import xml.etree.ElementTree as et
from xml.dom import minidom
import requests

ACCESS_KEY = 'db91a917d3c326fd12a78b8b992cbd74'

app = Flask(__name__, template_folder='templates')


def dictToXml(tag, d):
    '''
    Turn a simple dict of key/value pairs into XML
    '''
    elem = et.Element(tag)
    for key, val in d.items():
        child = et.Element(key)
        child.text = str(val)
        elem.append(child)
    return elem


def addWeather(city, date):
    """
    Call the Weatherstack to obtain the average temperature on a given city and day.
    """
    params = {
        'access_key': ACCESS_KEY,
        'query': city,
        'historical_date' : date
    }
    api_result = requests.get('http://api.weatherstack.com/current', params)
    api_response = api_result.json()
    return api_response['current']
    

@app.route('/')
def uploadFile():
    return render_template('index.html')


@app.route('/uploader', methods = ['POST'])
def transformFile():
    
	tree = et.parse(request.files['file'])
	root = tree.getroot()
	
	for order in root.findall('order'):
		order_number = order.get('order-no')
		date = order.find('order-date').text[:10]
		city = order.find('customer').find('billing-address').find('city').text
    
		weather = dictToXml('weather', addWeather(city, date))
		order.append(weather)
        
	response = make_response(minidom.parseString(et.tostring(root)).toprettyxml(indent='\t', newl='\n')) 
	response.headers["Content-Disposition"] = "attachment; filename=result.xml" 
	return response


if __name__ == '__main__':
    
    app.run(host='127.0.0.1', port=8080, debug = True)