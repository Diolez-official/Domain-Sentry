from flask import Flask, render_template, request, jsonify
import socket
import requests

app = Flask(__name__)  # Changed from ip_app to app

def get_comprehensive_ip_info(domain):
    try:
        # Rest of your get_comprehensive_ip_info function remains the same
        ip_address = socket.gethostbyname(domain)
        
        apis = [
            f'https://ipapi.co/{ip_address}/json/',
            f'https://ipwhois.app/json/{ip_address}',
            f'https://ip-api.com/json/{ip_address}'
        ]
        
        full_info = {
            'ip': ip_address,
            'location': 'Unknown',
            'provider': 'Unknown',
            'status': 'Unknown',
            'continent': 'Unknown',
            'country': 'Unknown',
            'region': 'Unknown',
            'city': 'Unknown',
            'latitude': 0,
            'longitude': 0
        }
        
        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=5).json()
                
                if 'org' in response:
                    full_info['provider'] = response.get('org', 'Unknown')
                
                if 'country' in response:
                    full_info['country'] = response.get('country', 'Unknown')
                    full_info['continent'] = response.get('continent', 'Unknown')
                
                if 'regionName' in response:
                    full_info['region'] = response.get('regionName', 'Unknown')
                    full_info['city'] = response.get('city', 'Unknown')
                    full_info['latitude'] = response.get('lat', 0)
                    full_info['longitude'] = response.get('lon', 0)
                
            except Exception:
                continue
        
        try:
            socket.create_connection((domain, 80), timeout=5)
            full_info['status'] = 'Active'
        except:
            full_info['status'] = 'Offline'
        
        location_parts = [
            part for part in [
                full_info['city'], 
                full_info['region'], 
                full_info['country'], 
                full_info['continent']
            ] if part != 'Unknown'
        ]
        full_info['location'] = ', '.join(location_parts) or 'Unknown'
        
        return full_info
    
    except Exception as e:
        return {
            'ip': 'Error',
            'location': 'Unable to lookup',
            'provider': 'N/A',
            'status': 'Error'
        }

@app.route('/')  # Changed from ip_app to app
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])  # Changed from ip_app to app
def lookup_domain():
    data = request.json
    domain = data.get('domain', '')
    result = get_comprehensive_ip_info(domain)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)  # Removed port specification
