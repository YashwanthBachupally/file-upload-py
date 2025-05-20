# file-upload-py
<p>
---------------------------------------------------------------------
  Debian-based systems (like Ubuntu) now restrict system-wide pip installations to avoid breaking system-managed Python packages.

✅ Recommended Fix: Use a Virtual Environment
This is the safest and cleanest way to install Flask and other packages:

1. Install python3-venv (if not already installed)
<code>
sudo apt update
sudo apt install python3-venv
</code>

3. Create a Virtual Environment

python3 -m venv venv

4. Activate the Virtual Environment

source venv/bin/activate


You’ll now see (venv) in your terminal prompt.

4. Install Flask Inside the Virtual Environment

pip install flask

5. Run Your Flask App
   sudo python3 app.py


  ----------------------------------------------------------------
  <br>
  Edit app.py and change:
app.run(host='0.0.0.0', port=80)


to:
app.run(host='0.0.0.0', port=5000)


Run the app without sudo:

venv/bin/python app.py

Access it via:
http://<your-ec2-public-ip>:5000

Option 2: Allow Port 80 Without sudo (Advanced)
If you really want to use port 80 without sudo, you can use a tool like setcap:


Then run:


⚠️ This is more advanced and not al
</p>
