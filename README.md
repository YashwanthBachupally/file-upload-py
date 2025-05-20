# file-upload-py
<p>
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
