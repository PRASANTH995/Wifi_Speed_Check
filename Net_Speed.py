import psutil
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import time

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Network Monitor"

# Layout of the dashboard
app.layout = html.Div(children=[
    html.H1("Network Monitoring Dashboard", style={'textAlign': 'center', 'color': '#4CAF50'}),
    
    html.Div(children=[
        html.P("Upload Speed: ", id='upload-speed', style={'color': '#2196F3'}),
        html.P("Download Speed: ", id='download-speed', style={'color': '#E91E63'}),
        html.P("Total Data Sent: ", id='total-sent', style={'color': '#FF9800'}),
        html.P("Total Data Received: ", id='total-received', style={'color': '#9C27B0'}),
        html.P("Active Connections: ", id='active-connections', style={'color': '#673AB7'}),
    ], style={'textAlign': 'center', 'fontSize': 18}),
    
    dcc.Graph(id='network-graph'),
    dcc.Interval(id='interval', interval=1000, n_intervals=0)
])

# Store network data
time_series = []
upload_speed_series = []
download_speed_series = []
prev_sent = psutil.net_io_counters().bytes_sent
prev_recv = psutil.net_io_counters().bytes_recv

@app.callback(
    [
        Output('upload-speed', 'children'),
        Output('download-speed', 'children'),
        Output('total-sent', 'children'),
        Output('total-received', 'children'),
        Output('active-connections', 'children'),
        Output('network-graph', 'figure')
    ],
    Input('interval', 'n_intervals')
)
def update_network_stats(n):
    global prev_sent, prev_recv
    counters = psutil.net_io_counters()
    
    # Calculate speed
    upload_speed = (counters.bytes_sent - prev_sent) / 1024  # KB/s
    download_speed = (counters.bytes_recv - prev_recv) / 1024  # KB/s
    
    # Update previous values
    prev_sent, prev_recv = counters.bytes_sent, counters.bytes_recv
    
    active_connections = len(psutil.net_connections())
    
    # Append new data
    time_series.append(time.time())
    upload_speed_series.append(upload_speed)
    download_speed_series.append(download_speed)
    
    # Keep only the last 60 seconds of data to keep the graph readable
    if len(time_series) > 60:
        time_series.pop(0)
        upload_speed_series.pop(0)
        download_speed_series.pop(0)
    
    # Create the graph
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=time_series, y=upload_speed_series, mode='lines', name='Upload Speed (KB/s)', line=dict(color='#2196F3')))
    figure.add_trace(go.Scatter(x=time_series, y=download_speed_series, mode='lines', name='Download Speed (KB/s)', line=dict(color='#E91E63')))
    figure.update_layout(title='Real-Time Network Speed', xaxis_title='Time', yaxis_title='Speed (KB/s)', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='#f5f5f5')
    
    return (
        f"Upload Speed: {upload_speed:.2f} KB/s",
        f"Download Speed: {download_speed:.2f} KB/s",
        f"Total Data Sent: {counters.bytes_sent / (1024*1024):.2f} MB",
        f"Total Data Received: {counters.bytes_recv / (1024*1024):.2f} MB",
        f"Active Connections: {active_connections}",
        figure
    )

# Fixed the syntax error here
if __name__ == '__main__':
    app.run(debug=True)