'''
mini-seerver to test files loading
'''

# from pprint import pprint, pformat
from flask import Flask, render_template, send_from_directory, send_file, json
from flask_cors import CORS

app = Flask(__name__, template_folder='')
CORS(app)

@app.route("/", methods=['GET'])
def serveIndex():  
  print("\n... serveIndex > render index ...")
  return render_template( "index.html" )

@app.route("/content/<path:folder_path>/<string:filename>", methods=['GET'])
def serveHtml(folder_path, filename):  
  print("\n... serveHtml > folder_path : ", folder_path)
  print("serveHtml > filename : ", filename)
  return render_template( folder_path + '/' + filename )

@app.route('/statics/<path:folder_path>/<string:filename>')
def sendStatic(folder_path, filename):
  print("\n... sendStatic > folder_path : ", folder_path)
  print("sendStatic > filename : ", filename)
  return send_from_directory(folder_path, filename)

# @app.route('/images/<path:folder_path>/<string:filename>')
# def sendImage(folder_path, filename):
#   print("folder_path : ", folder_path)
#   print("filename : ", filename)
#   return send_from_directory(folder_path, filename)

# run the application
if __name__ == "__main__":  
  app.run(debug=True, host='localhost', port=8800)
