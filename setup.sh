#!/bin/bash
# Download necessary packages
echo "Installing necessary packages..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy python3-spidev python3-gpiozero python3-flask python3-gunicorn
echo "Packages installed."

# Define file names
QUOTES_FILE="quotes.json"
CURRENT_QUOTE_FILE="current_quote.json"

# Create quotes.json if it doesn't exist
if [ ! -f "$QUOTES_FILE" ]; then
    echo "[]" > "$QUOTES_FILE"
    echo "FILE $QUOTES_FILE created."
else
    echo "FILE $QUOTES_FILE already exists."
fi

# Create current_quote.json if it doesn't exist
if [ ! -f "$CURRENT_QUOTE_FILE" ]; then
    echo "{}" > "$CURRENT_QUOTE_FILE"
    echo "FILE $CURRENT_QUOTE_FILE created."
else
    echo "FILE $CURRENT_QUOTE_FILE already exists."
fi

# Change ownership to desired user
sudo chown pi:pi "$QUOTES_FILE" "$CURRENT_QUOTE_FILE" # Change 'pi:pi' to your desired user and group
sudo chmod 644 "$QUOTES_FILE" "$CURRENT_QUOTE_FILE" # Set permissions to read and write for owner, allows others to read
echo "File permissions set."
echo "File setup completed."

# Setup Cron Jobs
echo "Setting up cron jobs"
(crontab -l 2>/dev/null | grep -v "quotey.py"; echo "0 0 * * * python3 /home/pi/Quotey/quotey.py") | crontab -
echo "Cron job added to update quote daily at midnight."

(crontab -l 2>/dev/null | grep -v "gunicorn"; echo "@reboot cd /home/pi/Quotey && python3 -m gunicorn --bind 0.0.0.0:5000 api:app &") | crontab -
echo "Cron job added to start API server on reboot."

# Start API server
echo "Starting API server now..."
cd /home/pi/Quotey
python3 -m gunicorn --bind 0.0.0.0:5000 api:app --daemon
echo "API server started."

echo "Setup complete. Time to add quotes! To display first quote, populate quotes.json then run quotey.py."