
user="sam"
host="api.stratako.lytiko.com"

# Empty the current source directory on the server
ssh $user@$host "rm -r ~/$host/source/* >& /dev/null"

# Send git tracked files
rsync -vr . --exclude-from='.gitignore' --exclude='.git' $user@$host:~/$host/source

# Copy secrets
scp core/secrets.py $user@$host:~/$host/source/core/secrets.py

# Turn off debug on server
ssh $user@$host "sed -i s/\"DEBUG = True\"/\"DEBUG = False\"/g ~/$host/source/core/settings.py"

# Add allowed host
ssh $user@$host "sed -i s/\"HOSTS = \[\]\"/\"HOSTS = \['$host'\]\"/g ~/$host/source/core/settings.py"

# Switch database
ssh $user@$host "sed -i s/\"DATABASES = local\"/\"DATABASES = live\"/g ~/$host/source/core/secrets.py"

# Apply migrations
ssh $user@$host "~/$host/env/bin/python ~/$host/source/manage.py migrate"

# Install pip packages
ssh $user@$host "~/$host/env/bin/pip install psycopg2-binary"
ssh $user@$host "~/$host/env/bin/pip install -r ~/$host/source/requirements.txt"
