from flask import Flask, render_template, request, jsonify
import socket
import requests

ip_app = Flask(__name__)

def get_comprehensive_ip_info(domain):
    try:
        # Resolve IP
        ip_address = socket.gethostbyname(domain)
        
        # Multiple API calls for comprehensive info
        apis = [
            f'https://ipapi.co/{ip_address}/json/',
            f'https://ipwhois.app/json/{ip_address}',
            f'https://ip-api.com/json/{ip_address}'
        ]
        
        # Aggregate information
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
        
        # Try multiple APIs to get comprehensive data
        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=5).json()
                
                # ipapi.co
                if 'org' in response:
                    full_info['provider'] = response.get('org', 'Unknown')
                
                # ipwhois.app
                if 'country' in response:
                    full_info['country'] = response.get('country', 'Unknown')
                    full_info['continent'] = response.get('continent', 'Unknown')
                
                # ip-api.com
                if 'regionName' in response:
                    full_info['region'] = response.get('regionName', 'Unknown')
                    full_info['city'] = response.get('city', 'Unknown')
                    full_info['latitude'] = response.get('lat', 0)
                    full_info['longitude'] = response.get('lon', 0)
                
            except Exception:
                continue
        
        # Check domain status
        try:
            socket.create_connection((domain, 80), timeout=5)
            full_info['status'] = 'Active'
        except:
            full_info['status'] = 'Offline'
        
        # Construct location string
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

@ip_app.route('/')
def index():
    return render_template('index.html')

@ip_app.route('/lookup', methods=['POST'])
def lookup_domain():
    data = request.json
    domain = data.get('domain', '')
    result = get_comprehensive_ip_info(domain)
    return jsonify(result)

if __name__ == '__main__':
    ip_app.run(debug=True, port=5001)