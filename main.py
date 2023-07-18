import requests
import json

from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/input', methods = ["GET","POST"])
def input():
    if request.method == "POST":
        input_city = request.form["c"]
        input_format = request.form["f"]
        return redirect(url_for("weather_now", cty=input_city, fo=input_format))
    else:
        return render_template('input.html')

# To get the response in webpage use this endpoint --->
@app.route('/<cty>/<fo>', methods=['GET','POST'])
def weather_now(cty, fo):
    # url of the weather website for API call
    url = 'https://weatherapi-com.p.rapidapi.com/current.json'
    city_string = {"q": cty}

    headers = {
        "X-RapidAPI-Key": "18e66b3f10msh0dc95898897194cp108e33jsn5a73e17b89a7",
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=city_string)
    # collecting all the weather and location related information in python dict
    json_dict = {
                "Weather": str(response.json()["current"]["temp_c"]) + " C",
                "Latitude": str(response.json()["location"]["lat"]),
                "Longitude": str(response.json()["location"]["lon"]),
                "City": response.json()['location']['name'] + ", " + response.json()['location']['country']
            }
    if fo == "json":
        return render_template("output.html", y=json_dict)
    if fo == "xml":
        xml_format = dicttoxml(json_dict, attr_type=False)
        y = parseString(xml_format).toprettyxml(indent='', newl="", encoding="UTF-8")
        return render_template("output.html", y=y)


# To enter the input in json format using Postman, use this end point -->
@app.route('/getCurrentWeather', methods=['POST'])
# Post request should be in {"city":"name", "output_format":"json or xml"}
# function which will send json or xml response as given in request json
def weather():
    # Getting the body of data posted by POST method
    data = request.get_json()
    # Getting the city name from 'data' variable
    city = data['city']
    # Getting the output format from 'data' variable
    output_format = data['output_format']

    if request.method == 'POST':
        # url of the weather website for API call
        url = 'https://weatherapi-com.p.rapidapi.com/current.json'
        querystring = {"q": city, "output_format": output_format}
        format_string = [{list(querystring.keys())[i]: list(querystring.values())[i]} for i in range(2)]
        city_string = format_string[0]

        headers = {
            "X-RapidAPI-Key": "18e66b3f10msh0dc95898897194cp108e33jsn5a73e17b89a7",
            "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=city_string)
        # collecting all the weather and location related information in python dict

        # try except to catch the error in json (wrong key and wrong value)
        try:
            json_dict = {
                "Weather": str(response.json()["current"]["temp_c"]) + " C",
                "Latitude": str(response.json()["location"]["lat"]),
                "Longitude": str(response.json()["location"]["lon"]),
                "City": response.json()['location']['name'] + ", " + response.json()['location']['country']
            }
        except (ValueError, KeyError, TypeError):
            # Not valid information, bail out and return an error
            return 'Wrong JSON format Passed'

        # output in json format
        if list(querystring.values())[1] == "json":
            return json_dict

        # output in xml format
        if list(querystring.values())[1] == "xml":
            xml_format = dicttoxml(json_dict, attr_type=False)
            return parseString(xml_format).toprettyxml(indent='', newl="", encoding="UTF-8")


if __name__ == "__main__":
    app.run(debug=True, port=8000)
