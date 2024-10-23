from flask import Flask, jsonify
import psycopg2
import requests
from groq import Groq

app = Flask(__name__)

# Database connection 
DB_NAME = "weather"
DB_USER = "postgres"
DB_PASS = "1608@HRt"
DB_HOST = "localhost"
DB_PORT = "5432"

API_KEY = "QRcS8mMo2+PAmjj0mNAhWQ==N6CfqoAQQ9IAxmLj"

GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

def fetch_country_data(country_name):
    try:
        api_url = f"https://api.api-ninjas.com/v1/country?name={country_name}"
        headers = {'X-Api-Key': API_KEY}
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data:
                country_data = {
                    'name': data[0]['name'],
                    'gdp': data[0].get('gdp', 0),
                    'population': data[0]['population'],
                    'literacy_rate': data[0].get('literacy', 0),
                    'currency': data[0]['currency']['code'],
                    'surface_area': data[0].get('surface_area', 0)
                }
                return country_data
            else:
                print("No data found for the country.")
                return None
        else:
            print(f"Error fetching data: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

def store_country_data(country_data):
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO country_details (name, gdp, population, literacy_rate, currency, surface_area)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (
            country_data['name'],
            country_data['gdp'],
            country_data['population'],
            country_data['literacy_rate'],
            country_data['currency'],
            country_data['surface_area']
        ))
        connection.commit()
        print("Data stored successfully")
    except Exception as error:
        print("Error while storing data:", error)

def generate_summary(data):
    prompt = f"You are expert in giving summary , Summarize the country data in a detailed paragraph and for different country start the paragraph from a new line also remove symbols only give text: {data}."
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        summary = completion.choices[0].message.content 
        return summary


    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Unable to generate summary"

@app.route('/fetch-country/<string:country_name>', methods=['GET'])
def fetch_and_store_country(country_name):
    country_data = fetch_country_data(country_name)
    if country_data:
        store_country_data(country_data)
        return jsonify({'message': f"Data for {country_name} fetched and stored successfully.", 'data': country_data}), 200
    else:
        return jsonify({'error': 'Failed to fetch country data'}), 500


@app.route('/countries', methods=['GET'])
def get_countries_summary():
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        query = "SELECT name, gdp, population, literacy_rate, currency, surface_area FROM country_details;"
        cursor.execute(query)
        rows = cursor.fetchall()

        result = []
        for row in rows:
            country_data = {
                'name': row[0],
                'gdp': row[1],
                'population': row[2],
                'literacy_rate': row[3],
                'currency': row[4],
                'surface_area': row[5]
            }
            result.append(country_data)

        cursor.close()
        connection.close()
        return jsonify(result)

    except Exception as error:
        print("Error while fetching data:", error)
        return jsonify({'error': 'Unable to fetch data'}), 500



@app.route('/generate-summary', methods=['GET'])
def generate_summary_route():
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        query = "SELECT name, gdp, population, literacy_rate, currency, surface_area FROM country_details;"
        cursor.execute(query)
        rows = cursor.fetchall()

        summary_data = []
        for row in rows:
            country_data = {
                'name': row[0],
                'gdp': row[1],
                'population': row[2],
                'literacy_rate': row[3],
                'currency': row[4],
                'surface_area': row[5]
            }
            summary_data.append(country_data)

        cursor.close()
        connection.close()

        if summary_data:
            summary = generate_summary(summary_data)
            return jsonify({'summary': summary}), 200
        else:
            return jsonify({'message': 'No data available for summarization.'}), 404

    except Exception as error:
        print("Error while generating summary:", error)
        return jsonify({'error': 'Unable to generate summary'}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)



























































