# Export requests as a python script

Exports requests from burp proxy as a python script. 

# Installation

1.	Download Burp Suite : http://portswigger.net/burp/download.html
2.	Download Jython standalone JAR: http://www.jython.org/downloads.html
3.	Open burp -> Extender -> Options -> Python Environment -> Select File -> Choose the Jython standalone JAR
4.	Download the extension.
5.	Open Burp -> Extender -> Extensions -> Add -> Choose the export.py file.

# Usage

After installation, a new option will be added to proxy context menu - "Export as script".

# Demo

![Demo](https://raw.githubusercontent.com/ngo/burp-export-as-script/master/sample.gif)

# TODO:

* Special treatment for session cookies
* Automatic derivation of data dependencies between requests (a-la burp's macro editor)
* Customization of code templates, other languages, multithreading, bruteforce etc.a
* ...
