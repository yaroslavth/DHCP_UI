from flask import Flask, render_template
import datetime

app = Flask(__name__)

def parse_leases_file(leases_file):
    lease_records = {}
    current_lease = {}

    for line in leases_file:
        line = line.strip()

        if line.startswith('lease'):
            parts = line.split(' ')
            current_lease['ip_address'] = parts[1]
        elif line.startswith('starts'):
            timestamp_str = line.split(' ')[2] + ' ' + line.split(' ')[3].rstrip(';')
            current_lease['starts'] = datetime.datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S')
        elif line.startswith('ends'):
            timestamp_str = line.split(' ')[2] + ' ' + line.split(' ')[3].rstrip(';')
            current_lease['ends'] = datetime.datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S')
        elif line.startswith('hardware'):
            current_lease['hardware'] = line.split(' ')[2].rstrip(';')
        elif line.startswith('}'):
            ip_address = current_lease['ip_address']
            if ip_address in lease_records:
                lease_records[ip_address].append(current_lease)
            else:
                lease_records[ip_address] = [current_lease]
            current_lease = {}

    return lease_records

def lease_is_active(lease_rec, timestamp_now):
    return lease_rec['starts'] <= lease_rec['ends'] <= timestamp_now

@app.route('/')
def index():
    leases_file = open('dhcpd.leases', 'r')
    leases_db = parse_leases_file(leases_file)
    leases_file.close()

    active_leases = []
    timestamp_now = datetime.datetime.now()

    for ip_address in leases_db:
        lease_recs = leases_db[ip_address]

        for lease_rec in lease_recs:
            if lease_is_active(lease_rec, timestamp_now):
                try:
                    active_leases.append((lease_rec['starts'], lease_rec['ends'], lease_rec['hardware'], lease_rec['ip_address']))
                except:
                    print(lease_rec)


    active_leases.sort()

    return render_template('index.html', active_leases=active_leases)

if __name__ == '__main__':
    app.run(debug=True)