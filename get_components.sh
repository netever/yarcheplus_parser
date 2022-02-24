sudo apt install openjdk-8-jre
sudo apt install firefox chromium-browser
wget https://chromedriver.storage.googleapis.com/76.0.3809.68/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/chromedriver
sudo chown root:root /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver
tar -xvzf geckodriver_linux64.tar.gz
sudo mv geckodriver /usr/local/bin/geckodriver
sudo chown root:root /usr/local/bin/geckodriver
sudo chmod +x /usr/local/bin/geckodriver
wget https://selenium-release.storage.googleapis.com/3.141/selenium-server-standalone-3.141.59.jar
java -jar selenium-server-standalone-3.141.59.jar
sudo apt install xvfb libxi6 libgconf-2-4
xvfb-run java -jar selenium-server-standalone-3.141.59.jar
sudo mv selenium-server-standalone-3.141.59.jar /usr/local/bin/
sudo useradd -d /tmp/ selenium
