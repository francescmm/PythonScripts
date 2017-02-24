from urllib.request import urlopen
import datetime
import sys, getopt, re
import base64
import os

# Gets the content of a webpage or web resource
def getWebsource(url, encoding):
   response = urlopen(url)
   pageSource = ""
   
   if (len(encoding) > 0):
      pageSource = str(response.read(), encoding)
   else:
      pageSource = str(response.read())

   return pageSource

# Gets the substring between to patterns
def getSubstring(begin, end, text):
   startIndex = text.find(begin)
   endIndex = text.find(end)
   return (text[startIndex + len(begin):endIndex])

#Gets all the images from the XML stream to check if anyone copied it
def getAllImagesFromXml(xmlStream, date):
   print ("Getting all the images from the BOPI...\n")

   startText = "<tns:imagen>data:image/jpg;base64,"
   endText = "</tns:imagen>"
   startIndex = xmlStream.find(startText)
   endIndex = xmlStream.find(endText)
   imgIndex = 0

   while (startIndex is not -1 or endIndex is not -1):
      imgSrc = xmlStream[startIndex + len(startText):endIndex]
      xmlStream = xmlStream[startIndex + len(startText) + len(imgSrc) + len(endText):]
      
      imgdata = base64.b64decode(imgSrc)
      filename = "images\\" + date + "\\img_" + str(imgIndex) + ".jpg"

      os.makedirs(os.path.dirname(filename), exist_ok = True)
      with open(filename, 'wb') as f:
         f.write(imgdata)
         
      imgIndex += 1
      startIndex = xmlStream.find(startText)
      endIndex = xmlStream.find(endText)


# Returns any of the strings we set are in today's BOPI. Otherwise it returns false.
# If today there isn't BOPI, it informs about that.
def isTextInTodaysBOPI(strings, date):
   print ("====================== START ======================")
   print ("Accessing to the OEPM to get the BOPI of %s...\n" % date)
   
   day = 0
   
   if (len(date) != 0):
      repeat = True;
      day = datetime.datetime.strptime(date, '%d-%m-%Y').weekday()
   else:
      day = datetime.datetime.now().weekday()
         
   if day >= 0 and day < 5:
      if len(date) == 0:
         date = datetime.datetime.now().strftime('%d-%m-%Y')
        
      url = "https://sede.oepm.gob.es/bopiweb/descargaPublicaciones/resultBusqueda.action?fecha=" + date
      pageSource = getWebsource(url, 'utf-8')

      # We look for the MARCAS section
      print ("Looking for the document ID...\n")
      textSlot = getSubstring("TOMO 1", "TOMO 2", pageSource)
      
      # Checking that the file we're looking for is in XML format
      textSlot = getSubstring("en formato PDF", "en formato XML')", textSlot)

      # Finally, we get the UCM id to download the document
      print ("Getting the UCM id...\n")
      textSlot = getSubstring("cargaForm('", "','xml')", textSlot)

      # Download the BOPI of the day and we check that the document contains the text we want to look for
      url = "https://sede.oepm.gob.es/bopiweb/DescargaDocumento?idUcm=" + textSlot + "&docTipo=xml"

      print ("Getting the XML file from the server...\n")
      
      findText = getWebsource(url, '')
      
      found = False
      
      for f in strings:
         if findText.find(str(f).upper()) != -1 or findText.find(str(f).lower()) != -1:
            found = True
            print (f, " found")
         else:
            print (f, " not found")
            
      print ("Saving the XML file in local filesystem...\n")
      
      filename = "bopi\\bopi_" + date + ".xml"
      os.makedirs(os.path.dirname(filename), exist_ok = True)
      
      with open(filename, 'w') as f:
         f.write(findText)
         
      getAllImagesFromXml(findText, date)
   else:
      print ("There is no BOPI.")
      
   print("======================= END =======================\n\n\n")

def main(argv):
   startDate = ''
   words = []
   allFrom = False
   try:
      opts, args = getopt.getopt(argv,"hd:rw:",["date=","words=","recursive"])
   except getopt.GetoptError:
      print ('bopi-checker.py -d <startDate format dd-MM-yyyy> -w <words separated by comma>')
      sys.exit(2)
      
   for opt, arg in opts:
      if opt == '-h':
         print ('bopi-checker.py -d <startDate format dd-MM-yyyy> -w <words separated by comma>')
         sys.exit()
      elif opt in ("-d", "--date"):
         match = re.search(r'(\b\d{1,2}[-/:]\d{1,2}[-/:]\d{4}\b)', arg)
         if match is not None and (datetime.datetime.strptime(arg, '%d-%m-%Y') <= datetime.datetime.now()):
            startDate = arg
         else:
            print ('\nThe date must be valid and equal or lower than today.')
            sys.exit()
      elif opt in ("-w", "--words"):
         words = arg.split(",")
      elif opt in ("-r", "--recursive"):
         allFrom = True;
   
   if len(words) == 0:
      print ('\nThere is nothing to search. Please set some words separated by commas.')
      sys.exit()

   repeat = len(startDate) != 0
   userDate = datetime.datetime.strptime(startDate, '%d-%m-%Y')
   
   while userDate < datetime.datetime.now():
      startDate = datetime.datetime.strftime(userDate, '%d-%m-%Y')
      isTextInTodaysBOPI(words, startDate)
      
      if allFrom:
         userDate += datetime.timedelta(days = 1)
      else:
         userDate = datetime.datetime.now()

if __name__ == "__main__":
   main(sys.argv[1:])

