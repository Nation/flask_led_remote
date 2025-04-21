from flask import Flask, render_template, request
import serial
import serial.tools.list_ports
import time

app = Flask(__name__)

# Global variable to store the serial connection
ser = None

def find_arduino():
    """Try to find the Arduino port"""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(f"Found port: {p.device} - {p.description}")
        if "Arduino" in p.description or "CH340" in p.description or "USB Serial" in p.description:
            print(f"Selected Arduino port: {p.device}")
            return p.device
    return None

def connect_to_arduino():
    """Establish connection to Arduino"""
    global ser
    
    try:
        # Close any existing connection
        if ser is not None and ser.is_open:
            ser.close()
            print("Closed existing connection")
            
        # Find Arduino port
        port = find_arduino()
        if not port:
            print("Arduino not found!")
            return False
            
        # Connect to Arduino
        ser = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        print(f"Connected to Arduino on {port}")
        return True
        
    except Exception as e:
        print(f"Error connecting to Arduino: {e}")
        return False

def send_command(command):
    """Send command to Arduino"""
    global ser
    
    # Try to connect if not connected
    if ser is None or not ser.is_open:
        if not connect_to_arduino():
            return "Connection failed"
    
    try:
        # Send command
        ser.write(f"{command}\n".encode())
        print(f"Sent command: {command}")
        
        # Read response (if any)
        time.sleep(0.1)
        if ser.in_waiting:
            response = ser.readline().decode('utf-8').strip()
            print(f"Arduino response: {response}")
            return response
        return "Command sent (no response)"
        
    except Exception as e:
        print(f"Error sending command: {e}")
        ser = None  # Reset connection
        return f"Error: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    
    # Handle button presses
    if request.method == 'POST':
        command = request.form.get('command')
        if command in ['on1', 'off1', 'on2', 'off2', 'on3', 'off3']:
            result = send_command(command)
            message = f"Command '{command}' result: {result}"
        else:
            message = "Invalid command"
    
    # For the first visit, try to establish connection
    if request.method == 'GET' and (ser is None or not ser.is_open):
        if connect_to_arduino():
            message = "Connected to Arduino"
        else:
            message = "Could not connect to Arduino"
    
    return render_template('index.html', message=message)

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True)
